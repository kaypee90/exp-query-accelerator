from db.base import BaseDatabaseWrapper

from utils.logging import create_logger

logger = create_logger(__name__)


class Postgres(BaseDatabaseWrapper):
    def __init__(self, connection_string):
        super().__init__(connection_string)

    async def query(self, **kwargs):
        """
        Query postgres db base
        kwargs: table, fields, filters
        """
        pass
