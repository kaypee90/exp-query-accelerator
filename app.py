"""
Author kaypee90

TTL
Separate Query Cache and Item Cache
Based on async await
Handle concurrency
Monitoring tool eg. Displaying Service health
Use official db async driver

==============================================
"""

import uvicorn
from handlers import handle_invalid_request, handle_post


async def app(scope, receive, send):
    assert scope["type"] == "http"

    if scope["method"] == "POST":
        await handle_post(send, receive)

    else:
        await handle_invalid_request(send, "Request must be a POST")


if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, log_level="info")
