from db.query import SelectQuery, Filter, AND, OR


def build_sql_query(table, fields=None, filters=None):
    """
    Converts request payload to sql query
    """
    assert table, "Table name is required"
    ALL_FIELDS = "*"

    selected_fields = fields or ALL_FIELDS
    query = SelectQuery(table, selected_fields)
    if filters:
        query_filter = [
            Filter(
                filter["field"],
                filter["value"],
                filter["operator"],
                filter.get("bind", AND),
            )
            for filter in filters
        ]
        query.filter(query_filter[0])

        if len(query_filter) > 1:
            for filter in query_filter[1:]:
                if filter.bind == OR:
                    query.or_filter(filter)
                else:
                    query.and_filter(filter)

    return query.query

