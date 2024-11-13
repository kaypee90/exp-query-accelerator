def validate_payload(payload):
    """
    Validates request to payload to match request schema

     Payload:
     {
      "table": "products",
      "fields": ["name", "price"],
      "filters": [
         {"field": "price", "value": "109", "operator": "="},
         {"field": "name", "value": "Rice", "operator": "=", "bind": "|"},
                 {"field": "price", "value": "1100", "operator": "=", "bind": "&"}
      ]
     }
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
        if not isinstance(filters, list):
            errors.append("`filters` must be a list")
        else:
            for key in filters:
                if not isinstance(key.get("field"), str):
                    errors.append("`filters` keys must be strings")
                    break
    return errors
