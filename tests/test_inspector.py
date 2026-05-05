"""Tests for schemadiff.inspector."""

import pytest
from unittest.mock import MagicMock

from schemadiff.inspector import (
    InspectionReport,
    TableInspection,
    _inspect_table,
    inspect_snapshot,
)


def _make_snapshot(tables: dict):
    snap = MagicMock()
    snap.table_names.return_value = list(tables.keys())
    snap.get_table.side_effect = lambda name: tables.get(name)
    return snap


_USERS_TABLE = {
    "columns": {
        "id": {"type": "integer", "nullable": False},
        "email": {"type": "varchar", "nullable": False},
        "bio": {"type": "text", "nullable": True},
    }
}

_ORDERS_TABLE = {
    "columns": {
        "id": {"type": "integer", "nullable": False},
        "amount": {"type": "numeric", "nullable": True},
    }
}


def test_inspect_table_column_count():
    insp = _inspect_table("users", _USERS_TABLE)
    assert insp.column_count == 3


def test_inspect_table_nullable_columns():
    insp = _inspect_table("users", _USERS_TABLE)
    assert "bio" in insp.nullable_columns
    assert "id" not in insp.nullable_columns


def test_inspect_table_non_nullable_columns():
    insp = _inspect_table("users", _USERS_TABLE)
    assert "id" in insp.non_nullable_columns
    assert "email" in insp.non_nullable_columns


def test_inspect_table_unique_types():
    insp = _inspect_table("users", _USERS_TABLE)
    assert set(insp.unique_types) == {"integer", "varchar", "text"}


def test_nullable_ratio_calculation():
    insp = _inspect_table("users", _USERS_TABLE)
    assert abs(insp.nullable_ratio - 1 / 3) < 1e-6


def test_nullable_ratio_zero_columns():
    insp = _inspect_table("empty", {"columns": {}})
    assert insp.nullable_ratio == 0.0


def test_inspect_snapshot_table_count():
    snap = _make_snapshot({"users": _USERS_TABLE, "orders": _ORDERS_TABLE})
    report = inspect_snapshot(snap)
    assert report.table_count == 2


def test_inspect_snapshot_total_columns():
    snap = _make_snapshot({"users": _USERS_TABLE, "orders": _ORDERS_TABLE})
    report = inspect_snapshot(snap)
    assert report.total_columns == 5


def test_widest_table():
    snap = _make_snapshot({"users": _USERS_TABLE, "orders": _ORDERS_TABLE})
    report = inspect_snapshot(snap)
    assert report.widest_table() == "users"


def test_widest_table_empty_report():
    report = InspectionReport(table_count=0, total_columns=0)
    assert report.widest_table() is None


def test_tables_with_no_nullable_columns():
    strict_table = {
        "columns": {
            "id": {"type": "integer", "nullable": False},
        }
    }
    snap = _make_snapshot({"users": _USERS_TABLE, "strict": strict_table})
    report = inspect_snapshot(snap)
    assert "strict" in report.tables_with_no_nullable_columns()
    assert "users" not in report.tables_with_no_nullable_columns()


def test_all_column_types_sorted():
    snap = _make_snapshot({"users": _USERS_TABLE, "orders": _ORDERS_TABLE})
    report = inspect_snapshot(snap)
    types = report.all_column_types()
    assert types == sorted(types)
    assert "numeric" in types
    assert "varchar" in types
