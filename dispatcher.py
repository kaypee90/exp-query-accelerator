import json
from cache import cache_request, get_cached_request
from db.sqlite import Sqlite

from utils.logging import create_logger
from utils.config import CONNECTION_STRING
logger = create_logger(__name__)


async def dispatch(request):
    """
    Query dispatcher, checks if query response is cached
    if not avalable query db cache query response
    """
    data = get_cached_request(request)

    if not data:
        # TODO: retrieve db class type based on connection type
        logger.info("Couldb't find data in cache, retrieveing from db")
        db = Sqlite(CONNECTION_STRING)
        request_payload = json.loads(request)
        data = await db.query(**request_payload)

        if data:
            logger.info("Caching request retrieved from db")
            cache_request(request, data)
        else:
            logger.info("No data found in db")

    return data
