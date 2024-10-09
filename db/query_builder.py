from db.query import SelectQuery, Filter


def build_sql_query(table, fields=None, filters=None):
    """
    Converts request payload to sql query
    """
    assert table, "Table name is required"

    ALL_FIELDS = "*"

    selected_fields = fields or ALL_FIELDS
    query = SelectQuery(table, selected_fields)
    if filters:
        query_filter = [Filter(key, value) for key, value in filters.items()]
        query.filter(query_filter[0])

        # Fix this to support OR too
        if len(query_filter) > 1:
            for filter in query_filter[1:]:
                query.and_filter(filter)

    return query.query

