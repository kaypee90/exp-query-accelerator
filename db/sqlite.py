from db.base import BaseDatabaseWrapper
import aiosqlite
import sqlite3

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

    def _generate_query(self, table, fields=None, filters=None):
        """
        Converts request payload to sqlite query
        """
        assert table, "Table name is required"

        selected_fields = "*"
        if fields:
            selected_fields = ", ".join(fields)

        query = f"SELECT {selected_fields} FROM {table}"

        if filters:
            filter_clause = " AND ".join(
                [f"{key} = '{value}'" for key, value in filters.items()]
            )
            query += f" WHERE {filter_clause}"

        return query
