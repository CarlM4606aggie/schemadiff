"""Tests for schemadiff.summarizer."""

import pytest
from schemadiff.core import TableDiff, ColumnDiff, ChangeType
from schemadiff.summarizer import summarize_diffs, summarize_to_dict


def _col(name: str, change_type: ChangeType) -> ColumnDiff:
    return ColumnDiff(column_name=name, change_type=change_type)


@pytest.fixture
def added_table():
    return TableDiff(table_name="users", change_type=ChangeType.ADDED, column_diffs=[])


@pytest.fixture
def dropped_table():
    return TableDiff(table_name="legacy", change_type=ChangeType.DROPPED, column_diffs=[])


@pytest.fixture
def modified_table():
    cols = [_col("email", ChangeType.ADDED), _col("age", ChangeType.MODIFIED)]
    return TableDiff(table_name="orders", change_type=ChangeType.MODIFIED, column_diffs=cols)


@pytest.fixture
def mixed_diffs(added_table, dropped_table, modified_table):
    return [added_table, dropped_table, modified_table]


def test_summarize_empty_diffs_returns_no_changes_message():
    result = summarize_diffs([])
    assert "No schema changes detected" in result


def test_summarize_returns_string(mixed_diffs):
    result = summarize_diffs(mixed_diffs)
    assert isinstance(result, str)


def test_summarize_contains_title(mixed_diffs):
    result = summarize_diffs(mixed_diffs, title="My Report")
    assert "My Report" in result


def test_summarize_contains_table_names(mixed_diffs):
    result = summarize_diffs(mixed_diffs)
    assert "users" in result
    assert "legacy" in result
    assert "orders" in result


def test_summarize_shows_change_type_labels(mixed_diffs):
    result = summarize_diffs(mixed_diffs)
    assert "Added" in result
    assert "Dropped" in result
    assert "Modified" in result


def test_summarize_shows_column_change_count(modified_table):
    result = summarize_diffs([modified_table])
    assert "2 column change(s)" in result


def test_summarize_to_dict_returns_dict(mixed_diffs):
    result = summarize_to_dict(mixed_diffs)
    assert isinstance(result, dict)


def test_summarize_to_dict_has_changes_true(mixed_diffs):
    result = summarize_to_dict(mixed_diffs)
    assert result["has_changes"] is True


def test_summarize_to_dict_has_changes_false():
    result = summarize_to_dict([])
    assert result["has_changes"] is False


def test_summarize_to_dict_tables_count(mixed_diffs):
    result = summarize_to_dict(mixed_diffs)
    assert len(result["tables"]) == 3


def test_summarize_to_dict_column_changes(modified_table):
    result = summarize_to_dict([modified_table])
    entry = result["tables"][0]
    assert entry["column_changes"] == 2


def test_summarize_to_dict_change_counts_keys(mixed_diffs):
    result = summarize_to_dict(mixed_diffs)
    counts = result["change_counts"]
    assert "added" in counts or "dropped" in counts or "modified" in counts
