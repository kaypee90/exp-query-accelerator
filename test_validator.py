from validator import validate_payload


def test_validate_payload_without_table():
    errors = validate_payload({})
    assert errors[0] == "`table` is required"


def test_validate_payload_with_non_list_fields():
    errors = validate_payload({"table": "test", "fields": "test"})
    assert errors[0] == "`fields` must be a list"


def test_validate_payload_with_fields_with_list_not_containing_all_strings():
    errors = validate_payload({"table": "test", "fields": ["test", 1]})
    assert errors[0] == "`fields` must be a list of strings"


def test_validate_payload_with_fields_with_list_containing_all_strings():
    errors = validate_payload({"table": "test", "fields": ["test", "test2"]})
    assert len(errors) == 0


def test_validate_payload_with_filters_not_dict():
    errors = validate_payload({"table": "test", "filters": "test"})
    assert errors[0] == "`filters` must be a dict"


def test_validate_payload_with_filters_must_have_string_keys():
    errors = validate_payload({"table": "test", "filters": {1: "test"}})
    assert errors[0] == "`filters` keys must be strings"
