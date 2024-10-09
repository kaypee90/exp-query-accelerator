class Query:
    def __init__(self, table):
        self.table = table


class Filter:
    def __init__(self, field, value, operator="="):
        self.field = field
        self.value = value
        self.operator = operator

        if not self.field:
            raise ValueError("Field is required")


class SelectQuery(Query):
    def __init__(self, table, fields):
        super().__init__(table)
        self._fields = fields
        self._validate_fields()
        self._query = self._select_query()
        self._filter = None
        self._ordering = None

    def _validate_fields(self):
        if not self._fields:
            raise ValueError("Fields are required")

        if not isinstance(self._fields, list) and not isinstance(self._fields, str):
            raise ValueError("Fields must be a list of strings or a string")

    def _select_query(self):
        fields = None
        if isinstance(self._fields, list):
            fields = ", ".join(self._fields)
        elif isinstance(self._fields, str):
            fields = self._fields

        return f"SELECT {fields} FROM {self.table}"

    def _validate_filter(self, filter):
        if not isinstance(filter, Filter):
            raise TypeError("Filter must be a Filter object")

    def _get_filter_value(self, filter):
        return f"'{filter.value}'" if isinstance(filter.value, str) else filter.value

    def _validate_ordering_field(self, field):
        if not isinstance(field, str):
            raise TypeError("Field must be a string")

    @property
    def query(self):
        query = self._query
        if self._filter:
            query = f"{query} {self._filter}"
        if self._ordering:
            query = f"{query} {self._ordering}"
        return query

    def filter(self, filter):
        self._validate_filter(filter)
        value = self._get_filter_value(filter)
        self._filter = f"WHERE {filter.field} {filter.operator} {value}"

    def and_filter(self, filter):
        if not self._filter:
            raise ValueError("Cannot apply an AND filter without an existing filter")

        self._validate_filter(filter)
        value = self._get_filter_value(filter)
        self._filter = f"{self._filter} AND {filter.field} {filter.operator} {value}"

    def or_filter(self, filter):
        if not self._filter:
            raise ValueError("Cannot apply an OR filter without an existing filter")

        self._validate_filter(filter)
        value = self._get_filter_value(filter)
        self._filter = f"{self._filter} OR {filter.field} {filter.operator} {value}"

    def order_by(self, field):
        self._validate_ordering_field(field)
        self._ordering = f"ORDER BY {field}"

    def order_by_desc(self, field):
        self._validate_ordering_field(field)
        self._ordering = f"ORDER BY {field} DESC"

    def __str__(self):
        return self.query
