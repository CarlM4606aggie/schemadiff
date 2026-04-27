"""Tests for schemadiff.filter module."""

import pytest
from schemadiff.core import TableDiff, ColumnDiff, ChangeType
from schemadiff.filter import filter_diffs, filter_by_pattern


@pytest.fixture
def sample_diffs():
    return [
        TableDiff(table_name="users", change_type=ChangeType.ADDED, column_diffs=[]),
        TableDiff(table_name="orders", change_type=ChangeType.MODIFIED, column_diffs=[
            ColumnDiff(column_name="status", change_type=ChangeType.ADDED, old_definition=None, new_definition="VARCHAR(50)")
        ]),
        TableDiff(table_name="products", change_type=ChangeType.DROPPED, column_diffs=[]),
        TableDiff(table_name="order_items", change_type=ChangeType.MODIFIED, column_diffs=[]),
    ]


def test_filter_by_table_names(sample_diffs):
    result = filter_diffs(sample_diffs, tables=["users", "products"])
    names = [d.table_name for d in result]
    assert names == ["users", "products"]


def test_filter_by_table_names_case_insensitive(sample_diffs):
    result = filter_diffs(sample_diffs, tables=["USERS", "Orders"])
    names = [d.table_name for d in result]
    assert "users" in names
    assert "orders" in names


def test_filter_by_change_type_added(sample_diffs):
    result = filter_diffs(sample_diffs, change_types=[ChangeType.ADDED])
    assert len(result) == 1
    assert result[0].table_name == "users"


def test_filter_by_change_type_modified(sample_diffs):
    result = filter_diffs(sample_diffs, change_types=[ChangeType.MODIFIED])
    assert len(result) == 2
    names = [d.table_name for d in result]
    assert "orders" in names
    assert "order_items" in names


def test_filter_by_change_type_dropped(sample_diffs):
    result = filter_diffs(sample_diffs, change_types=[ChangeType.DROPPED])
    assert len(result) == 1
    assert result[0].table_name == "products"


def test_filter_exclude_tables(sample_diffs):
    result = filter_diffs(sample_diffs, exclude_tables=["orders", "products"])
    names = [d.table_name for d in result]
    assert "orders" not in names
    assert "products" not in names
    assert len(result) == 2


def test_filter_combined_tables_and_change_type(sample_diffs):
    result = filter_diffs(sample_diffs, tables=["orders", "users"], change_types=[ChangeType.MODIFIED])
    assert len(result) == 1
    assert result[0].table_name == "orders"


def test_filter_no_criteria_returns_all(sample_diffs):
    result = filter_diffs(sample_diffs)
    assert len(result) == len(sample_diffs)


def test_filter_empty_diffs():
    result = filter_diffs([], tables=["users"], change_types=[ChangeType.ADDED])
    assert result == []


def test_filter_by_pattern_matches_substring(sample_diffs):
    result = filter_by_pattern(sample_diffs, "order")
    names = [d.table_name for d in result]
    assert "orders" in names
    assert "order_items" in names
    assert "users" not in names


def test_filter_by_pattern_case_insensitive(sample_diffs):
    result = filter_by_pattern(sample_diffs, "USER")
    assert len(result) == 1
    assert result[0].table_name == "users"


def test_filter_by_pattern_no_match(sample_diffs):
    result = filter_by_pattern(sample_diffs, "invoice")
    assert result == []
