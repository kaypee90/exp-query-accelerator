import pytest

from src.validator import validate_payload


def valid_filter(**overrides):
    return {"field": "name", "operator": "=", "value": "Bread", **overrides}


class TestValidator:
    def test_validate_full_valid_payload(self):
        payload = {
            "table": "products",
            "fields": ["name", "price"],
            "filters": [valid_filter(), valid_filter(bind="|", value=10)],
            "order_by": "name",
            "order_dir": "DESC",
        }
        assert validate_payload(payload) == []

    @pytest.mark.parametrize("payload", [[], "products", 1, None])
    def test_validate_payload_that_is_not_an_object(self, payload):
        assert validate_payload(payload) == ["Payload must be a JSON object"]

    def test_validate_payload_without_table(self):
        errors = validate_payload({})
        assert errors[0] == "`table` is required"

    def test_validate_payload_with_unsafe_table(self):
        errors = validate_payload({"table": "users; DROP TABLE users"})
        assert errors == ["`table` must be a valid identifier"]

    def test_validate_payload_with_unknown_keys(self):
        errors = validate_payload({"table": "test", "limit": 1, "join": "x"})
        assert errors == ["Unknown keys: join, limit"]

    def test_validate_payload_with_non_list_fields(self):
        errors = validate_payload({"table": "test", "fields": "test"})
        assert errors[0] == "`fields` must be a list"

    def test_validate_payload_with_fields_with_list_not_containing_all_strings(self):
        errors = validate_payload({"table": "test", "fields": ["test", 1]})
        assert errors[0] == "`fields` must be a list of strings"

    def test_validate_payload_with_fields_with_list_containing_all_strings(self):
        errors = validate_payload({"table": "test", "fields": ["test", "test2"]})
        assert len(errors) == 0

    def test_validate_payload_with_unsafe_fields(self):
        errors = validate_payload({"table": "test", "fields": ["name", "1; --"]})
        assert errors == ["`fields` must contain valid identifiers"]

    def test_validate_payload_with_filters_not_list(self):
        errors = validate_payload({"table": "test", "filters": "test"})
        assert errors[0] == "`filters` must be a list"

    def test_validate_payload_with_filter_that_is_not_an_object(self):
        errors = validate_payload({"table": "test", "filters": ["name = 1"]})
        assert errors == ["`filters[0]` must be an object"]

    def test_validate_payload_with_filters_must_have_field_value_as_string(self):
        errors = validate_payload({"table": "test", "filters": [valid_filter(field=1)]})
        assert errors == ["`filters[0]`.field must be a string"]

    def test_validate_payload_with_unsafe_filter_field(self):
        errors = validate_payload(
            {"table": "test", "filters": [valid_filter(field="1=1 OR name")]}
        )
        assert errors == ["`filters[0]`.field must be a valid identifier"]

    @pytest.mark.parametrize("operator", [None, "", "IN", "= 1 OR 1 ="])
    def test_validate_payload_with_bad_operator(self, operator):
        errors = validate_payload(
            {"table": "test", "filters": [valid_filter(operator=operator)]}
        )
        assert errors == ["`filters[0]`.operator is missing or not supported"]

    def test_validate_payload_with_missing_value(self):
        item = valid_filter()
        del item["value"]
        errors = validate_payload({"table": "test", "filters": [item]})
        assert errors == ["`filters[0]`.value is required"]

    @pytest.mark.parametrize(
        "value", [None, [1, 2], {"a": 1}, float("nan"), float("inf")]
    )
    def test_validate_payload_with_invalid_value(self, value):
        errors = validate_payload(
            {"table": "test", "filters": [valid_filter(value=value)]}
        )
        assert errors == [
            "`filters[0]`.value must be a string, finite number or boolean"
        ]

    @pytest.mark.parametrize("bind", ["AND", [], {}, 1, None])
    def test_validate_payload_with_bad_bind(self, bind):
        errors = validate_payload(
            {"table": "test", "filters": [valid_filter(), valid_filter(bind=bind)]}
        )
        assert errors == ["`filters[1]`.bind must be one of: &, |"]

    def test_validate_payload_reports_errors_for_each_filter(self):
        errors = validate_payload(
            {"table": "test", "filters": [valid_filter(field=1), "bad"]}
        )
        assert errors == [
            "`filters[0]`.field must be a string",
            "`filters[1]` must be an object",
        ]

    @pytest.mark.parametrize("order_by", ["", 1, "name DESC; --"])
    def test_validate_payload_with_bad_order_by(self, order_by):
        errors = validate_payload({"table": "test", "order_by": order_by})
        assert errors == ["`order_by` must be a valid identifier"]

    @pytest.mark.parametrize("order_dir", ["up", 1, ""])
    def test_validate_payload_with_bad_order_dir(self, order_dir):
        errors = validate_payload(
            {"table": "test", "order_by": "name", "order_dir": order_dir}
        )
        assert errors == ["`order_dir` must be `asc` or `desc`"]
