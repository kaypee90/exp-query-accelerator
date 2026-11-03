import pytest

from src.db.query import Filter, SelectQuery, is_valid_identifier, normalize_operator


class TestIdentifiers:
    @pytest.mark.parametrize("name", ["users", "_users", "user_2", "public.users"])
    def test_valid_identifiers(self, name):
        assert is_valid_identifier(name)

    @pytest.mark.parametrize(
        "name",
        [
            "",
            None,
            1,
            "2users",
            "users; DROP TABLE users",
            "users--",
            "a b",
            "a.b.c",
            "name'",
            '"name"',
            "*",
        ],
    )
    def test_invalid_identifiers(self, name):
        assert not is_valid_identifier(name)


class TestOperators:
    @pytest.mark.parametrize(
        "operator, expected",
        [("=", "="), ("like", "LIKE"), ("not   like", "NOT LIKE"), ("<>", "<>")],
    )
    def test_normalizes_supported_operators(self, operator, expected):
        assert normalize_operator(operator) == expected

    @pytest.mark.parametrize("operator", ["", None, "OR 1=1 --", "IN", ";", 1])
    def test_rejects_unsupported_operators(self, operator):
        assert normalize_operator(operator) is None


class TestFilter:
    def test_filter_requires_field(self):
        with pytest.raises(ValueError):
            Filter(None, "two")

    def test_filter_rejects_unsafe_field(self):
        with pytest.raises(ValueError):
            Filter("age = 1 OR 1", 1)

    def test_filter_rejects_unsupported_operator(self):
        with pytest.raises(ValueError):
            Filter("age", 1, "= 1 OR 1 =")

    @pytest.mark.parametrize("bind", ["^", "AND", [], {}, None])
    def test_filter_rejects_invalid_bind(self, bind):
        with pytest.raises(ValueError):
            Filter("age", 1, "=", bind)


class TestSelectQuery:
    def test_select_query_for_all_fields(self):
        q = SelectQuery("users", "*")
        assert q.query == "SELECT * FROM users"
        assert q.params == ()

    def test_select_query_with_specific_fields(self):
        q = SelectQuery("users", ["name", "age"])
        assert q.query == "SELECT name, age FROM users"

    def test_select_query_with_invalid_fields(self):
        with pytest.raises(ValueError):
            SelectQuery("users", None)

    def test_select_query_rejects_unsafe_table(self):
        with pytest.raises(ValueError):
            SelectQuery("users; DROP TABLE users", "*")

    def test_select_query_rejects_unsafe_field(self):
        with pytest.raises(ValueError):
            SelectQuery("users", ["name", "(SELECT password FROM admins)"])

    def test_select_query_rejects_non_star_string_fields(self):
        with pytest.raises(ValueError):
            SelectQuery("users", "name, password")

    def test_filter_with_invalid_filter_type(self):
        q = SelectQuery("users", ["name", "age"])
        with pytest.raises(TypeError):
            q.filter(123)

    def test_filter_query_with_valid_filter(self):
        q = SelectQuery("users", ["name", "age"])
        q.filter(Filter("age", 20, ">"))
        expected_query = "SELECT name, age FROM users WHERE age > ?"

        assert q.query == expected_query
        assert str(q) == expected_query
        assert q.params == (20,)

    def test_filter_values_are_never_inlined(self):
        q = SelectQuery("users", "*")
        malicious = "x' OR '1'='1"
        q.filter(Filter("name", malicious))

        assert malicious not in q.query
        assert q.params == (malicious,)

    def test_custom_placeholder(self):
        q = SelectQuery("users", "*", placeholder="%s")
        q.filter(Filter("age", 20, ">"))
        q.and_filter(Filter("name", "John"))

        assert q.query == "SELECT * FROM users WHERE age > %s AND name = %s"

    def test_filter_replaces_existing_conditions(self):
        q = SelectQuery("users", "*")
        q.filter(Filter("age", 20, ">"))
        q.filter(Filter("name", "John"))

        assert q.query == "SELECT * FROM users WHERE name = ?"
        assert q.params == ("John",)

    def test_and_filter_without_initial_filtering(self):
        q = SelectQuery("users", ["name", "age"])
        with pytest.raises(ValueError):
            q.and_filter(Filter("age", 20, ">"))

    def test_and_filter_with_initial_filtering(self):
        q = SelectQuery("users", ["name", "age"])
        q.filter(Filter("age", 20, ">"))
        q.and_filter(Filter("name", "John"))

        assert q.query == "SELECT name, age FROM users WHERE age > ? AND name = ?"
        assert q.params == (20, "John")

    def test_or_filter_without_initial_filtering(self):
        q = SelectQuery("users", ["name", "age"])
        with pytest.raises(ValueError):
            q.or_filter(Filter("age", 20, ">"))

    def test_or_filter_with_initial_filtering(self):
        q = SelectQuery("users", ["name", "age"])
        q.filter(Filter("age", 20, ">"))
        q.or_filter(Filter("name", "John"))

        assert q.query == "SELECT name, age FROM users WHERE age > ? OR name = ?"
        assert q.params == (20, "John")

    def test_order_by_with_invalid_field_type(self):
        q = SelectQuery("users", ["name", "age"])
        with pytest.raises(TypeError):
            q.order_by(190)

    def test_order_by_rejects_unsafe_field(self):
        q = SelectQuery("users", ["name", "age"])
        with pytest.raises(ValueError):
            q.order_by("age; DROP TABLE users")

    def test_order_by_with_filtering(self):
        q = SelectQuery("users", ["name", "age"])
        q.filter(Filter("age", 20, ">"))
        q.order_by("age")
        q.or_filter(Filter("name", "John"))

        assert (
            q.query
            == "SELECT name, age FROM users WHERE age > ? OR name = ? ORDER BY age"
        )

    def test_order_by_desc_with_invalid_field_type(self):
        q = SelectQuery("users", ["name", "age"])
        with pytest.raises(TypeError):
            q.order_by_desc(190)

    def test_order_by_desc_with_filtering(self):
        q = SelectQuery("users", ["name", "age"])
        q.filter(Filter("age", 20, ">"))
        q.order_by_desc("age")
        q.or_filter(Filter("name", "John"))

        assert (
            q.query
            == "SELECT name, age FROM users WHERE age > ? OR name = ? ORDER BY age DESC"
        )
