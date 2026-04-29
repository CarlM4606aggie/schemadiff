"""Tests for schemadiff.merger."""

import pytest
from schemadiff.snapshot import SchemaSnapshot
from schemadiff.merger import merge_snapshots


def _make_snapshot(*table_names: str) -> SchemaSnapshot:
    """Helper: build a minimal SchemaSnapshot with the given table names."""
    tables = {
        name: {
            "columns": {
                "id": {"type": "integer", "nullable": False}
            }
        }
        for name in table_names
    }
    return SchemaSnapshot({"tables": tables})


# ---------------------------------------------------------------------------
# Basic merge behaviour
# ---------------------------------------------------------------------------

def test_merge_disjoint_snapshots_contains_all_tables():
    a = _make_snapshot("users", "orders")
    b = _make_snapshot("products", "invoices")
    merged = merge_snapshots(a, b)
    assert set(merged.table_names()) == {"users", "orders", "products", "invoices"}


def test_merge_returns_schema_snapshot_instance():
    a = _make_snapshot("users")
    b = _make_snapshot("orders")
    result = merge_snapshots(a, b)
    assert isinstance(result, SchemaSnapshot)


def test_merge_empty_base_returns_override_tables():
    a = _make_snapshot()
    b = _make_snapshot("products")
    merged = merge_snapshots(a, b)
    assert merged.table_names() == ["products"]


def test_merge_empty_override_returns_base_tables():
    a = _make_snapshot("users")
    b = _make_snapshot()
    merged = merge_snapshots(a, b)
    assert merged.table_names() == ["users"]


# ---------------------------------------------------------------------------
# Conflict strategies
# ---------------------------------------------------------------------------

def test_conflict_override_uses_override_table():
    a = SchemaSnapshot({"tables": {"users": {"columns": {"id": {"type": "integer", "nullable": False}}}}})
    b = SchemaSnapshot({"tables": {"users": {"columns": {"id": {"type": "bigint", "nullable": False}}}}})
    merged = merge_snapshots(a, b, conflict="override")
    assert merged.get_table("users")["columns"]["id"]["type"] == "bigint"


def test_conflict_keep_preserves_base_table():
    a = SchemaSnapshot({"tables": {"users": {"columns": {"id": {"type": "integer", "nullable": False}}}}})
    b = SchemaSnapshot({"tables": {"users": {"columns": {"id": {"type": "bigint", "nullable": False}}}}})
    merged = merge_snapshots(a, b, conflict="keep")
    assert merged.get_table("users")["columns"]["id"]["type"] == "integer"


def test_conflict_error_raises_on_collision():
    a = _make_snapshot("users")
    b = _make_snapshot("users")
    with pytest.raises(ValueError, match="collision"):
        merge_snapshots(a, b, conflict="error")


def test_conflict_error_no_collision_succeeds():
    a = _make_snapshot("users")
    b = _make_snapshot("orders")
    merged = merge_snapshots(a, b, conflict="error")
    assert set(merged.table_names()) == {"users", "orders"}


def test_unknown_conflict_strategy_raises():
    a = _make_snapshot("users")
    b = _make_snapshot("orders")
    with pytest.raises(ValueError, match="Unknown conflict strategy"):
        merge_snapshots(a, b, conflict="invalid")
