"""Tests for schemadiff.pruner."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.pruner import PruneOptions, prune_diffs, prune_summary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _col(name: str, change: ChangeType = ChangeType.MODIFIED) -> ColumnDiff:
    return ColumnDiff(column_name=name, change_type=change, old_def=None, new_def=None)


def _make_diff(
    table: str,
    change: ChangeType = ChangeType.MODIFIED,
    col_changes: int = 0,
) -> TableDiff:
    cols = [_col(f"col_{i}") for i in range(col_changes)]
    return TableDiff(table_name=table, change_type=change, column_diffs=cols)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mixed_diffs():
    return [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.DROPPED),
        _make_diff("tmp_cache", ChangeType.MODIFIED, col_changes=2),
        _make_diff("tmp_session", ChangeType.ADDED),
        _make_diff("products", ChangeType.MODIFIED, col_changes=6),
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_prune_no_options_returns_all(mixed_diffs):
    result = prune_diffs(mixed_diffs, options=None)
    assert len(result) == len(mixed_diffs)


def test_prune_exclude_added(mixed_diffs):
    opts = PruneOptions(exclude_change_types=[ChangeType.ADDED])
    result = prune_diffs(mixed_diffs, opts)
    assert all(d.change_type != ChangeType.ADDED for d in result)


def test_prune_exclude_multiple_types(mixed_diffs):
    opts = PruneOptions(exclude_change_types=[ChangeType.ADDED, ChangeType.DROPPED])
    result = prune_diffs(mixed_diffs, opts)
    assert all(d.change_type == ChangeType.MODIFIED for d in result)


def test_prune_exclude_table_prefix(mixed_diffs):
    opts = PruneOptions(exclude_table_prefixes=["tmp_"])
    result = prune_diffs(mixed_diffs, opts)
    assert all(not d.table_name.startswith("tmp_") for d in result)


def test_prune_prefix_is_case_insensitive(mixed_diffs):
    opts = PruneOptions(exclude_table_prefixes=["TMP_"])
    result = prune_diffs(mixed_diffs, opts)
    assert all(not d.table_name.lower().startswith("tmp_") for d in result)


def test_prune_max_column_changes(mixed_diffs):
    opts = PruneOptions(max_column_changes=3)
    result = prune_diffs(mixed_diffs, opts)
    assert all(len(d.column_diffs) <= 3 for d in result)


def test_prune_keep_only_breaking(mixed_diffs):
    opts = PruneOptions(keep_only_breaking=True)
    result = prune_diffs(mixed_diffs, opts)
    # ADDED with no dropped/modified cols is not breaking
    assert all(d.change_type != ChangeType.ADDED for d in result)


def test_prune_empty_input():
    opts = PruneOptions(exclude_change_types=[ChangeType.DROPPED])
    assert prune_diffs([], opts) == []


def test_prune_summary_no_removal():
    diffs = [_make_diff("users")]
    msg = prune_summary(diffs, diffs)
    assert "no diffs were removed" in msg


def test_prune_summary_with_removal(mixed_diffs):
    opts = PruneOptions(exclude_change_types=[ChangeType.ADDED])
    pruned = prune_diffs(mixed_diffs, opts)
    msg = prune_summary(mixed_diffs, pruned)
    assert "removed" in msg
    assert str(len(pruned)) in msg


def test_prune_returns_new_list(mixed_diffs):
    result = prune_diffs(mixed_diffs, options=None)
    assert result is not mixed_diffs
