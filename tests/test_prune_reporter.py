"""Tests for schemadiff.prune_reporter."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.pruner import PruneOptions
from schemadiff.prune_reporter import render_prune_text, render_prune_markdown


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(table: str, change: ChangeType = ChangeType.MODIFIED) -> TableDiff:
    return TableDiff(table_name=table, change_type=change, column_diffs=[])


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_diffs():
    return [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.DROPPED),
        _make_diff("products", ChangeType.MODIFIED),
    ]


@pytest.fixture()
def exclude_added_opts():
    return PruneOptions(exclude_change_types=[ChangeType.ADDED])


# ---------------------------------------------------------------------------
# render_prune_text
# ---------------------------------------------------------------------------

def test_render_text_returns_string(sample_diffs, exclude_added_opts):
    result = render_prune_text(sample_diffs, exclude_added_opts)
    assert isinstance(result, str)


def test_render_text_contains_header(sample_diffs, exclude_added_opts):
    result = render_prune_text(sample_diffs, exclude_added_opts)
    assert "Prune Report" in result


def test_render_text_lists_removed_table(sample_diffs, exclude_added_opts):
    result = render_prune_text(sample_diffs, exclude_added_opts)
    assert "users" in result


def test_render_text_retained_tables_present(sample_diffs, exclude_added_opts):
    result = render_prune_text(sample_diffs, exclude_added_opts)
    assert "orders" in result
    assert "products" in result


def test_render_text_no_removal_message(sample_diffs):
    opts = PruneOptions()  # no exclusions
    result = render_prune_text(sample_diffs, opts)
    assert "No diffs were removed" in result


def test_render_text_all_pruned_shows_none():
    diffs = [_make_diff("tmp_x", ChangeType.ADDED)]
    opts = PruneOptions(exclude_change_types=[ChangeType.ADDED])
    result = render_prune_text(diffs, opts)
    assert "(none)" in result


# ---------------------------------------------------------------------------
# render_prune_markdown
# ---------------------------------------------------------------------------

def test_render_markdown_returns_string(sample_diffs, exclude_added_opts):
    result = render_prune_markdown(sample_diffs, exclude_added_opts)
    assert isinstance(result, str)


def test_render_markdown_contains_heading(sample_diffs, exclude_added_opts):
    result = render_prune_markdown(sample_diffs, exclude_added_opts)
    assert "## Prune Report" in result


def test_render_markdown_removed_section(sample_diffs, exclude_added_opts):
    result = render_prune_markdown(sample_diffs, exclude_added_opts)
    assert "### Removed" in result
    assert "`users`" in result


def test_render_markdown_retained_section(sample_diffs, exclude_added_opts):
    result = render_prune_markdown(sample_diffs, exclude_added_opts)
    assert "### Retained" in result
    assert "`orders`" in result


def test_render_markdown_no_retained_shows_placeholder():
    diffs = [_make_diff("gone", ChangeType.DROPPED)]
    opts = PruneOptions(exclude_change_types=[ChangeType.DROPPED])
    result = render_prune_markdown(diffs, opts)
    assert "_No diffs retained._" in result


def test_render_markdown_summary_line_present(sample_diffs, exclude_added_opts):
    result = render_prune_markdown(sample_diffs, exclude_added_opts)
    assert "removed" in result.lower() or "no diffs" in result.lower()
