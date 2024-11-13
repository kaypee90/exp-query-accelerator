"""
Author kaypee90

TTL
Use single cache for` Query Cache and Item Cache
Based on async await
Handle concurrency
Monitoring tool eg. Displaying Service health
Use official db async driver
Microseconds latency

==============================================
"""

import uvicorn
from src.handlers import handle_invalid_request, handle_post, handle_get


async def app(scope, receive, send):
    assert scope["type"] == "http"

    if scope["method"] == "POST":
        await handle_post(send, receive)
    elif scope["method"] == "GET":
        await handle_get(send)
    else:
        await handle_invalid_request(send, "Request must be a POST")


if __name__ == "__main__":
    try:
        uvicorn.run("app:app", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("Shut down in progress...")
