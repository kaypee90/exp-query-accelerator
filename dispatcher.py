import json
import time
from cache import Cache

from utils.logging import create_logger
from utils.config import DB_TYPE, CONNECTION_STRING, databases

logger = create_logger(__name__)


async def dispatch(request):
    """
    Query dispatcher, checks if query response is cached
    if not available in cache, query db and cache the response
    """
    start_time = time.time()

    data = Cache.get(request)
    error = None

    if not data:
        logger.info("Couldn't find data in cache, retrieving from db")
        database_type = databases[DB_TYPE]
        db = database_type(CONNECTION_STRING)
        request_payload = json.loads(request)

        # TODO: Validate request payload
        error, data = await db.query(**request_payload)

        if not error and data:
            logger.info("Caching request retrieved from db")
            Cache.set(request, data)

    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000  
    logger.info(f"Dispatching processed in {duration_ms:.2f} milliseconds")  

    return error, data
