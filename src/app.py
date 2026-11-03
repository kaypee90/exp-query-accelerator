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

from src.handlers import (
    handle_get,
    handle_lifespan,
    handle_method_not_allowed,
    handle_post,
)


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        await handle_lifespan(receive, send)
        return

    if scope["type"] != "http":
        return

    if scope["method"] == "POST":
        await handle_post(send, receive)
    elif scope["method"] == "GET":
        await handle_get(send)
    else:
        await handle_method_not_allowed(send)


if __name__ == "__main__":
    try:
        uvicorn.run("src.app:app", port=8000, log_level="info")
    except KeyboardInterrupt:
        print("Shut down in progress...")
