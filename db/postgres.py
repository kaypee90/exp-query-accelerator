from psycopg.errors import UndefinedColumn, UndefinedTable
from psycopg_pool import AsyncConnectionPool
from db.base import BaseDatabaseWrapper
from db.query_builder import build_sql_query

from utils.logging import create_logger

logger = create_logger(__name__)


class Postgres(BaseDatabaseWrapper):
    def __init__(self, connection_string):
        super().__init__(connection_string)

    async def query(self, **kwargs):
        """
        Query postgres db base
        kwargs: table, fields, filters
        https://www.psycopg.org/psycopg3/docs/advanced/pool.html
        https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool
        """
        try:
            query = self._generate_query(**kwargs)
            # Create an asynchronous connection pool
            async with AsyncConnectionPool(self.connection_string, min_size=1, max_size=4) as pool:
                async with pool.connection() as connection:
                    async with connection.cursor() as cursor:
                        await cursor.execute(query)
                        rows = await cursor.fetchall()
                        
                        return None, rows
        except (TypeError, UndefinedTable, UndefinedColumn) as e:
            error = f"Error: {e}"
            logger.error(error)
            return error, None


    def _generate_query(self, table, fields=None, filters=None):
        """
        Converts request payload to postgres query
        """
        return build_sql_query(table, fields, filters)