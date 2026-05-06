"""Tests for schemadiff.deduplicator."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.deduplicator import (
    DeduplicateResult,
    deduplicate,
    deduplicate_summary,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(table: str, change_type: ChangeType = ChangeType.ADDED) -> TableDiff:
    return TableDiff(
        table_name=table,
        change_type=change_type,
        column_diffs=[],
    )


# ---------------------------------------------------------------------------
# DeduplicateResult
# ---------------------------------------------------------------------------

def test_deduplicate_result_had_duplicates_true():
    result = DeduplicateResult(diffs=[], removed_count=3)
    assert result.had_duplicates is True


def test_deduplicate_result_had_duplicates_false():
    result = DeduplicateResult(diffs=[], removed_count=0)
    assert result.had_duplicates is False


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

def test_deduplicate_empty_list():
    result = deduplicate([])
    assert result.diffs == []
    assert result.removed_count == 0


def test_deduplicate_no_duplicates_returns_all():
    diffs = [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.DROPPED),
        _make_diff("products", ChangeType.MODIFIED),
    ]
    result = deduplicate(diffs)
    assert len(result.diffs) == 3
    assert result.removed_count == 0


def test_deduplicate_removes_exact_duplicate():
    diffs = [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("users", ChangeType.ADDED),
    ]
    result = deduplicate(diffs)
    assert len(result.diffs) == 1
    assert result.removed_count == 1


def test_deduplicate_keeps_first_occurrence():
    first = _make_diff("users", ChangeType.ADDED)
    second = _make_diff("users", ChangeType.ADDED)
    result = deduplicate([first, second])
    assert result.diffs[0] is first


def test_deduplicate_same_table_different_change_types_kept():
    diffs = [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("users", ChangeType.DROPPED),
    ]
    result = deduplicate(diffs)
    assert len(result.diffs) == 2
    assert result.removed_count == 0


def test_deduplicate_multiple_duplicates():
    diffs = [
        _make_diff("a", ChangeType.ADDED),
        _make_diff("a", ChangeType.ADDED),
        _make_diff("a", ChangeType.ADDED),
        _make_diff("b", ChangeType.DROPPED),
    ]
    result = deduplicate(diffs)
    assert len(result.diffs) == 2
    assert result.removed_count == 2


def test_deduplicate_returns_deduplicate_result_instance():
    result = deduplicate([_make_diff("x")])
    assert isinstance(result, DeduplicateResult)


# ---------------------------------------------------------------------------
# deduplicate_summary
# ---------------------------------------------------------------------------

def test_deduplicate_summary_returns_string():
    result = DeduplicateResult(diffs=[], removed_count=0)
    summary = deduplicate_summary(result)
    assert isinstance(summary, str)


def test_deduplicate_summary_no_duplicates_message():
    result = DeduplicateResult(diffs=[_make_diff("t")], removed_count=0)
    summary = deduplicate_summary(result)
    assert "No duplicates" in summary


def test_deduplicate_summary_contains_removed_count():
    result = DeduplicateResult(diffs=[_make_diff("t")], removed_count=4)
    summary = deduplicate_summary(result)
    assert "4" in summary
