def build_sql_query(table, fields=None, filters=None):
        """
        Converts request payload to sql query
        """
        assert table, "Table name is required"

        ALL_FIELDS = "*"
        SELECT = "SELECT"
        FROM = "FROM"
        AND = "AND"
        WHERE = "WHERE"

        if fields:
            selected_fields = ", ".join(fields)
        else:
            selected_fields = ALL_FIELDS

        query = f"{SELECT} {selected_fields} {FROM} {table}"

        if filters:
            filter_clause = f" {AND} ".join(
                [f"{key} = '{value}'" for key, value in filters.items()]
            )
            query += f" {WHERE} {filter_clause}"

        return query