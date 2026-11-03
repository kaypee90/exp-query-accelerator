from abc import ABC, abstractmethod

from src.db.query_builder import build_sql_query
from src.utils.logging import create_logger

logger = create_logger(__name__)


class BaseDatabaseWrapper(ABC):
    """
    Common query flow for all backends: build a parameterized query, run it,
    and turn errors caused by the request (bad table, bad column, ...) into
    an error message. Any other error (e.g. connection failures) propagates.
    """

    placeholder = "?"
    client_errors = (ValueError,)

    def __init__(self, connection_string):
        self.connection_string = connection_string

    async def query(
        self, table, fields=None, filters=None, order_by=None, order_dir=None
    ):
        """
        Returns:
            tuple[str | None, list | None]: (error, rows)
        """
        try:
            sql, params = build_sql_query(
                table,
                fields=fields,
                filters=filters,
                order_by=order_by,
                order_dir=order_dir,
                placeholder=self.placeholder,
            )
            return None, await self._execute(sql, params)
        except self.client_errors as e:
            error = f"Error: {e}"
            logger.error(error)
            return error, None

    @abstractmethod
    async def _execute(self, sql, params):
        """Runs the query and returns all rows."""

    async def close(self):
        """Releases any resources held by the backend."""
