import pytest
from db.query import SelectQuery, Filter


def test_select_query_for_all_fields():
    q = SelectQuery("users", "*")
    assert q.query == "SELECT * FROM users"


def test_select_query_with_specific_fields():
    q = SelectQuery("users", ["name", "age"])
    assert q.query == "SELECT name, age FROM users"


def test_select_query_with_with_invalid_fields():
    with pytest.raises(ValueError):
        q = SelectQuery("users", None)
        q.query


def test_filter_with_invalid_filter_type():
    with pytest.raises(TypeError):
        q = SelectQuery("users", ["name", "age"])
        q.filter(123)


def test_invalid_filter_with_no_field():
    with pytest.raises(ValueError):
        q = SelectQuery("users", ["name", "age"])
        q.filter(Filter(None, "two"))


def test_filter_query_with_valid_filter():
    q = SelectQuery("users", ["name", "age"])
    q.filter(Filter("age", 20, ">"))
    expected_query = "SELECT name, age FROM users WHERE age > 20"

    assert q.query == expected_query
    assert str(q) == expected_query


def test_and_filter_without_initial_filtering():
    with pytest.raises(ValueError):
        q = SelectQuery("users", ["name", "age"])
        q.and_filter(Filter("age", 20, ">"))


def test_and_filter_with_initial_filtering():
    q = SelectQuery("users", ["name", "age"])
    q.filter(Filter("age", 20, ">"))
    q.and_filter(Filter("name", "John"))
    expected_query = "SELECT name, age FROM users WHERE age > 20 AND name = 'John'"

    assert q.query == expected_query
    assert str(q) == expected_query


def test_or_filter_without_initial_filtering():
    with pytest.raises(ValueError):
        q = SelectQuery("users", ["name", "age"])
        q.or_filter(Filter("age", 20, ">"))


def test_or_filter_with_initial_filtering():
    q = SelectQuery("users", ["name", "age"])
    q.filter(Filter("age", 20, ">"))
    q.or_filter(Filter("name", "John"))
    expected_query = "SELECT name, age FROM users WHERE age > 20 OR name = 'John'"

    assert q.query == expected_query
    assert str(q) == expected_query


def test_order_by_with_invalid_field_type():
    with pytest.raises(TypeError):
        q = SelectQuery("users", ["name", "age"])
        q.order_by(190)


def test_order_by_with_filtering():
    q = SelectQuery("users", ["name", "age"])
    q.filter(Filter("age", 20, ">"))
    q.order_by("age")
    q.or_filter(Filter("name", "John"))
    expected_query = (
        "SELECT name, age FROM users WHERE age > 20 OR name = 'John' ORDER BY age"
    )

    assert q.query == expected_query
    assert str(q) == expected_query


def test_order_by_desc_with_invalid_field_type():
    with pytest.raises(TypeError):
        q = SelectQuery("users", ["name", "age"])
        q.order_by_desc(190)


def test_order_by_desc_with_filtering():
    q = SelectQuery("users", ["name", "age"])
    q.filter(Filter("age", 20, ">"))
    q.order_by_desc("age")
    q.or_filter(Filter("name", "John"))
    expected_query = (
        "SELECT name, age FROM users WHERE age > 20 OR name = 'John' ORDER BY age DESC"
    )

    assert q.query == expected_query
    assert str(q) == expected_query
