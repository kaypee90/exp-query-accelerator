import pytest

from src import dispatcher
from src.db.sqlite import Sqlite


def test_get_database_builds_backend_from_config(monkeypatch):
    monkeypatch.setattr(dispatcher, "DB_TYPE", "sqlite")
    monkeypatch.setitem(
        dispatcher.databases,
        "sqlite",
        {"module": Sqlite, "connection_string": "x.db"},
    )

    database = dispatcher.get_database()

    assert isinstance(database, Sqlite)
    assert database.connection_string == "x.db"
    assert dispatcher.get_database() is database


def test_get_database_without_connection_settings_fails_fast(monkeypatch):
    monkeypatch.setattr(dispatcher, "DB_TYPE", "sqlite")
    monkeypatch.setitem(
        dispatcher.databases, "sqlite", {"module": Sqlite, "connection_string": None}
    )

    with pytest.raises(RuntimeError):
        dispatcher.get_database()


@pytest.mark.asyncio
async def test_close_database_without_backend_is_a_no_op():
    await dispatcher.close_database()

    assert dispatcher._database is None
