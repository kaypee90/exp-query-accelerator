import pytest

from src.db.query_builder import build_sql_query


class TestQueryBuilder:
    def test_build_sql_query_with_no_filters(self):
        assert build_sql_query("products") == ("SELECT * FROM products", ())

    def test_build_sql_query_with_empty_fields_selects_all(self):
        sql, _ = build_sql_query("products", fields=[])
        assert sql == "SELECT * FROM products"

    def test_build_sql_query_with_filters_and_fields(self):
        sql, params = build_sql_query(
            "products",
            fields=["name", "price"],
            filters=[{"field": "price", "value": "30", "operator": "="}],
        )
        assert sql == "SELECT name, price FROM products WHERE price = ?"
        assert params == ("30",)

    def test_build_sql_query_with_no_table(self):
        with pytest.raises(ValueError):
            build_sql_query(
                "",
                fields=["name", "price"],
                filters=[{"field": "price", "value": "30", "operator": "="}],
            )

    def test_build_sql_query_with_multiple_filters_and_fields(self):
        # Conditions are joined in request order without parentheses, so SQL
        # precedence applies: AND binds tighter than OR.
        sql, params = build_sql_query(
            "products",
            fields=["name", "price"],
            filters=[
                {"field": "price", "value": "30%", "operator": "LIKE"},
                {"field": "name", "value": "Lisa Smith", "operator": "=", "bind": "|"},
                {"field": "price", "value": 10, "operator": ">", "bind": "&"},
            ],
        )
        assert (
            sql == "SELECT name, price FROM products "
            "WHERE price LIKE ? OR name = ? AND price > ?"
        )
        assert params == ("30%", "Lisa Smith", 10)

    def test_build_sql_query_with_postgres_placeholder(self):
        sql, params = build_sql_query(
            "products",
            filters=[{"field": "price", "value": "30%", "operator": "like"}],
            placeholder="%s",
        )
        assert sql == "SELECT * FROM products WHERE price LIKE %s"
        assert params == ("30%",)

    @pytest.mark.parametrize(
        "order_dir, expected",
        [
            (None, "ORDER BY name"),
            ("asc", "ORDER BY name"),
            ("DESC", "ORDER BY name DESC"),
        ],
    )
    def test_build_sql_query_ordering(self, order_dir, expected):
        sql, _ = build_sql_query("products", order_by="name", order_dir=order_dir)
        assert sql == f"SELECT * FROM products {expected}"

    def test_build_sql_query_rejects_unsafe_table(self):
        with pytest.raises(ValueError):
            build_sql_query("products; DROP TABLE products; --")
