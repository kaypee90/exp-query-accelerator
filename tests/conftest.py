import sys
from pathlib import Path

import pytest
import pytest_asyncio

# Make the `src` package importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import dispatcher  # noqa: E402
from src.cache import Cache  # noqa: E402


@pytest.fixture(autouse=True)
def isolate_global_state(monkeypatch):
    """The cache and the shared backend are process-global; isolate each test."""
    monkeypatch.setattr(dispatcher, "_database", None)
    Cache.flush()
    yield
    Cache.flush()


@pytest_asyncio.fixture
async def use_database(monkeypatch):
    """
    Installs a database backend as the dispatcher's shared backend and closes
    it after the test (each test runs in its own event loop).
    """
    installed = []

    def install(database):
        monkeypatch.setattr(dispatcher, "_database", database)
        installed.append(database)
        return database

    yield install

    for database in installed:
        await database.close()
