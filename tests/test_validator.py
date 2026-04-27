"""Tests for schemadiff.validator."""

import pytest
from schemadiff.validator import validate_snapshot_dict, ValidationError


MINIMAL_VALID = {
    "tables": {
        "users": {
            "columns": {
                "id": {"type": "integer", "nullable": False},
                "name": {"type": "varchar(255)", "nullable": True},
            }
        }
    }
}


def test_valid_snapshot_passes():
    validate_snapshot_dict(MINIMAL_VALID, "test")


def test_empty_tables_passes():
    validate_snapshot_dict({"tables": {}}, "test")


def test_non_dict_raises():
    with pytest.raises(ValidationError, match="must be a JSON object"):
        validate_snapshot_dict(["not", "a", "dict"], "test")


def test_missing_tables_key_raises():
    with pytest.raises(ValidationError, match="missing required keys"):
        validate_snapshot_dict({}, "test")


def test_tables_not_dict_raises():
    with pytest.raises(ValidationError, match="'tables' must be an object"):
        validate_snapshot_dict({"tables": ["users"]}, "test")


def test_table_not_dict_raises():
    with pytest.raises(ValidationError, match="must be an object"):
        validate_snapshot_dict({"tables": {"users": "bad"}}, "test")


def test_columns_not_dict_raises():
    with pytest.raises(ValidationError, match="columns must be an object"):
        validate_snapshot_dict({"tables": {"users": {"columns": ["id"]}}}, "test")


def test_column_missing_type_raises():
    data = {"tables": {"users": {"columns": {"id": {"nullable": False}}}}}
    with pytest.raises(ValidationError, match="missing keys"):
        validate_snapshot_dict(data, "test")


def test_column_unknown_type_raises():
    data = {"tables": {"users": {"columns": {"id": {"type": "imaginary_type"}}}}}
    with pytest.raises(ValidationError, match="unknown type"):
        validate_snapshot_dict(data, "test")


def test_column_varchar_with_length_passes():
    data = {"tables": {"users": {"columns": {"name": {"type": "varchar(100)"}}}}}
    validate_snapshot_dict(data, "test")


def test_source_label_appears_in_error():
    with pytest.raises(ValidationError, match="my_source.json"):
        validate_snapshot_dict({}, "my_source.json")


def test_multiple_tables_all_validated():
    data = {
        "tables": {
            "users": {"columns": {"id": {"type": "integer"}}},
            "orders": {"columns": {"id": {"type": "bigint"}}},
        }
    }
    validate_snapshot_dict(data, "test")


def test_column_not_dict_raises():
    data = {"tables": {"users": {"columns": {"id": "integer"}}}}
    with pytest.raises(ValidationError, match="must be an object"):
        validate_snapshot_dict(data, "test")
