"""Tests for schemadiff.comparator_reporter."""

import pytest
from schemadiff.core import ChangeType, TableDiff, ColumnDiff
from schemadiff.comparator_reporter import (
    render_comparator_text,
    render_comparator_markdown,
)


def _make_col_diff(name: str, change_type: ChangeType) -> ColumnDiff:
    return ColumnDiff(
        column_name=name,
        change_type=change_type,
        old_definition={"type": "int"} if change_type != ChangeType.ADDED else None,
        new_definition={"type": "varchar"} if change_type != ChangeType.DROPPED else None,
    )


@pytest.fixture
def added_table():
    return TableDiff(table_name="users", change_type=ChangeType.ADDED, column_diffs=[])


@pytest.fixture
def dropped_table():
    return TableDiff(table_name="legacy", change_type=ChangeType.DROPPED, column_diffs=[])


@pytest.fixture
def modified_table():
    return TableDiff(
        table_name="orders",
        change_type=ChangeType.MODIFIED,
        column_diffs=[
            _make_col_diff("status", ChangeType.MODIFIED),
            _make_col_diff("note", ChangeType.ADDED),
        ],
    )


def test_render_text_returns_string(added_table):
    result = render_comparator_text([added_table])
    assert isinstance(result, str)


def test_render_text_no_diffs_message():
    result = render_comparator_text([])
    assert "No differences found" in result


def test_render_text_contains_table_name(added_table):
    result = render_comparator_text([added_table])
    assert "users" in result


def test_render_text_added_symbol(added_table):
    result = render_comparator_text([added_table])
    assert "[+]" in result


def test_render_text_dropped_symbol(dropped_table):
    result = render_comparator_text([dropped_table])
    assert "[-]" in result


def test_render_text_modified_symbol(modified_table):
    result = render_comparator_text([modified_table])
    assert "[~]" in result


def test_render_text_contains_column_name(modified_table):
    result = render_comparator_text([modified_table])
    assert "status" in result
    assert "note" in result


def test_render_text_custom_title(added_table):
    result = render_comparator_text([added_table], title="My Report")
    assert "My Report" in result


def test_render_text_summary_line(added_table, dropped_table):
    result = render_comparator_text([added_table, dropped_table])
    assert "2 table change(s)" in result


def test_render_markdown_returns_string(added_table):
    result = render_comparator_markdown([added_table])
    assert isinstance(result, str)


def test_render_markdown_no_diffs_message():
    result = render_comparator_markdown([])
    assert "No differences found" in result


def test_render_markdown_contains_heading(added_table):
    result = render_comparator_markdown([added_table])
    assert result.startswith("# Schema Comparison")


def test_render_markdown_custom_title(added_table):
    result = render_comparator_markdown([added_table], title="Prod vs Staging")
    assert "# Prod vs Staging" in result


def test_render_markdown_table_row(added_table):
    result = render_comparator_markdown([added_table])
    assert "`users`" in result


def test_render_markdown_column_count(modified_table):
    result = render_comparator_markdown([modified_table])
    assert "2" in result
