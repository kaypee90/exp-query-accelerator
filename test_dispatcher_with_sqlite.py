import pytest
import json
import sqlite3
from dispatcher import dispatch


@pytest.fixture
def setup_database():
    # Connect to a test database (SQLite for example)
    SQLITE_DB = "test_db"
    conn = sqlite3.connect(SQLITE_DB)  # In-memory database for testing
    cursor = conn.cursor()

    # Create a test table
    cursor.execute(
        """CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"""
    )

    # Insert setup data
    users = [(1, "John Doe", 30), (2, "Jane Smith", 25)]
    cursor.executemany("INSERT INTO users (id, name, age) VALUES (?, ?, ?)", users)
    conn.commit()

    # Yield the database connection to use in tests
    yield conn

    # Teardown: Close the connection after the test
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.close()


@pytest.mark.asyncio
async def test_dispatch_db_and_cached_data_should_be_same(setup_database):
    cursor = setup_database.cursor()

    # Query the database
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

    # Assert the data is as expected
    assert len(results) == 2

    payload = json.dumps({"table": "users", "fields": ["id", "name", "age"]})

    error, data = await dispatch(payload)

    assert error is None
    assert data == results

    error_2, data_2 = await dispatch(payload)

    assert error_2 is None
    assert data_2 == results
