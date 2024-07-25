import json
from cache import Cache

from utils.logging import create_logger
from utils.config import DB_TYPE, CONNECTION_STRING, databases

logger = create_logger(__name__)


async def dispatch(request):
    """
    Query dispatcher, checks if query response is cached
    if not avalable query db and cache query response
    """
    data = Cache.get(request)
    error = None

    if not data:
        logger.info("Couldb't find data in cache, retrieveing from db")
        database_type = databases[DB_TYPE]
        db = database_type(CONNECTION_STRING)
        request_payload = json.loads(request)
        error, data = await db.query(**request_payload)

        if not error and data:
            logger.info("Caching request retrieved from db")
            Cache.set(request, data)

    return error, data
