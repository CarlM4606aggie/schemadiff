"""Tests for schemadiff.renderer module."""

import pytest
from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.renderer import (
    RenderOptions,
    render_diff_list,
    render_table_diff,
)


@pytest.fixture
def added_table():
    return TableDiff(
        table_name="users",
        change_type=ChangeType.ADDED,
        column_diffs=[
            ColumnDiff("id", ChangeType.ADDED, None, "INT PRIMARY KEY"),
            ColumnDiff("email", ChangeType.ADDED, None, "VARCHAR(255)"),
        ],
    )


@pytest.fixture
def dropped_table():
    return TableDiff(
        table_name="legacy",
        change_type=ChangeType.DROPPED,
        column_diffs=[],
    )


@pytest.fixture
def modified_table():
    return TableDiff(
        table_name="orders",
        change_type=ChangeType.MODIFIED,
        column_diffs=[
            ColumnDiff("status", ChangeType.MODIFIED, "VARCHAR(50)", "VARCHAR(100)"),
            ColumnDiff("note", ChangeType.ADDED, None, "TEXT"),
        ],
    )


def test_render_table_diff_returns_string(added_table):
    result = render_table_diff(added_table)
    assert isinstance(result, str)


def test_render_added_table_contains_symbol(added_table):
    result = render_table_diff(added_table)
    assert result.startswith("+")
    assert "users" in result
    assert "added" in result.lower()


def test_render_dropped_table_contains_minus(dropped_table):
    result = render_table_diff(dropped_table)
    assert result.startswith("-")
    assert "legacy" in result


def test_render_modified_shows_column_details(modified_table):
    result = render_table_diff(modified_table)
    assert "status" in result
    assert "VARCHAR(50)" in result
    assert "VARCHAR(100)" in result
    assert "note" in result


def test_render_hide_column_details(modified_table):
    opts = RenderOptions(show_column_details=False)
    result = render_table_diff(modified_table, opts)
    assert "status" not in result
    assert "orders" in result


def test_render_with_color_contains_ansi(added_table):
    opts = RenderOptions(use_color=True)
    result = render_table_diff(added_table, opts)
    assert "\033[" in result


def test_render_without_color_no_ansi(added_table):
    opts = RenderOptions(use_color=False)
    result = render_table_diff(added_table, opts)
    assert "\033[" not in result


def test_render_diff_list_empty():
    result = render_diff_list([])
    assert "No schema differences" in result


def test_render_diff_list_multiple(added_table, dropped_table, modified_table):
    diffs = [added_table, dropped_table, modified_table]
    result = render_diff_list(diffs)
    assert "users" in result
    assert "legacy" in result
    assert "orders" in result


def test_render_diff_list_separates_sections(added_table, dropped_table):
    result = render_diff_list([added_table, dropped_table])
    assert "\n\n" in result
