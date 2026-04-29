"""Tests for schemadiff.scorer."""

import pytest
from schemadiff.core import ChangeType, TableDiff, ColumnDiff
from schemadiff.scorer import DiffScore, score_table_diff, score_diffs, total_score


@pytest.fixture
def added_table_diff():
    return TableDiff(
        table_name="users",
        change_type=ChangeType.ADDED,
        column_diffs=[],
    )


@pytest.fixture
def dropped_table_diff():
    return TableDiff(
        table_name="legacy_log",
        change_type=ChangeType.DROPPED,
        column_diffs=[],
    )


@pytest.fixture
def modified_table_with_nullable_change():
    col = ColumnDiff(
        column_name="email",
        change_type=ChangeType.MODIFIED,
        old_definition={"type": "varchar", "nullable": True},
        new_definition={"type": "varchar", "nullable": False},
    )
    return TableDiff(
        table_name="accounts",
        change_type=ChangeType.MODIFIED,
        column_diffs=[col],
    )


def test_score_table_diff_returns_diff_score(added_table_diff):
    result = score_table_diff(added_table_diff)
    assert isinstance(result, DiffScore)


def test_added_table_has_lower_score_than_dropped(added_table_diff, dropped_table_diff):
    added_score = score_table_diff(added_table_diff)
    dropped_score = score_table_diff(dropped_table_diff)
    assert dropped_score.score > added_score.score


def test_score_includes_reasons(added_table_diff):
    result = score_table_diff(added_table_diff)
    assert len(result.reasons) >= 1
    assert any("added" in r for r in result.reasons)


def test_nullable_to_not_null_adds_penalty(modified_table_with_nullable_change):
    result = score_table_diff(modified_table_with_nullable_change)
    assert any("nullable→not-null" in r for r in result.reasons)
    # base modified table (5) + modified col (4) + nullable penalty (3) = 12
    assert result.score == 12


def test_score_diffs_returns_sorted_list(added_table_diff, dropped_table_diff):
    scores = score_diffs([added_table_diff, dropped_table_diff])
    assert scores[0].score >= scores[1].score


def test_score_diffs_table_names_preserved(added_table_diff, dropped_table_diff):
    scores = score_diffs([added_table_diff, dropped_table_diff])
    names = {s.table_name for s in scores}
    assert names == {"users", "legacy_log"}


def test_total_score_sums_all(added_table_diff, dropped_table_diff):
    result = total_score([added_table_diff, dropped_table_diff])
    individual = sum(
        score_table_diff(d).score for d in [added_table_diff, dropped_table_diff]
    )
    assert result == individual


def test_total_score_empty_list():
    assert total_score([]) == 0


def test_diff_score_repr(added_table_diff):
    score = score_table_diff(added_table_diff)
    assert "users" in repr(score)
    assert "score" in repr(score)
