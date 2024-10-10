from db.base import BaseDatabaseWrapper
import aiosqlite
import sqlite3
from db.query_builder import build_sql_query

from utils.logging import create_logger

logger = create_logger(__name__)


class Sqlite(BaseDatabaseWrapper):
    def __init__(self, db_path):
        super().__init__(db_path)

    async def query(self, **kwargs):
        """
        Query sqlite db base
        kwargs: table, fields, filters
        """
        try:
            query = self._generate_query(**kwargs)

            async with aiosqlite.connect(self.connection_string) as db:
                async with db.execute(query) as cursor:
                    rows = await cursor.fetchall()
                    return None, rows
        except (TypeError, sqlite3.OperationalError) as e:
            error = f"Error: {e}"
            logger.error(error)
            return error, None

    def _generate_query(
        self, table, fields=None, filters=None, order_by=None, order_dir=None
    ):
        """
        Converts request payload to sqlite query
        """
        return build_sql_query(
            table,
            fields=fields,
            filters=filters,
            order_by=order_by,
            order_dir=order_dir,
        )
