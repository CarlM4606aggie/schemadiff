"""Tests for schemadiff.sorter module."""

import pytest
from schemadiff.sorter import sort_diffs, group_by_change_type, SORT_KEYS
from schemadiff.core import TableDiff, ColumnDiff, ChangeType


@pytest.fixture
def sample_diffs():
    return [
        TableDiff(
            table_name="zebra",
            change_type=ChangeType.MODIFIED,
            column_diffs=[
                ColumnDiff(column_name="id", change_type=ChangeType.ADDED),
                ColumnDiff(column_name="name", change_type=ChangeType.ADDED),
            ],
        ),
        TableDiff(
            table_name="alpha",
            change_type=ChangeType.ADDED,
            column_diffs=[],
        ),
        TableDiff(
            table_name="mango",
            change_type=ChangeType.DROPPED,
            column_diffs=[
                ColumnDiff(column_name="col1", change_type=ChangeType.DROPPED),
            ],
        ),
    ]


def test_sort_by_table_name(sample_diffs):
    result = sort_diffs(sample_diffs, by="table")
    names = [d.table_name for d in result]
    assert names == ["alpha", "mango", "zebra"]


def test_sort_by_table_name_reverse(sample_diffs):
    result = sort_diffs(sample_diffs, by="table", reverse=True)
    names = [d.table_name for d in result]
    assert names == ["zebra", "mango", "alpha"]


def test_sort_by_change_type(sample_diffs):
    result = sort_diffs(sample_diffs, by="change_type")
    types = [d.change_type for d in result]
    # Sorted by enum value string; order depends on ChangeType values
    assert types == sorted([d.change_type for d in sample_diffs], key=lambda c: c.value)


def test_sort_by_column_count(sample_diffs):
    result = sort_diffs(sample_diffs, by="column_count")
    counts = [len(d.column_diffs) for d in result]
    assert counts == sorted(counts)


def test_sort_does_not_mutate_original(sample_diffs):
    original_order = [d.table_name for d in sample_diffs]
    sort_diffs(sample_diffs, by="table")
    assert [d.table_name for d in sample_diffs] == original_order


def test_sort_invalid_key_raises(sample_diffs):
    with pytest.raises(ValueError, match="Unsupported sort key"):
        sort_diffs(sample_diffs, by="nonexistent")


def test_sort_empty_list():
    result = sort_diffs([], by="table")
    assert result == []


def test_group_by_change_type(sample_diffs):
    groups = group_by_change_type(sample_diffs)
    assert ChangeType.ADDED in groups
    assert ChangeType.DROPPED in groups
    assert ChangeType.MODIFIED in groups
    assert len(groups[ChangeType.ADDED]) == 1
    assert groups[ChangeType.ADDED][0].table_name == "alpha"


def test_group_by_change_type_excludes_empty_groups(sample_diffs):
    groups = group_by_change_type(sample_diffs)
    for ct, items in groups.items():
        assert len(items) > 0


def test_group_by_change_type_empty_input():
    groups = group_by_change_type([])
    assert groups == {}
