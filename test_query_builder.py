import pytest
from db.query_builder import build_sql_query

def test_build_sql_query_with_no_filters():
    query = build_sql_query("table")
    assert query == "SELECT * FROM table"

def test_build_sql_query_with_filters_and_fields():
    query = build_sql_query("table", fields=["name", "price"], filters={"price": 30})
    assert query == "SELECT name, price FROM table WHERE price = '30'"

def test_build_sql_query_with_no_table():
    with pytest.raises(AssertionError):
        build_sql_query('', fields=["name", "price"], filters={"price": 30})
