"""
End-to-end tests against a real Postgres. Run via `make test_pg_e2e`, which
starts a container and exports the POSTGRES_* variables used below.
"""

import json

import psycopg
import pytest

from src.db.postgres import Postgres
from src.dispatcher import dispatch
from src.utils.config import get_pg_conn_str

pytestmark = pytest.mark.asyncio

USERS = [("John Doe", 20), ("Jane Smith", 25), ("Lisa Smith", 20)]


@pytest.fixture
def setup_database(use_database):
    conn_str = get_pg_conn_str()
    with psycopg.connect(conn_str, autocommit=True) as conn:
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute(
            "CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(100), age INT)"
        )
        with conn.cursor() as cursor:
            cursor.executemany("INSERT INTO users (name, age) VALUES (%s, %s)", USERS)

        use_database(Postgres(conn_str))
        yield conn

        conn.execute("DROP TABLE IF EXISTS users")


async def test_dispatch_db_and_cached_data_should_be_same(setup_database):
    expected = setup_database.execute(
        "SELECT id, name, age FROM users WHERE age > 18 AND age <= 22 ORDER BY id"
    ).fetchall()
    assert len(expected) == 2

    payload = json.dumps(
        {
            "table": "users",
            "fields": ["id", "name", "age"],
            "filters": [
                {"field": "age", "value": 18, "operator": ">"},
                {"field": "age", "value": 22, "operator": "<=", "bind": "&"},
            ],
            "order_by": "id",
        }
    )

    error, data = await dispatch(payload)

    assert error is None
    assert data == expected

    setup_database.execute("DELETE FROM users")
    error_2, data_2 = await dispatch(payload)

    assert error_2 is None
    assert data_2 == expected


async def test_dispatch_db_with_or_query(setup_database):
    expected = setup_database.execute(
        "SELECT id, name, age FROM users WHERE age > 24 OR name = 'Lisa Smith' "
        "ORDER BY id"
    ).fetchall()
    assert len(expected) == 2

    payload = json.dumps(
        {
            "table": "users",
            "fields": ["id", "name", "age"],
            "filters": [
                {"field": "age", "value": 24, "operator": ">"},
                {"field": "name", "value": "Lisa Smith", "operator": "=", "bind": "|"},
            ],
            "order_by": "id",
        }
    )

    error, data = await dispatch(payload)

    assert error is None
    assert data == expected


async def test_dispatch_with_like_and_quotes(setup_database):
    setup_database.execute("INSERT INTO users (name, age) VALUES ('Seán O''Brien', 41)")

    error, data = await dispatch(
        json.dumps(
            {
                "table": "users",
                "fields": ["name"],
                "filters": [{"field": "name", "value": "%O'B%", "operator": "LIKE"}],
            }
        )
    )

    assert error is None
    assert data == [("Seán O'Brien",)]


async def test_dispatch_value_injection_is_treated_as_data(setup_database):
    error, data = await dispatch(
        json.dumps(
            {
                "table": "users",
                "filters": [
                    {"field": "name", "value": "x' OR '1'='1", "operator": "="}
                ],
            }
        )
    )

    assert error is None
    assert data == []


async def test_dispatch_unknown_table_returns_error(setup_database):
    error, data = await dispatch(json.dumps({"table": "missing"}))

    assert "missing" in error
    assert data is None


async def test_dispatch_invalid_value_for_column_type_returns_error(setup_database):
    error, data = await dispatch(
        json.dumps(
            {
                "table": "users",
                "filters": [{"field": "age", "value": "abc", "operator": "="}],
            }
        )
    )

    assert "invalid input syntax" in error
    assert data is None


async def test_dispatch_reuses_connection_pool(setup_database):
    database = Postgres(get_pg_conn_str())
    try:
        await database.query(table="users")
        pool = database._pool
        await database.query(table="users")

        assert pool is not None
        assert database._pool is pool
    finally:
        await database.close()
    assert database._pool is None
