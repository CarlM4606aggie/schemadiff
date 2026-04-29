"""Tests for schemadiff.linter module."""

import pytest
from schemadiff.linter import lint_diffs, LintResult, LintWarning
from schemadiff.core import TableDiff, ColumnDiff, ChangeType


@pytest.fixture
def dropped_table_diff():
    return TableDiff(
        table_name="orders",
        change_type=ChangeType.DROPPED,
        column_diffs=[]
    )


@pytest.fixture
def modified_table_with_dropped_col():
    return TableDiff(
        table_name="users",
        change_type=ChangeType.MODIFIED,
        column_diffs=[
            ColumnDiff(
                column_name="email",
                change_type=ChangeType.DROPPED,
                old_definition={"type": "varchar", "nullable": True},
                new_definition=None
            )
        ]
    )


@pytest.fixture
def modified_table_with_type_change():
    return TableDiff(
        table_name="products",
        change_type=ChangeType.MODIFIED,
        column_diffs=[
            ColumnDiff(
                column_name="price",
                change_type=ChangeType.MODIFIED,
                old_definition={"type": "integer", "nullable": True},
                new_definition={"type": "varchar", "nullable": True}
            )
        ]
    )


@pytest.fixture
def modified_table_nullable_to_not_null():
    return TableDiff(
        table_name="accounts",
        change_type=ChangeType.MODIFIED,
        column_diffs=[
            ColumnDiff(
                column_name="username",
                change_type=ChangeType.MODIFIED,
                old_definition={"type": "varchar", "nullable": True},
                new_definition={"type": "varchar", "nullable": False}
            )
        ]
    )


def test_lint_empty_diffs_returns_no_issues():
    result = lint_diffs([])
    assert isinstance(result, LintResult)
    assert not result.has_issues


def test_lint_dropped_table_produces_error(dropped_table_diff):
    result = lint_diffs([dropped_table_diff])
    assert result.has_issues
    assert result.error_count == 1
    assert any("Table dropped" in str(w) for w in result.warnings)


def test_lint_dropped_column_produces_error(modified_table_with_dropped_col):
    result = lint_diffs([modified_table_with_dropped_col])
    assert result.error_count >= 1
    assert any("Column dropped" in str(w) for w in result.warnings)


def test_lint_type_change_produces_error(modified_table_with_type_change):
    result = lint_diffs([modified_table_with_type_change])
    assert result.error_count >= 1
    assert any("type changed" in str(w) for w in result.warnings)


def test_lint_nullable_to_not_null_produces_warning(modified_table_nullable_to_not_null):
    result = lint_diffs([modified_table_nullable_to_not_null])
    assert result.warning_count >= 1
    assert any("NOT NULL" in str(w) for w in result.warnings)


def test_lint_result_str_no_issues():
    result = LintResult()
    assert str(result) == "No lint issues found."


def test_lint_result_str_with_warnings():
    result = LintResult(warnings=[
        LintWarning(table="t", column="c", message="Test warning", severity="warning")
    ])
    output = str(result)
    assert "[WARNING]" in output
    assert "0 error(s), 1 warning(s)" in output


def test_lint_warning_str_with_column():
    w = LintWarning(table="users", column="id", message="Something wrong", severity="error")
    assert str(w) == "[ERROR] users.id: Something wrong"


def test_lint_warning_str_without_column():
    w = LintWarning(table="users", column=None, message="Table issue", severity="warning")
    assert str(w) == "[WARNING] users: Table issue"
