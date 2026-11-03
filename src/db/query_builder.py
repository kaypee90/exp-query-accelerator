from src.db.query import ALL_FIELDS, AND, OR, Filter, SelectQuery


def build_sql_query(
    table,
    *,
    fields=None,
    filters=None,
    order_by=None,
    order_dir=None,
    placeholder="?",
):
    """
    Converts a request payload to a parameterized SQL query.

    Returns:
        tuple[str, tuple]: The SQL text and the values to bind to it.
    """
    if not table:
        raise ValueError("Table name is required")

    query = SelectQuery(table, fields or ALL_FIELDS, placeholder=placeholder)

    for index, item in enumerate(filters or []):
        query_filter = Filter(
            item["field"],
            item["value"],
            item["operator"],
            item.get("bind", AND),
        )
        if index == 0:
            query.filter(query_filter)
        elif query_filter.bind == OR:
            query.or_filter(query_filter)
        else:
            query.and_filter(query_filter)

    if order_by:
        if order_dir and order_dir.lower() == "desc":
            query.order_by_desc(order_by)
        else:
            query.order_by(order_by)

    return query.query, query.params
