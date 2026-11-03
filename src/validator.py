import math

from src.db.query import BINDS, is_valid_bind, is_valid_identifier, normalize_operator

ALLOWED_KEYS = frozenset({"table", "fields", "filters", "order_by", "order_dir"})
ORDER_DIRECTIONS = frozenset({"asc", "desc"})
SCALAR_TYPES = (str, int, float, bool)


def validate_payload(payload):
    """
    Validates a request payload against the request schema and returns a
    list of human readable errors (empty when the payload is valid).

     Payload:
     {
      "table": "products",
      "fields": ["name", "price"],
      "filters": [
         {"field": "price", "value": "109", "operator": "="},
         {"field": "name", "value": "Rice", "operator": "=", "bind": "|"},
         {"field": "price", "value": "1100", "operator": "=", "bind": "&"}
      ],
      "order_by": "name",
      "order_dir": "asc"
     }
    """
    if not isinstance(payload, dict):
        return ["Payload must be a JSON object"]

    errors = []

    unknown_keys = sorted(set(payload) - ALLOWED_KEYS)
    if unknown_keys:
        errors.append(f"Unknown keys: {', '.join(unknown_keys)}")

    errors.extend(_validate_table(payload.get("table")))
    errors.extend(_validate_fields(payload.get("fields")))
    errors.extend(_validate_filters(payload.get("filters")))
    errors.extend(_validate_ordering(payload.get("order_by"), payload.get("order_dir")))
    return errors


def _validate_table(table):
    if not table:
        return ["`table` is required"]
    if not is_valid_identifier(table):
        return ["`table` must be a valid identifier"]
    return []


def _validate_fields(fields):
    if fields is None:
        return []
    if not isinstance(fields, list):
        return ["`fields` must be a list"]
    if not all(isinstance(field, str) for field in fields):
        return ["`fields` must be a list of strings"]
    if not all(is_valid_identifier(field) for field in fields):
        return ["`fields` must contain valid identifiers"]
    return []


def _validate_filters(filters):
    if filters is None:
        return []
    if not isinstance(filters, list):
        return ["`filters` must be a list"]

    errors = []
    for index, item in enumerate(filters):
        errors.extend(_validate_filter(index, item))
    return errors


def _validate_filter(index, item):
    prefix = f"`filters[{index}]`"
    if not isinstance(item, dict):
        return [f"{prefix} must be an object"]

    errors = []
    field = item.get("field")
    if not isinstance(field, str):
        errors.append(f"{prefix}.field must be a string")
    elif not is_valid_identifier(field):
        errors.append(f"{prefix}.field must be a valid identifier")

    if normalize_operator(item.get("operator")) is None:
        errors.append(f"{prefix}.operator is missing or not supported")

    if "value" not in item:
        errors.append(f"{prefix}.value is required")
    elif not _is_valid_value(item["value"]):
        errors.append(f"{prefix}.value must be a string, finite number or boolean")

    if "bind" in item and not is_valid_bind(item["bind"]):
        errors.append(f"{prefix}.bind must be one of: {', '.join(BINDS)}")
    return errors


def _is_valid_value(value):
    if isinstance(value, float):
        return math.isfinite(value)
    return isinstance(value, SCALAR_TYPES)


def _validate_ordering(order_by, order_dir):
    errors = []
    if order_by is not None and not is_valid_identifier(order_by):
        errors.append("`order_by` must be a valid identifier")
    if order_dir is not None and (
        not isinstance(order_dir, str) or order_dir.lower() not in ORDER_DIRECTIONS
    ):
        errors.append("`order_dir` must be `asc` or `desc`")
    return errors
