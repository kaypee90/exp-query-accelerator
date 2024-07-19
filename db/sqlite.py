from base import BaseDatabaseWrapper
import aiosqlite

class Sqlite(BaseDatabaseWrapper):
    def __init__(self, db_path):
        super().__init__(db_path)

    async def query(self, **kwargs):
        """
        Query sqlite db base
        """
        # query filters
        # table
        # fields
        query = "SELECT * FROM some_table" # TODO: generate query from kwargs
        async with aiosqlite.connect(self.connection_string) as db:
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                # TODO: return rows