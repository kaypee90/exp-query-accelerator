import json
import time

from src.cache import Cache
from src.utils.config import DB_TYPE, databases
from src.utils.logging import create_logger
from src.validator import validate_payload

logger = create_logger(__name__)

_database = None


def get_database():
    """Returns the shared database backend, creating it on first use."""
    global _database
    if _database is None:
        config = databases[DB_TYPE]
        if not config["connection_string"]:
            raise RuntimeError(f"No connection settings configured for {DB_TYPE}")
        logger.info(f"Creating {config['module'].__name__} backend")
        _database = config["module"](config["connection_string"])
    return _database


async def close_database():
    """Closes the shared database backend, if one was created."""
    global _database
    if _database is not None:
        await _database.close()
        _database = None


def _cache_key(payload):
    # Canonical form so equivalent payloads share one cache entry.
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


async def dispatch(request):
    """
    Query dispatcher: validates the request, serves it from the cache when
    possible, otherwise queries the database and caches the result.

    Returns:
        tuple[str | None, list | None]: (error, data)
    """
    start_time = time.perf_counter()

    try:
        payload = json.loads(request)
    except (json.JSONDecodeError, UnicodeDecodeError, RecursionError):
        logger.error("Invalid JSON payload")
        return "Invalid JSON payload", None

    errors = validate_payload(payload)
    if errors:
        logger.error(f"Invalid payload: {', '.join(errors)}")
        return ", ".join(errors), None

    key = _cache_key(payload)
    data = Cache.get(key)
    error = None

    if data is None:
        logger.info("Cache miss, retrieving from db")
        error, data = await get_database().query(**payload)
        if error is None:
            Cache.set(key, data)
    else:
        logger.info("Cache hit")

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(f"Dispatching processed in {duration_ms:.2f} milliseconds")

    return error, data
