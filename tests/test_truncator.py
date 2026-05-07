"""Tests for schemadiff.truncator."""

import pytest

from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.truncator import TruncateResult, truncate_diffs, truncate_summary


def _make_diff(name: str, change_type: ChangeType = ChangeType.ADDED) -> TableDiff:
    return TableDiff(table_name=name, change_type=change_type, column_diffs=[])


@pytest.fixture()
def mixed_diffs():
    return [
        _make_diff("orders", ChangeType.ADDED),
        _make_diff("users", ChangeType.DROPPED),
        _make_diff("products", ChangeType.MODIFIED),
        _make_diff("sessions", ChangeType.ADDED),
        _make_diff("logs", ChangeType.DROPPED),
    ]


def test_truncate_returns_truncate_result(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=3)
    assert isinstance(result, TruncateResult)


def test_truncate_keeps_correct_count(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=3)
    assert len(result.diffs) == 3


def test_truncate_total_is_original_length(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=3)
    assert result.total == 5


def test_truncate_truncated_count(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=3)
    assert result.truncated == 2


def test_truncate_was_truncated_true(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=3)
    assert result.was_truncated is True


def test_truncate_was_truncated_false(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=10)
    assert result.was_truncated is False


def test_truncate_no_truncation_returns_all(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=10)
    assert len(result.diffs) == 5
    assert result.truncated == 0


def test_truncate_exact_limit(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=5)
    assert len(result.diffs) == 5
    assert result.truncated == 0


def test_truncate_limit_zero_returns_empty(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=0)
    assert result.diffs == []
    assert result.truncated == 5


def test_truncate_negative_limit_raises(mixed_diffs):
    with pytest.raises(ValueError, match="limit must be >= 0"):
        truncate_diffs(mixed_diffs, limit=-1)


def test_truncate_prefer_breaking_keeps_dropped_first(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=2, prefer_breaking=True)
    change_types = [d.change_type for d in result.diffs]
    assert ChangeType.DROPPED in change_types


def test_truncate_prefer_breaking_no_added_when_limit_small(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=2, prefer_breaking=True)
    change_types = [d.change_type for d in result.diffs]
    assert ChangeType.ADDED not in change_types


def test_truncate_repr_contains_total():
    r = TruncateResult(diffs=[], total=10, truncated=7, limit=3)
    assert "10" in repr(r)
    assert "7" in repr(r)


def test_truncate_summary_not_truncated(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=10)
    msg = truncate_summary(result)
    assert "all 5" in msg


def test_truncate_summary_truncated(mixed_diffs):
    result = truncate_diffs(mixed_diffs, limit=3)
    msg = truncate_summary(result)
    assert "2 truncated" in msg
    assert "limit=3" in msg
