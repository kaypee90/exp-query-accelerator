import json
from urllib.parse import parse_qs
from http_code import HTTP_200_OK, HTTP_400_BAD_REQUEST


async def process_response(status_code, response, send):
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


async def handle_post(send, receive):
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    data = parse_qs(body.decode())
    name = data.get("name", [""])[0]
    description = data.get("description", [""])[0]

    response = {
        "name": name,
        "description": description,
    }

    await process_response(HTTP_200_OK, response, send)


async def handle_invalid_request(send):
    response = {"message": "Request must be a POST"}

    await process_response(HTTP_400_BAD_REQUEST, response, send)
