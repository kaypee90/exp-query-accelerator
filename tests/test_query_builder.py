import pytest
from src.db.query_builder import build_sql_query


class TestQueryBuilder:

    def test_build_sql_query_with_no_filters(self):
        query = build_sql_query("table")
        assert query == "SELECT * FROM table"

    def test_build_sql_query_with_filters_and_fields(self):
        query = build_sql_query(
            "table",
            fields=["name", "price"],
            filters=[{"field": "price", "value": "30", "operator": "="}],
        )
        assert query == "SELECT name, price FROM table WHERE price = '30'"

    def test_build_sql_query_with_no_table(self):
        with pytest.raises(AssertionError):
            build_sql_query(
                "",
                fields=["name", "price"],
                filters=[{"field": "price", "value": "30", "operator": "="}],
            )

    def test_build_sql_query_with_multiple_filters_and_fields(self):
        query = build_sql_query(
            "table",
            fields=["name", "price"],
            filters=[
                {"field": "price", "value": "30%", "operator": "LIKE"},
                {"field": "name", "value": "Lisa Smith", "operator": "=", "bind": "|"},
            ],
        )
        assert (
            query
            == "SELECT name, price FROM table WHERE price LIKE '30%' OR name = 'Lisa Smith'"
        )
