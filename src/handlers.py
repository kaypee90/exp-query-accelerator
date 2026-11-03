import base64
import datetime
import decimal
import json
import uuid

from src.dispatcher import close_database, dispatch
from src.http_code import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_413_CONTENT_TOO_LARGE,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from src.utils.logging import create_logger

logger = create_logger(__name__)

MAX_BODY_BYTES = 64 * 1024


class BodyTooLarge(Exception):
    pass


def _json_default(value):
    """Encodes common database column types that json cannot handle natively."""
    if isinstance(value, (datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, (decimal.Decimal, uuid.UUID)):
        return str(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return base64.b64encode(bytes(value)).decode("ascii")
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def encode_json(response):
    return json.dumps(response, default=_json_default, allow_nan=False).encode("utf-8")


async def process_response(status_code, response, send, headers=()):
    """
    Sends a JSON response. The body is encoded before anything is sent, so an
    encoding failure can still be answered with a proper error response.
    """
    body = encode_json(response)
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json"), *headers],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def handle_get(send):
    """
    Handler for health checks
    """
    logger.info("Health check succeeded")
    await process_response(HTTP_200_OK, {"status": "Healthy"}, send)


async def read_body(receive, max_bytes=MAX_BODY_BYTES):
    """
    Returns the request body, or None if the client disconnected.
    Raises BodyTooLarge when the body exceeds `max_bytes`.
    """
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        if message["type"] == "http.disconnect":
            return None
        body += message.get("body", b"")
        if len(body) > max_bytes:
            raise BodyTooLarge
        more_body = message.get("more_body", False)
    return body


async def handle_post(send, receive):
    """
    Handler for fetching data
    """
    try:
        body = await read_body(receive)
    except BodyTooLarge:
        await process_response(
            HTTP_413_CONTENT_TOO_LARGE,
            {"message": f"Request body cannot exceed {MAX_BODY_BYTES} bytes"},
            send,
        )
        return

    if body is None:
        logger.info("Client disconnected before sending the full request")
        return

    if not body:
        await handle_invalid_request(send, "Request body cannot be empty")
        return

    try:
        error, data = await dispatch(body)
        if error:
            await handle_invalid_request(send, error)
            return
        await process_response(HTTP_200_OK, {"data": data}, send)
    except Exception:
        logger.exception("Unexpected error while handling request")
        await process_response(
            HTTP_500_INTERNAL_SERVER_ERROR, {"message": "Internal server error"}, send
        )


async def handle_invalid_request(send, message):
    await process_response(HTTP_400_BAD_REQUEST, {"message": message}, send)


async def handle_method_not_allowed(send):
    await process_response(
        HTTP_405_METHOD_NOT_ALLOWED,
        {"message": "Method not allowed, use GET or POST"},
        send,
        headers=[(b"allow", b"GET, POST")],
    )


async def handle_lifespan(receive, send):
    """
    Handles ASGI lifespan events so the database pool is closed on shutdown.
    """
    while True:
        message = await receive()
        if message["type"] == "lifespan.startup":
            await send({"type": "lifespan.startup.complete"})
        elif message["type"] == "lifespan.shutdown":
            await close_database()
            await send({"type": "lifespan.shutdown.complete"})
            return
