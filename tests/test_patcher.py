"""Tests for schemadiff.patcher module."""

import pytest
from schemadiff.patcher import (
    _column_def,
    patch_for_column_diff,
    patch_for_table_diff,
    generate_patch,
)
from schemadiff.core import ChangeType, ColumnDiff, TableDiff


# --- Fixtures ---

@pytest.fixture
def added_col_diff():
    return ColumnDiff(
        column_name="email",
        change_type=ChangeType.ADDED,
        old_value=None,
        new_value={"type": "VARCHAR(255)", "nullable": False},
    )


@pytest.fixture
def dropped_col_diff():
    return ColumnDiff(
        column_name="legacy_field",
        change_type=ChangeType.DROPPED,
        old_value={"type": "TEXT", "nullable": True},
        new_value=None,
    )


@pytest.fixture
def modified_col_diff():
    return ColumnDiff(
        column_name="status",
        change_type=ChangeType.MODIFIED,
        old_value={"type": "VARCHAR(50)", "nullable": True},
        new_value={"type": "VARCHAR(100)", "nullable": False, "default": "'active'"},
    )


@pytest.fixture
def modified_table_diff(added_col_diff, dropped_col_diff):
    return TableDiff(
        table_name="users",
        change_type=ChangeType.MODIFIED,
        column_diffs=[added_col_diff, dropped_col_diff],
    )


@pytest.fixture
def dropped_table_diff():
    return TableDiff(
        table_name="old_logs",
        change_type=ChangeType.DROPPED,
        column_diffs=[],
    )


# --- Tests ---

def test_column_def_basic():
    result = _column_def({"type": "INTEGER", "nullable": False})
    assert "INTEGER" in result
    assert "NOT NULL" in result


def test_column_def_with_default():
    result = _column_def({"type": "TEXT", "nullable": True, "default": "''"})
    assert "DEFAULT" in result
    assert "NULL" in result


def test_patch_for_added_column(added_col_diff):
    stmt = patch_for_column_diff("users", added_col_diff)
    assert stmt.startswith("ALTER TABLE users ADD COLUMN email")
    assert "VARCHAR(255)" in stmt


def test_patch_for_dropped_column(dropped_col_diff):
    stmt = patch_for_column_diff("users", dropped_col_diff)
    assert "DROP COLUMN legacy_field" in stmt


def test_patch_for_modified_column(modified_col_diff):
    stmt = patch_for_column_diff("users", modified_col_diff)
    assert "MODIFY COLUMN status" in stmt
    assert "VARCHAR(100)" in stmt


def test_patch_for_dropped_table(dropped_table_diff):
    stmts = patch_for_table_diff(dropped_table_diff)
    assert any("DROP TABLE" in s for s in stmts)
    assert any("old_logs" in s for s in stmts)


def test_patch_for_added_table():
    diff = TableDiff(table_name="new_table", change_type=ChangeType.ADDED, column_diffs=[])
    stmts = patch_for_table_diff(diff)
    assert any("added" in s.lower() for s in stmts)


def test_patch_for_modified_table_includes_column_stmts(modified_table_diff):
    stmts = patch_for_table_diff(modified_table_diff)
    assert len(stmts) == 2
    assert any("ADD COLUMN" in s for s in stmts)
    assert any("DROP COLUMN" in s for s in stmts)


def test_generate_patch_returns_string(modified_table_diff, dropped_table_diff):
    result = generate_patch([modified_table_diff, dropped_table_diff])
    assert isinstance(result, str)
    assert "Auto-generated" in result
    assert "DROP TABLE" in result
    assert "ADD COLUMN" in result


def test_generate_patch_empty_diffs():
    result = generate_patch([])
    assert isinstance(result, str)
    assert "Auto-generated" in result
