def validate_payload(payload):
    """
    Validates request to payload to match request schema
    """
    errors = []
    if not payload.get("table"):
        errors.append("`table` is required")

    fields = payload.get("fields")
    if fields:
        if not isinstance(fields, list):
            errors.append("`fields` must be a list")
        else:
            for field in fields:
                if not isinstance(field, str):
                    errors.append("`fields` must be a list of strings")
                    break

    filters = payload.get("filters")
    if filters:
        if not isinstance(filters, dict):
            errors.append("`filters` must be a dict")
        else:
            for key in filters.keys():
                if not isinstance(key, str):
                    errors.append("`filters` keys must be strings")
                    break
    return errors
