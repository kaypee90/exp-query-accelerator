# Author kaypee90

# TTL
# Separate Query Cache and Item Cache
# Based on async await
# Handle concurrency
# Monitoring tool eg. Displaying Service health

#  ==============================================

import json
from urllib.parse import parse_qs

async def app(scope, receive, send):
    assert scope['type'] == 'http'

    if scope['method'] == 'GET':
        response = {
            'message': 'Hello, World!'
        }
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps(response).encode('utf-8'),
        })

    elif scope['method'] == 'POST':
        body = b''
        more_body = True
        while more_body:
            message = await receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)
        
        data = parse_qs(body.decode())
        name = data.get('name', [''])[0]
        description = data.get('description', [''])[0]
        
        response = {
            'name': name,
            'description': description,
        }

        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                (b'content-type', b'application/json'),
            ]
        })
        await send({
            'type': 'http.response.body',
            'body': json.dumps(response).encode('utf-8'),
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8081, log_level="info")
