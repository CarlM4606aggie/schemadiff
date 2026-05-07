"""Tests for schemadiff.flattener."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.flattener import FlatDiffRecord, flatten_diff, flatten_diffs


def _col(name, change_type, old_type=None, new_type=None, old_nullable=True, new_nullable=True):
    return ColumnDiff(
        column_name=name,
        change_type=change_type,
        old_type=old_type,
        new_type=new_type,
        old_nullable=old_nullable,
        new_nullable=new_nullable,
    )


@pytest.fixture
def added_table():
    return TableDiff(table_name="orders", change_type=ChangeType.ADDED, column_diffs=[])


@pytest.fixture
def dropped_table():
    return TableDiff(table_name="legacy", change_type=ChangeType.DROPPED, column_diffs=[])


@pytest.fixture
def modified_table():
    return TableDiff(
        table_name="users",
        change_type=ChangeType.MODIFIED,
        column_diffs=[
            _col("email", ChangeType.ADDED, new_type="varchar", new_nullable=True),
            _col("age", ChangeType.DROPPED, old_type="int", old_nullable=False),
            _col("name", ChangeType.MODIFIED, old_type="varchar", new_type="text", old_nullable=True, new_nullable=False),
        ],
    )


def test_flatten_added_table_returns_one_record(added_table):
    records = flatten_diff(added_table)
    assert len(records) == 1


def test_flatten_added_table_label(added_table):
    record = flatten_diff(added_table)[0]
    assert "Added" in record.label
    assert "orders" in record.label


def test_flatten_dropped_table_returns_one_record(dropped_table):
    records = flatten_diff(dropped_table)
    assert len(records) == 1


def test_flatten_dropped_table_label(dropped_table):
    record = flatten_diff(dropped_table)[0]
    assert "Dropped" in record.label
    assert "legacy" in record.label


def test_flatten_added_table_has_no_column(added_table):
    record = flatten_diff(added_table)[0]
    assert record.column_name is None
    assert record.column_change is None


def test_flatten_modified_table_expands_columns(modified_table):
    records = flatten_diff(modified_table)
    assert len(records) == 3


def test_flatten_modified_column_added_label(modified_table):
    records = flatten_diff(modified_table)
    added = next(r for r in records if r.column_name == "email")
    assert "Added column" in added.label
    assert "users" in added.label


def test_flatten_modified_column_dropped_label(modified_table):
    records = flatten_diff(modified_table)
    dropped = next(r for r in records if r.column_name == "age")
    assert "Dropped column" in dropped.label


def test_flatten_modified_column_modified_label(modified_table):
    records = flatten_diff(modified_table)
    modified = next(r for r in records if r.column_name == "name")
    assert "Modified column" in modified.label
    assert "varchar" in modified.column_change
    assert "text" in modified.column_change


def test_flatten_diffs_aggregates_all(added_table, dropped_table, modified_table):
    records = flatten_diffs([added_table, dropped_table, modified_table])
    assert len(records) == 5  # 1 + 1 + 3


def test_flat_diff_record_to_dict_has_required_keys(added_table):
    record = flatten_diff(added_table)[0]
    d = record.to_dict()
    assert "table" in d
    assert "change_type" in d
    assert "label" in d
    assert "column" in d
    assert "column_change" in d


def test_flatten_empty_list_returns_empty():
    assert flatten_diffs([]) == []
