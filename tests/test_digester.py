"""Tests for schemadiff.digester."""

import pytest
from unittest.mock import MagicMock

from schemadiff.digester import (
    digest_snapshot,
    digest_diffs,
    digests_match,
    _snapshot_to_stable_dict,
    _diff_to_stable_dict,
)
from schemadiff.core import TableDiff, ColumnDiff, ChangeType


def _make_snapshot(tables: dict):
    snap = MagicMock()
    snap.table_names.return_value = list(tables.keys())
    snap.get_table.side_effect = lambda name: tables[name]
    return snap


def _make_table_diff(table_name, change_type=ChangeType.MODIFIED, col_diffs=None):
    diff = MagicMock(spec=TableDiff)
    diff.table_name = table_name
    diff.change_type = change_type
    diff.column_diffs = col_diffs or []
    return diff


def _make_col_diff(col_name, change_type=ChangeType.MODIFIED, old="int", new="bigint"):
    cd = MagicMock(spec=ColumnDiff)
    cd.column_name = col_name
    cd.change_type = change_type
    cd.old_definition = old
    cd.new_definition = new
    return cd


# --- digest_snapshot ---

def test_digest_snapshot_returns_string():
    snap = _make_snapshot({"users": {"columns": {"id": "int"}}})
    result = digest_snapshot(snap)
    assert isinstance(result, str)
    assert len(result) == 64  # sha256 hex


def test_digest_snapshot_identical_snapshots_same_hash():
    tables = {"orders": {"columns": {"id": "int", "total": "decimal"}}}
    snap_a = _make_snapshot(tables)
    snap_b = _make_snapshot(tables)
    assert digest_snapshot(snap_a) == digest_snapshot(snap_b)


def test_digest_snapshot_different_tables_differ():
    snap_a = _make_snapshot({"users": {"columns": {"id": "int"}}})
    snap_b = _make_snapshot({"products": {"columns": {"id": "int"}}})
    assert digest_snapshot(snap_a) != digest_snapshot(snap_b)


def test_digest_snapshot_md5_algorithm():
    snap = _make_snapshot({"t": {"columns": {"c": "varchar"}}})
    result = digest_snapshot(snap, algorithm="md5")
    assert len(result) == 32


def test_snapshot_to_stable_dict_sorted_keys():
    snap = _make_snapshot({
        "z_table": {"columns": {"b": "int", "a": "varchar"}},
        "a_table": {"columns": {"x": "text"}},
    })
    d = _snapshot_to_stable_dict(snap)
    keys = list(d["tables"].keys())
    assert keys == sorted(keys)


# --- digest_diffs ---

def test_digest_diffs_returns_string():
    diff = _make_table_diff("users")
    result = digest_diffs([diff])
    assert isinstance(result, str)
    assert len(result) == 64


def test_digest_diffs_empty_list():
    result = digest_diffs([])
    assert isinstance(result, str)
    assert len(result) > 0


def test_digest_diffs_order_independent():
    d1 = _make_table_diff("alpha", ChangeType.ADDED)
    d2 = _make_table_diff("beta", ChangeType.DROPPED)
    assert digest_diffs([d1, d2]) == digest_diffs([d2, d1])


def test_digest_diffs_column_change_affects_hash():
    cd = _make_col_diff("price", ChangeType.MODIFIED, old="int", new="bigint")
    d_with = _make_table_diff("orders", col_diffs=[cd])
    d_without = _make_table_diff("orders", col_diffs=[])
    assert digest_diffs([d_with]) != digest_diffs([d_without])


# --- digests_match ---

def test_digests_match_same():
    snap = _make_snapshot({"t": {"columns": {"id": "int"}}})
    h = digest_snapshot(snap)
    assert digests_match(h, h) is True


def test_digests_match_different():
    snap_a = _make_snapshot({"a": {"columns": {}}})
    snap_b = _make_snapshot({"b": {"columns": {}}})
    assert digests_match(digest_snapshot(snap_a), digest_snapshot(snap_b)) is False
