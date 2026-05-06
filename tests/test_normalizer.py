"""Tests for schemadiff.normalizer."""

import pytest

from schemadiff.normalizer import normalize_type, normalize_column, normalize_snapshot
from schemadiff.snapshot import SchemaSnapshot


# ---------------------------------------------------------------------------
# normalize_type
# ---------------------------------------------------------------------------

def test_normalize_type_int_alias():
    assert normalize_type("int") == "integer"


def test_normalize_type_int4_alias():
    assert normalize_type("int4") == "integer"


def test_normalize_type_varchar_with_size():
    # varchar(255) should map to character varying
    assert normalize_type("varchar(255)") == "character varying"


def test_normalize_type_bool_alias():
    assert normalize_type("bool") == "boolean"


def test_normalize_type_unknown_passthrough():
    assert normalize_type("jsonb") == "jsonb"


def test_normalize_type_strips_whitespace():
    assert normalize_type("  bigint  ") == "bigint"


def test_normalize_type_lowercases():
    assert normalize_type("INT") == "integer"


# ---------------------------------------------------------------------------
# normalize_column
# ---------------------------------------------------------------------------

def test_normalize_column_type_is_normalised():
    col = {"type": "int", "nullable": True}
    result = normalize_column(col)
    assert result["type"] == "integer"


def test_normalize_column_nullable_is_bool():
    col = {"type": "text", "nullable": 1}
    result = normalize_column(col)
    assert result["nullable"] is True


def test_normalize_column_default_preserved():
    col = {"type": "integer", "nullable": False, "default": "0"}
    result = normalize_column(col)
    assert result["default"] == "0"


def test_normalize_column_missing_default_is_none():
    col = {"type": "text", "nullable": True}
    result = normalize_column(col)
    assert result["default"] is None


# ---------------------------------------------------------------------------
# normalize_snapshot
# ---------------------------------------------------------------------------

def _make_snapshot(tables: dict) -> SchemaSnapshot:
    return SchemaSnapshot({"tables": tables})


def test_normalize_snapshot_returns_schema_snapshot():
    snap = _make_snapshot({"users": {"id": {"type": "int", "nullable": False}}})
    result = normalize_snapshot(snap)
    assert isinstance(result, SchemaSnapshot)


def test_normalize_snapshot_does_not_mutate_original():
    snap = _make_snapshot({"users": {"id": {"type": "int", "nullable": False}}})
    normalize_snapshot(snap)
    original_col = snap.get_table("users")["id"]
    assert original_col["type"] == "int"  # unchanged


def test_normalize_snapshot_column_types_are_canonical():
    snap = _make_snapshot({
        "orders": {
            "order_id": {"type": "int4", "nullable": False},
            "note": {"type": "varchar(500)", "nullable": True},
        }
    })
    result = normalize_snapshot(snap)
    table = result.get_table("orders")
    assert table["order_id"]["type"] == "integer"
    assert table["note"]["type"] == "character varying"


def test_normalize_snapshot_preserves_table_names():
    snap = _make_snapshot({
        "alpha": {"x": {"type": "bool", "nullable": True}},
        "beta": {"y": {"type": "int8", "nullable": False}},
    })
    result = normalize_snapshot(snap)
    assert set(result.table_names()) == {"alpha", "beta"}
