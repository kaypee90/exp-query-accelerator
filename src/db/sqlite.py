import sqlite3

import aiosqlite

from src.db.base import BaseDatabaseWrapper

# OperationalError is also raised for server-side faults ("database is
# locked", "unable to open database file"); only these are the client's fault.
_CLIENT_ERROR_PREFIXES = ("no such table", "no such column", "near ")


class Sqlite(BaseDatabaseWrapper):
    client_errors = (ValueError, OverflowError, sqlite3.InterfaceError)

    async def _execute(self, sql, params):
        try:
            async with aiosqlite.connect(self.connection_string) as db:
                async with db.execute(sql, params) as cursor:
                    return await cursor.fetchall()
        except sqlite3.OperationalError as e:
            if str(e).startswith(_CLIENT_ERROR_PREFIXES):
                raise ValueError(str(e)) from e
            raise
