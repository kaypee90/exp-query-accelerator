import asyncio

from psycopg.errors import DataError, ProgrammingError
from psycopg_pool import AsyncConnectionPool

from src.db.base import BaseDatabaseWrapper


class Postgres(BaseDatabaseWrapper):
    """
    Postgres backend backed by a single connection pool that is opened on
    first use and reused for the lifetime of the instance.
    https://www.psycopg.org/psycopg3/docs/advanced/pool.html
    """

    placeholder = "%s"
    # ProgrammingError covers UndefinedTable, UndefinedColumn, syntax errors...
    client_errors = (ValueError, ProgrammingError, DataError)

    def __init__(self, connection_string, min_size=1, max_size=4, timeout=10.0):
        super().__init__(connection_string)
        self._min_size = min_size
        self._max_size = max_size
        # Seconds to wait for a connection before failing (psycopg default: 30)
        self._timeout = timeout
        self._pool = None
        self._pool_lock = asyncio.Lock()

    async def _get_pool(self):
        if self._pool is None:
            async with self._pool_lock:
                if self._pool is None:
                    pool = AsyncConnectionPool(
                        self.connection_string,
                        min_size=self._min_size,
                        max_size=self._max_size,
                        timeout=self._timeout,
                        open=False,
                    )
                    await pool.open()
                    self._pool = pool
        return self._pool

    async def _execute(self, sql, params):
        pool = await self._get_pool()
        async with pool.connection() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(sql, params)
                return await cursor.fetchall()

    async def close(self):
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
