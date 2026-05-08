"""Tests for schemadiff.labeler."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.labeler import LabeledDiff, label_diff, label_diffs


def _col(name: str, change_type: ChangeType) -> ColumnDiff:
    return ColumnDiff(
        column_name=name,
        change_type=change_type,
        old_definition=None if change_type == ChangeType.ADDED else {"type": "int"},
        new_definition=None if change_type == ChangeType.DROPPED else {"type": "varchar"},
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
            _col("email", ChangeType.ADDED),
            _col("old_flag", ChangeType.DROPPED),
            _col("status", ChangeType.MODIFIED),
        ],
    )


def test_label_diff_returns_labeled_diff(added_table):
    result = label_diff(added_table)
    assert isinstance(result, LabeledDiff)


def test_label_added_table_label(added_table):
    result = label_diff(added_table)
    assert result.label == "CREATE TABLE"


def test_label_dropped_table_label(dropped_table):
    result = label_diff(dropped_table)
    assert result.label == "DROP TABLE"


def test_label_modified_table_contains_add_and_drop(modified_table):
    result = label_diff(modified_table)
    assert "ADD COLUMN" in result.label
    assert "DROP COLUMN" in result.label
    assert "ALTER COLUMN" in result.label


def test_intent_added_table_mentions_create(added_table):
    result = label_diff(added_table)
    assert "Create" in result.intent
    assert "orders" in result.intent


def test_intent_dropped_table_mentions_remove(dropped_table):
    result = label_diff(dropped_table)
    assert "Remove" in result.intent
    assert "legacy" in result.intent


def test_intent_modified_mentions_column_names(modified_table):
    result = label_diff(modified_table)
    assert "email" in result.intent
    assert "old_flag" in result.intent
    assert "status" in result.intent


def test_label_diffs_returns_list(added_table, dropped_table):
    results = label_diffs([added_table, dropped_table])
    assert isinstance(results, list)
    assert len(results) == 2


def test_label_diffs_empty_list():
    results = label_diffs([])
    assert results == []


def test_labeled_diff_repr(added_table):
    result = label_diff(added_table)
    r = repr(result)
    assert "orders" in r
    assert "CREATE TABLE" in r


def test_label_diff_stores_original_diff(added_table):
    result = label_diff(added_table)
    assert result.diff is added_table
