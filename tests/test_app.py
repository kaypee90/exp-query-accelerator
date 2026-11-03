"""
ASGI-level tests for the app, driven by in-memory receive/send callables.
"""

import json
import sqlite3

import pytest

from src import dispatcher
from src.app import app
from src.db.sqlite import Sqlite
from src.handlers import MAX_BODY_BYTES

pytestmark = pytest.mark.asyncio


async def call(method="GET", body_chunks=(b"",)):
    chunks = list(body_chunks)
    messages = [
        {"type": "http.request", "body": chunk, "more_body": i < len(chunks) - 1}
        for i, chunk in enumerate(chunks)
    ]
    sent = []

    async def receive():
        return messages.pop(0)

    async def send(message):
        sent.append(message)

    await app({"type": "http", "method": method}, receive, send)

    start, body = sent
    return start["status"], dict(start["headers"]), json.loads(body["body"])


@pytest.fixture
def sqlite_db(tmp_path, use_database):
    path = str(tmp_path / "app.db")
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE products (name TEXT, price INT)")
        conn.execute("INSERT INTO products VALUES ('Bread', 109)")
        conn.execute("CREATE TABLE images (pic BLOB)")
        conn.execute("INSERT INTO images VALUES (x'00ff')")
    use_database(Sqlite(path))


async def test_get_is_health_check():
    status, headers, body = await call("GET")

    assert status == 200
    assert headers[b"content-type"] == b"application/json"
    assert body == {"status": "Healthy"}


@pytest.mark.parametrize("method", ["PUT", "DELETE", "PATCH"])
async def test_other_methods_are_not_allowed(method):
    status, headers, body = await call(method)

    assert status == 405
    assert headers[b"allow"] == b"GET, POST"
    assert "message" in body


async def test_post_with_empty_body():
    status, _, body = await call("POST")

    assert status == 400
    assert body == {"message": "Request body cannot be empty"}


async def test_post_with_invalid_json():
    status, _, body = await call("POST", [b"{nope"])

    assert status == 400
    assert body == {"message": "Invalid JSON payload"}


async def test_post_with_invalid_payload():
    status, _, body = await call("POST", [b"[]"])

    assert status == 400
    assert body == {"message": "Payload must be a JSON object"}


async def test_post_returns_rows(sqlite_db):
    status, _, body = await call("POST", [b'{"table": "products"}'])

    assert status == 200
    assert body == {"data": [["Bread", 109]]}


async def test_post_reads_chunked_body(sqlite_db):
    status, _, body = await call("POST", [b'{"table": ', b'"products"}'])

    assert status == 200
    assert body == {"data": [["Bread", 109]]}


async def test_post_with_database_error_is_bad_request(sqlite_db):
    status, _, body = await call("POST", [b'{"table": "missing"}'])

    assert status == 400
    assert "no such table" in body["message"]


async def test_post_with_unexpected_error_is_server_error(monkeypatch):
    class BrokenDatabase:
        async def query(self, **kwargs):
            raise ConnectionError("database is down")

    monkeypatch.setattr(dispatcher, "_database", BrokenDatabase())

    status, _, body = await call("POST", [b'{"table": "products"}'])

    assert status == 500
    assert body == {"message": "Internal server error"}


async def test_lifespan_closes_database_on_shutdown(monkeypatch):
    closed = []

    class FakeDatabase:
        async def close(self):
            closed.append(True)

    monkeypatch.setattr(dispatcher, "_database", FakeDatabase())
    messages = [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]
    sent = []

    async def receive():
        return messages.pop(0)

    async def send(message):
        sent.append(message["type"])

    await app({"type": "lifespan"}, receive, send)

    assert sent == ["lifespan.startup.complete", "lifespan.shutdown.complete"]
    assert closed == [True]
    assert dispatcher._database is None


async def test_post_with_blob_column_is_base64_encoded(sqlite_db):
    status, _, body = await call("POST", [b'{"table": "images"}'])

    assert status == 200
    assert body == {"data": [["AP8="]]}


async def test_post_with_body_too_large():
    chunk = b" " * (MAX_BODY_BYTES // 2 + 1)
    status, _, body = await call("POST", [chunk, chunk, b"never read"])

    assert status == 413
    assert "message" in body


async def test_post_client_disconnect_sends_nothing():
    messages = [
        {"type": "http.request", "body": b'{"table":', "more_body": True},
        {"type": "http.disconnect"},
    ]
    sent = []

    async def receive():
        return messages.pop(0)

    async def send(message):
        sent.append(message)

    await app({"type": "http", "method": "POST"}, receive, send)

    assert sent == []


async def test_post_with_unserializable_rows_is_server_error(monkeypatch):
    class OddDatabase:
        async def query(self, **kwargs):
            return None, [(object(),)]

    monkeypatch.setattr(dispatcher, "_database", OddDatabase())

    status, _, body = await call("POST", [b'{"table": "products"}'])

    assert status == 500
    assert body == {"message": "Internal server error"}
