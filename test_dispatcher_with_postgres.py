import json
import pytest
import psycopg2
from dispatcher import dispatch


# Define a fixture for database setup and teardown
@pytest.fixture(scope="function")
def setup_database():
    # Connection details defined in bash file
    conn = psycopg2.connect(
        host="localhost",
        database="testdb",
        user="testuser",
        password="testpass",
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INT
        )
    """
    )

    users = [("John Doe", 20), ("Jane Smith", 25), ("Lisa Smith", 20)]
    cursor.executemany("INSERT INTO users (name, age) VALUES (%s, %s)", users)
    conn.commit()

    # Yield the connection so it can be used in tests
    yield conn

    # Teardown: Drop the table after the test
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.commit()

    # Close connection
    cursor.close()
    conn.close()


@pytest.mark.asyncio
async def test_dispatch_db_and_cached_data_should_be_same(setup_database):
    # Get the cursor from the connection provided by the fixture
    cursor = setup_database.cursor()

    # Query the database
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

    # Assert that the data is as expected
    assert len(results) == 3

    # Query the database
    cursor.execute("SELECT id, name, age FROM users WHERE age = 20")
    results = cursor.fetchall()

    # Assert that the data is as expected
    assert len(results) == 2

    payload = json.dumps(
        {
            "table": "users",
            "fields": ["id", "name", "age"],
            "filters": [
                {"field": "age", "value": 18, "operator": ">"},
                {"field": "age", "value": 22, "operator": "<=", "bind": "&"},
            ],
        }
    )

    error, data = await dispatch(payload)

    assert error is None
    assert data == results

    error_2, data_2 = await dispatch(payload)

    assert error_2 is None
    assert data == data_2


@pytest.mark.asyncio
async def test_dispatch_db_with_or_query(setup_database):
    cursor = setup_database.cursor()

    # Query the database
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

    # Assert that the data is as expected
    assert len(results) == 3

    # Query the database
    cursor.execute(
        "SELECT id, name, age FROM users WHERE age > 24 OR name = 'Lisa Smith'"
    )
    results = cursor.fetchall()

    # Assert that the data is as expected
    assert len(results) == 2

    payload = json.dumps(
        {
            "table": "users",
            "fields": ["id", "name", "age"],
            "filters": [
                {"field": "age", "value": 24, "operator": ">"},
                {"field": "name", "value": "Lisa Smith", "operator": "=", "bind": "|"},
            ],
        }
    )

    error, data = await dispatch(payload)

    assert error is None
    assert data == results
