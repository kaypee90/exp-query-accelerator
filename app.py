# Author kaypee90

# TTL
# Separate Query Cache and Item Cache
# Based on async await
# Handle concurrency
# Monitoring tool eg. Displaying Service health

#  ==============================================

import uvicorn
from handlers import handle_invalid_request, handle_post


async def app(scope, receive, send):
    assert scope["type"] == "http"

    if scope["method"] == "POST":
        await handle_post(send, receive)

    else:
        await handle_invalid_request(send)


if __name__ == "__main__":
    config = uvicorn.Config("app:app", port=8081, log_level="info")
    server = uvicorn.Server(config)
    server.run()
