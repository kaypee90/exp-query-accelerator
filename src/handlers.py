import json
from src.http_code import HTTP_200_OK, HTTP_400_BAD_REQUEST
from src.dispatcher import dispatch

from src.utils.logging import create_logger

logger = create_logger(__name__)


async def process_response(status_code, response, send):
    """
    Process response content for handlers
    """
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": json.dumps(response).encode("utf-8"),
        }
    )


async def handle_get(send):
    """
    Handler for health checks
    """
    logger.info("Health check succeeded")
    await process_response(HTTP_200_OK, {"status": "Healthy"}, send)


async def handle_post(send, receive):
    """
    Handler for fetching data
    """
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    if not body:
        await handle_invalid_request(send, "Request body cannot be empty")
        return

    error, data = await dispatch(body)

    if error:
        await handle_invalid_request(send, error)
        return

    response = {"data": data}
    await process_response(HTTP_200_OK, response, send)


async def handle_invalid_request(send, message):
    response = {"message": message}

    await process_response(HTTP_400_BAD_REQUEST, response, send)
