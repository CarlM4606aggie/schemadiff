"""Tests for schemadiff.score_pipeline."""

import pytest
from unittest.mock import patch, MagicMock

from schemadiff.core import ChangeType, TableDiff
from schemadiff.scorer import DiffScore
from schemadiff.score_pipeline import ScorePipelineResult, run_score_pipeline


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

def _make_table_diff(name: str, change_type: ChangeType = ChangeType.ADDED) -> TableDiff:
    return TableDiff(table_name=name, change_type=change_type, column_diffs=[])


@pytest.fixture
def mixed_diffs():
    return [
        _make_table_diff("users", ChangeType.ADDED),
        _make_table_diff("orders", ChangeType.DROPPED),
        _make_table_diff("products", ChangeType.MODIFIED),
    ]


# ---------------------------------------------------------------------------
# ScorePipelineResult
# ---------------------------------------------------------------------------

def test_is_high_risk_true():
    result = ScorePipelineResult(
        diffs=[], scores=[], total_score=10,
        report_text="", report_markdown="",
    )
    assert result.is_high_risk(threshold=8) is True


def test_is_high_risk_false():
    result = ScorePipelineResult(
        diffs=[], scores=[], total_score=3,
        report_text="", report_markdown="",
    )
    assert result.is_high_risk(threshold=8) is False


def test_is_high_risk_default_threshold():
    result = ScorePipelineResult(
        diffs=[], scores=[], total_score=8,
        report_text="", report_markdown="",
    )
    assert result.is_high_risk() is True


# ---------------------------------------------------------------------------
# run_score_pipeline
# ---------------------------------------------------------------------------

def test_run_score_pipeline_returns_result_instance(mixed_diffs):
    result = run_score_pipeline(mixed_diffs)
    assert isinstance(result, ScorePipelineResult)


def test_run_score_pipeline_scores_count_matches_diffs(mixed_diffs):
    result = run_score_pipeline(mixed_diffs)
    assert len(result.scores) == len(mixed_diffs)


def test_run_score_pipeline_total_score_is_sum(mixed_diffs):
    result = run_score_pipeline(mixed_diffs)
    expected = sum(s.score for s in result.scores)
    assert result.total_score == expected


def test_run_score_pipeline_report_text_is_string(mixed_diffs):
    result = run_score_pipeline(mixed_diffs)
    assert isinstance(result.report_text, str)


def test_run_score_pipeline_report_markdown_is_string(mixed_diffs):
    result = run_score_pipeline(mixed_diffs)
    assert isinstance(result.report_markdown, str)


def test_run_score_pipeline_empty_diffs():
    result = run_score_pipeline([])
    assert result.total_score == 0
    assert result.scores == []
    assert "No diffs" in result.report_text


def test_run_score_pipeline_diffs_preserved(mixed_diffs):
    result = run_score_pipeline(mixed_diffs)
    assert result.diffs is mixed_diffs
