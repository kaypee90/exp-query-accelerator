"""
Minimal, injection-safe SELECT query builder.

Identifiers (table, fields, order by) are validated against a strict pattern
because they cannot be bound as parameters. Filter values are never inlined
into the SQL; they are collected in `params` and bound by the database driver.
"""

import re

AND = "&"
OR = "|"
BINDS = {AND: "AND", OR: "OR"}

OPERATORS = frozenset({"=", "!=", "<>", "<", "<=", ">", ">=", "LIKE", "NOT LIKE"})
ALL_FIELDS = "*"

# Plain identifier, optionally schema-qualified: name or schema.name
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?")


def is_valid_identifier(name):
    return isinstance(name, str) and _IDENTIFIER.fullmatch(name) is not None


def is_valid_bind(bind):
    return isinstance(bind, str) and bind in BINDS


def normalize_operator(operator):
    """Returns the canonical operator, or None if it is not supported."""
    if not isinstance(operator, str):
        return None
    canonical = " ".join(operator.upper().split())
    return canonical if canonical in OPERATORS else None


def _require_identifier(name, label):
    if not is_valid_identifier(name):
        raise ValueError(f"Invalid {label}: {name!r}")


class Filter:
    def __init__(self, field, value, operator="=", bind=AND):
        if not field:
            raise ValueError("Field is required")
        _require_identifier(field, "field")

        canonical_operator = normalize_operator(operator)
        if canonical_operator is None:
            raise ValueError(f"Invalid operator: {operator!r}")

        if not is_valid_bind(bind):
            raise ValueError("Invalid bind value")

        self.field = field
        self.value = value
        self.operator = canonical_operator
        self.bind = bind


class SelectQuery:
    def __init__(self, table, fields, placeholder="?"):
        _require_identifier(table, "table")
        self.table = table
        self._fields = fields
        self._validate_fields()
        self._placeholder = placeholder
        self._conditions = []
        self._params = []
        self._ordering = None

    def _validate_fields(self):
        if not self._fields:
            raise ValueError("Fields are required")

        if self._fields == ALL_FIELDS:
            return

        if not isinstance(self._fields, list):
            raise ValueError("Fields must be a list of strings or '*'")

        for field in self._fields:
            _require_identifier(field, "field")

    def _select_clause(self):
        fields = self._fields if self._fields == ALL_FIELDS else ", ".join(self._fields)
        return f"SELECT {fields} FROM {self.table}"

    def _add_condition(self, filter, connector=None):
        if not isinstance(filter, Filter):
            raise TypeError("Filter must be a Filter object")

        condition = f"{filter.field} {filter.operator} {self._placeholder}"
        if connector:
            condition = f"{connector} {condition}"
        self._conditions.append(condition)
        self._params.append(filter.value)

    def _require_existing_filter(self, connector):
        if not self._conditions:
            raise ValueError(
                f"Cannot apply an {connector} filter without an existing filter"
            )

    @property
    def query(self):
        """SQL text with driver placeholders for every filter value."""
        parts = [self._select_clause()]
        if self._conditions:
            parts.append("WHERE " + " ".join(self._conditions))
        if self._ordering:
            parts.append(self._ordering)
        return " ".join(parts)

    @property
    def params(self):
        """Values to bind to the placeholders, in order."""
        return tuple(self._params)

    def filter(self, filter):
        """Sets the first WHERE condition, replacing any existing conditions."""
        self._conditions = []
        self._params = []
        self._add_condition(filter)

    def and_filter(self, filter):
        self._require_existing_filter("AND")
        self._add_condition(filter, "AND")

    def or_filter(self, filter):
        self._require_existing_filter("OR")
        self._add_condition(filter, "OR")

    def order_by(self, field):
        self._set_ordering(field, "")

    def order_by_desc(self, field):
        self._set_ordering(field, " DESC")

    def _set_ordering(self, field, direction):
        if not isinstance(field, str):
            raise TypeError("Field must be a string")
        _require_identifier(field, "order by field")
        self._ordering = f"ORDER BY {field}{direction}"

    def __str__(self):
        return self.query
