import json
from cache import cache_request, get_cached_request
from db.sqlite import Sqlite

from config import CONNECTION_STRING


async def dispatch(request):
    # encode the request and check in cache
    # if not avalable query db
    # cache query response
    data = get_cached_request(request)

    if not data:
        # TODO: retrieve db class type based on connection type
        print("INFO: Couldb't find data in cache, retrieveing from db")
        db = Sqlite(CONNECTION_STRING)
        request_payload = json.loads(request)
        data = await db.query(**request_payload)

    if data:
        cache_request(request, data)

    return data
