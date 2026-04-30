"""Tests for schemadiff.grouper module."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.grouper import (
    group_by_change_type,
    group_by_prefix,
    group_by_risk,
    group_summary,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def added_table():
    return TableDiff(table_name="orders", change_type=ChangeType.ADDED, column_diffs=[])


@pytest.fixture()
def dropped_table():
    return TableDiff(table_name="legacy_log", change_type=ChangeType.DROPPED, column_diffs=[])


@pytest.fixture()
def modified_type_change():
    col = ColumnDiff(column_name="price", old_type="int", new_type="decimal", old_nullable=True, new_nullable=True)
    return TableDiff(table_name="products", change_type=ChangeType.MODIFIED, column_diffs=[col])


@pytest.fixture()
def modified_dropped_col():
    col = ColumnDiff(column_name="notes", old_type="text", new_type=None, old_nullable=True, new_nullable=None)
    return TableDiff(table_name="users_profile", change_type=ChangeType.MODIFIED, column_diffs=[col])


@pytest.fixture()
def modified_nullable_tightened():
    col = ColumnDiff(column_name="email", old_type="varchar", new_type="varchar", old_nullable=True, new_nullable=False)
    return TableDiff(table_name="accounts", change_type=ChangeType.MODIFIED, column_diffs=[col])


@pytest.fixture()
def modified_additive():
    col = ColumnDiff(column_name="bio", old_type=None, new_type="text", old_nullable=None, new_nullable=True)
    return TableDiff(table_name="users_settings", change_type=ChangeType.MODIFIED, column_diffs=[col])


# ---------------------------------------------------------------------------
# group_by_change_type
# ---------------------------------------------------------------------------

def test_group_by_change_type_keys(added_table, dropped_table, modified_type_change):
    result = group_by_change_type([added_table, dropped_table, modified_type_change])
    assert "added" in result
    assert "dropped" in result
    assert "modified" in result


def test_group_by_change_type_counts(added_table, dropped_table, modified_type_change):
    result = group_by_change_type([added_table, dropped_table, modified_type_change])
    assert len(result["added"]) == 1
    assert len(result["dropped"]) == 1
    assert len(result["modified"]) == 1


def test_group_by_change_type_empty():
    result = group_by_change_type([])
    assert result == {}


# ---------------------------------------------------------------------------
# group_by_prefix
# ---------------------------------------------------------------------------

def test_group_by_prefix_groups_correctly(modified_dropped_col, modified_additive):
    result = group_by_prefix([modified_dropped_col, modified_additive])
    assert "users" in result
    assert len(result["users"]) == 2


def test_group_by_prefix_no_separator(added_table):
    # 'orders' has no underscore — should map to its own name
    result = group_by_prefix([added_table])
    assert "orders" in result


def test_group_by_prefix_custom_separator(added_table):
    result = group_by_prefix([added_table], separator="-")
    assert "orders" in result


# ---------------------------------------------------------------------------
# group_by_risk
# ---------------------------------------------------------------------------

def test_group_by_risk_dropped_is_high(dropped_table):
    result = group_by_risk([dropped_table])
    assert dropped_table in result["high"]


def test_group_by_risk_added_is_low(added_table):
    result = group_by_risk([added_table])
    assert added_table in result["low"]


def test_group_by_risk_type_change_is_high(modified_type_change):
    result = group_by_risk([modified_type_change])
    assert modified_type_change in result["high"]


def test_group_by_risk_dropped_col_is_medium(modified_dropped_col):
    result = group_by_risk([modified_dropped_col])
    assert modified_dropped_col in result["medium"]


def test_group_by_risk_nullable_tightened_is_high(modified_nullable_tightened):
    result = group_by_risk([modified_nullable_tightened])
    assert modified_nullable_tightened in result["high"]


def test_group_by_risk_additive_modified_is_low(modified_additive):
    result = group_by_risk([modified_additive])
    assert modified_additive in result["low"]


# ---------------------------------------------------------------------------
# group_summary
# ---------------------------------------------------------------------------

def test_group_summary_returns_counts(added_table, dropped_table):
    groups = group_by_change_type([added_table, dropped_table])
    summary = group_summary(groups)
    assert summary["added"] == 1
    assert summary["dropped"] == 1


def test_group_summary_empty():
    assert group_summary({}) == {}
