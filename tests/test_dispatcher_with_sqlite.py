import json
import sqlite3

import pytest

from src.db.sqlite import Sqlite
from src.dispatcher import dispatch

pytestmark = pytest.mark.asyncio

USERS = [(1, "John Doe", 30), (2, "Jane Smith", 25), (3, "Seán O'Brien", 41)]


@pytest.fixture
def db_path(tmp_path, use_database):
    path = str(tmp_path / "test.db")
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INT)")
        conn.executemany("INSERT INTO users (id, name, age) VALUES (?, ?, ?)", USERS)
    use_database(Sqlite(path))
    return path


def run_sql(path, sql):
    with sqlite3.connect(path) as conn:
        return conn.execute(sql).fetchall()


def payload(**kwargs):
    return json.dumps({"table": "users", "fields": ["id", "name", "age"], **kwargs})


async def test_dispatch_db_and_cached_data_should_be_same(db_path):
    error, data = await dispatch(payload())

    assert error is None
    assert data == USERS

    error_2, data_2 = await dispatch(payload())

    assert error_2 is None
    assert data_2 == USERS


async def test_dispatch_serves_repeated_queries_from_cache(db_path):
    await dispatch(payload())
    run_sql(db_path, "DELETE FROM users")

    error, data = await dispatch(payload())

    assert error is None
    assert data == USERS


async def test_dispatch_equivalent_payloads_share_cache_entry(db_path):
    await dispatch(json.dumps({"table": "users", "order_by": "id"}))
    run_sql(db_path, "DELETE FROM users")

    error, data = await dispatch('{ "order_by" : "id", "table" : "users" }')

    assert error is None
    assert data == USERS


async def test_dispatch_caches_empty_results(db_path):
    query = payload(filters=[{"field": "age", "operator": ">", "value": 100}])
    _, data = await dispatch(query)
    run_sql(db_path, "INSERT INTO users VALUES (4, 'Old Timer', 101)")

    error, data_2 = await dispatch(query)

    assert error is None
    assert data == data_2 == []


async def test_dispatch_db_should_be_ordered_by_id(db_path):
    error, data = await dispatch(payload(order_by="id", order_dir="desc"))

    assert error is None
    assert [row[0] for row in data] == [3, 2, 1]


async def test_dispatch_with_and_or_filters(db_path):
    error, data = await dispatch(
        payload(
            filters=[
                {"field": "age", "operator": ">", "value": 26},
                {"field": "name", "operator": "=", "value": "Jane Smith", "bind": "|"},
            ],
            order_by="id",
        )
    )

    assert error is None
    assert data == USERS


async def test_dispatch_with_like_filter(db_path):
    error, data = await dispatch(
        payload(filters=[{"field": "name", "operator": "like", "value": "J%"}])
    )

    assert error is None
    assert sorted(row[0] for row in data) == [1, 2]


async def test_dispatch_handles_quotes_in_values(db_path):
    error, data = await dispatch(
        payload(filters=[{"field": "name", "operator": "=", "value": "Seán O'Brien"}])
    )

    assert error is None
    assert data == [USERS[2]]


async def test_dispatch_value_injection_is_treated_as_data(db_path):
    error, data = await dispatch(
        payload(filters=[{"field": "name", "operator": "=", "value": "x' OR '1'='1"}])
    )

    assert error is None
    assert data == []


async def test_dispatch_rejects_table_injection(db_path):
    error, data = await dispatch(json.dumps({"table": "users; DROP TABLE users"}))

    assert error == "`table` must be a valid identifier"
    assert data is None
    assert len(run_sql(db_path, "SELECT * FROM users")) == len(USERS)


async def test_dispatch_unknown_table_returns_error_and_is_not_cached(db_path):
    query = json.dumps({"table": "missing"})

    error, data = await dispatch(query)
    assert "no such table" in error
    assert data is None

    run_sql(db_path, "CREATE TABLE missing (id INT)")
    error, data = await dispatch(query)
    assert error is None
    assert data == []


async def test_dispatch_unknown_column_returns_error(db_path):
    error, data = await dispatch(json.dumps({"table": "users", "fields": ["nope"]}))

    assert "no such column" in error
    assert data is None


@pytest.mark.parametrize("body", ["not json", b"\xff\xfe", "{"])
async def test_dispatch_invalid_json(body):
    assert await dispatch(body) == ("Invalid JSON payload", None)


async def test_dispatch_invalid_payload():
    error, data = await dispatch(json.dumps({"fields": "name"}))

    assert error == "`table` is required, `fields` must be a list"
    assert data is None


async def test_dispatch_integer_too_large_for_sqlite_returns_error(db_path):
    error, data = await dispatch(
        payload(filters=[{"field": "age", "operator": "=", "value": 2**64}])
    )

    assert "too large" in error
    assert data is None


async def test_dispatch_server_side_sqlite_fault_is_raised(tmp_path, use_database):
    use_database(Sqlite(str(tmp_path / "missing_dir" / "x.db")))

    with pytest.raises(sqlite3.OperationalError):
        await dispatch(json.dumps({"table": "users"}))


async def test_dispatch_deeply_nested_json_is_invalid():
    assert await dispatch(b"[" * 100_000) == ("Invalid JSON payload", None)
