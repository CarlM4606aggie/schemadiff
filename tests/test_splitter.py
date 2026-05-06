"""Tests for schemadiff.splitter."""

import pytest

from schemadiff.core import ChangeType, TableDiff
from schemadiff.splitter import (
    DiffBatch,
    split_by_change_type,
    split_by_prefix,
    split_by_size,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(table_name: str, change_type: ChangeType) -> TableDiff:
    return TableDiff(table_name=table_name, change_type=change_type, column_diffs=[])


@pytest.fixture()
def mixed_diffs():
    return [
        _make_diff("orders", ChangeType.ADDED),
        _make_diff("users", ChangeType.MODIFIED),
        _make_diff("sessions", ChangeType.DROPPED),
        _make_diff("products", ChangeType.ADDED),
        _make_diff("audit_log", ChangeType.MODIFIED),
    ]


# ---------------------------------------------------------------------------
# DiffBatch
# ---------------------------------------------------------------------------

def test_diff_batch_len():
    batch = DiffBatch(name="test", diffs=[_make_diff("t", ChangeType.ADDED)])
    assert len(batch) == 1


def test_diff_batch_is_empty_true():
    assert DiffBatch(name="empty").is_empty()


def test_diff_batch_is_empty_false():
    batch = DiffBatch(name="x", diffs=[_make_diff("t", ChangeType.DROPPED)])
    assert not batch.is_empty()


def test_diff_batch_repr_contains_name():
    batch = DiffBatch(name="stage1")
    assert "stage1" in repr(batch)


# ---------------------------------------------------------------------------
# split_by_change_type
# ---------------------------------------------------------------------------

def test_split_by_change_type_returns_list(mixed_diffs):
    result = split_by_change_type(mixed_diffs)
    assert isinstance(result, list)


def test_split_by_change_type_order(mixed_diffs):
    result = split_by_change_type(mixed_diffs)
    names = [b.name for b in result]
    assert names == [ChangeType.ADDED.value, ChangeType.MODIFIED.value, ChangeType.DROPPED.value]


def test_split_by_change_type_counts(mixed_diffs):
    result = split_by_change_type(mixed_diffs)
    by_name = {b.name: len(b) for b in result}
    assert by_name[ChangeType.ADDED.value] == 2
    assert by_name[ChangeType.MODIFIED.value] == 2
    assert by_name[ChangeType.DROPPED.value] == 1


def test_split_by_change_type_empty_input():
    assert split_by_change_type([]) == []


def test_split_by_change_type_omits_empty_batches():
    diffs = [_make_diff("t", ChangeType.ADDED)]
    result = split_by_change_type(diffs)
    names = [b.name for b in result]
    assert ChangeType.DROPPED.value not in names


# ---------------------------------------------------------------------------
# split_by_size
# ---------------------------------------------------------------------------

def test_split_by_size_returns_correct_batch_count(mixed_diffs):
    result = split_by_size(mixed_diffs, batch_size=2)
    assert len(result) == 3  # 2 + 2 + 1


def test_split_by_size_last_batch_may_be_smaller(mixed_diffs):
    result = split_by_size(mixed_diffs, batch_size=2)
    assert len(result[-1]) == 1


def test_split_by_size_batch_names_sequential(mixed_diffs):
    result = split_by_size(mixed_diffs, batch_size=2)
    assert result[0].name == "batch_1"
    assert result[1].name == "batch_2"


def test_split_by_size_invalid_raises():
    with pytest.raises(ValueError):
        split_by_size([], batch_size=0)


def test_split_by_size_empty_input():
    assert split_by_size([], batch_size=5) == []


# ---------------------------------------------------------------------------
# split_by_prefix
# ---------------------------------------------------------------------------

def test_split_by_prefix_groups_correctly():
    diffs = [
        _make_diff("auth_users", ChangeType.ADDED),
        _make_diff("auth_roles", ChangeType.ADDED),
        _make_diff("billing_invoices", ChangeType.MODIFIED),
        _make_diff("orders", ChangeType.DROPPED),
    ]
    result = split_by_prefix(diffs)
    by_name = {b.name: len(b) for b in result}
    assert by_name["auth"] == 2
    assert by_name["billing"] == 1
    assert by_name["default"] == 1


def test_split_by_prefix_sorted_names():
    diffs = [
        _make_diff("z_table", ChangeType.ADDED),
        _make_diff("a_table", ChangeType.DROPPED),
    ]
    result = split_by_prefix(diffs)
    assert result[0].name == "a"
    assert result[1].name == "z"


def test_split_by_prefix_custom_delimiter():
    diffs = [
        _make_diff("ns.users", ChangeType.ADDED),
        _make_diff("ns.orders", ChangeType.ADDED),
    ]
    result = split_by_prefix(diffs, delimiter=".")
    assert len(result) == 1
    assert result[0].name == "ns"
