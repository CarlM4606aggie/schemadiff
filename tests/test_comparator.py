"""Tests for the schemadiff.comparator module."""

import pytest
from schemadiff.comparator import compare_snapshots, _compare_columns
from schemadiff.core import ChangeType
from schemadiff.snapshot import SchemaSnapshot

FIXTURE_V1 = "tests/fixtures/snapshot_v1.json"
FIXTURE_V2 = "tests/fixtures/snapshot_v2.json"


@pytest.fixture
def snapshot_v1():
    return SchemaSnapshot.load(FIXTURE_V1)


@pytest.fixture
def snapshot_v2():
    return SchemaSnapshot.load(FIXTURE_V2)


def test_compare_returns_list(snapshot_v1, snapshot_v2):
    result = compare_snapshots(snapshot_v1, snapshot_v2)
    assert isinstance(result, list)


def test_added_table_detected():
    old = SchemaSnapshot(tables={"users": {"columns": {"id": "int"}}})
    new = SchemaSnapshot(tables={
        "users": {"columns": {"id": "int"}},
        "orders": {"columns": {"id": "int", "total": "decimal"}},
    })
    diffs = compare_snapshots(old, new)
    added = [d for d in diffs if d.change_type == ChangeType.ADDED]
    assert len(added) == 1
    assert added[0].table_name == "orders"


def test_dropped_table_detected():
    old = SchemaSnapshot(tables={
        "users": {"columns": {"id": "int"}},
        "sessions": {"columns": {"token": "varchar"}},
    })
    new = SchemaSnapshot(tables={"users": {"columns": {"id": "int"}}})
    diffs = compare_snapshots(old, new)
    dropped = [d for d in diffs if d.change_type == ChangeType.DROPPED]
    assert len(dropped) == 1
    assert dropped[0].table_name == "sessions"


def test_modified_table_detected():
    old = SchemaSnapshot(tables={"users": {"columns": {"id": "int", "name": "varchar"}}})
    new = SchemaSnapshot(tables={"users": {"columns": {"id": "int", "name": "text"}}})
    diffs = compare_snapshots(old, new)
    modified = [d for d in diffs if d.change_type == ChangeType.MODIFIED]
    assert len(modified) == 1
    assert modified[0].table_name == "users"


def test_no_changes_returns_empty():
    old = SchemaSnapshot(tables={"users": {"columns": {"id": "int"}}})
    new = SchemaSnapshot(tables={"users": {"columns": {"id": "int"}}})
    diffs = compare_snapshots(old, new)
    assert diffs == []


def test_column_added():
    old_table = {"columns": {"id": "int"}}
    new_table = {"columns": {"id": "int", "email": "varchar"}}
    col_diffs = _compare_columns(old_table, new_table)
    assert len(col_diffs) == 1
    assert col_diffs[0].name == "email"
    assert col_diffs[0].change_type == ChangeType.ADDED


def test_column_dropped():
    old_table = {"columns": {"id": "int", "legacy": "text"}}
    new_table = {"columns": {"id": "int"}}
    col_diffs = _compare_columns(old_table, new_table)
    assert len(col_diffs) == 1
    assert col_diffs[0].name == "legacy"
    assert col_diffs[0].change_type == ChangeType.DROPPED


def test_column_type_changed():
    old_table = {"columns": {"score": "int"}}
    new_table = {"columns": {"score": "float"}}
    col_diffs = _compare_columns(old_table, new_table)
    assert len(col_diffs) == 1
    assert col_diffs[0].change_type == ChangeType.MODIFIED
    assert col_diffs[0].old == "int"
    assert col_diffs[0].new == "float"
