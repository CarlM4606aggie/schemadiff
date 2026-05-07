"""Tests for schemadiff.scorer_reporter."""

import pytest
from schemadiff.scorer import DiffScore
from schemadiff.scorer_reporter import (
    _risk_label,
    render_score_text,
    render_score_markdown,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _score(table: str, score: int, reasons=None) -> DiffScore:
    return DiffScore(table_name=table, score=score, reasons=reasons or [])


# ---------------------------------------------------------------------------
# _risk_label
# ---------------------------------------------------------------------------

def test_risk_label_zero_is_none():
    assert _risk_label(0) == "none"


def test_risk_label_low():
    assert _risk_label(2) == "low"


def test_risk_label_medium():
    assert _risk_label(5) == "medium"


def test_risk_label_high():
    assert _risk_label(10) == "high"


def test_risk_label_boundary_low_to_medium():
    """Score of 4 is still low; 5 is the first medium value."""
    assert _risk_label(4) == "low"
    assert _risk_label(5) == "medium"


def test_risk_label_boundary_medium_to_high():
    """Score of 7 is still medium; 8 is the first high value."""
    assert _risk_label(7) == "medium"
    assert _risk_label(8) == "high"


# ---------------------------------------------------------------------------
# render_score_text
# ---------------------------------------------------------------------------

def test_render_text_empty_returns_no_diffs_message():
    result = render_score_text([])
    assert "No diffs" in result


def test_render_text_returns_string():
    scores = [_score("users", 3, ["column dropped"])]
    result = render_score_text(scores)
    assert isinstance(result, str)


def test_render_text_contains_table_name():
    scores = [_score("orders", 5, ["type changed"])]
    result = render_score_text(scores)
    assert "orders" in result


def test_render_text_contains_total_score():
    scores = [_score("a", 4), _score("b", 3)]
    result = render_score_text(scores)
    assert "7" in result


def test_render_text_lists_reasons():
    scores = [_score("tbl", 6, ["nullable tightened", "column dropped"])]
    result = render_score_text(scores)
    assert "nullable tightened" in result
    assert "column dropped" in result


def test_render_text_risk_label_present():
    scores = [_score("tbl", 10)]
    result = render_score_text(scores)
    assert "HIGH" in result


def test_render_text_multiple_tables_all_present():
    """All table names should appear when multiple scores are rendered."""
    scores = [_score("users", 2), _score("orders", 5), _score("products", 8)]
    result = render_score_text(scores)
    assert "users" in result
    assert "orders" in result
    assert "products" in result


# ---------------------------------------------------------------------------
# render_score_markdown
# ---------------------------------------------------------------------------

def test_render_markdown_empty_returns_message():
    result = render_score_markdown([])
    assert "No diffs" in result


def test_render_markdown_returns_string():
    scores = [_score("users", 2)]
    result = render_score_markdown(scores)
    assert isinstance(result, str)


def test_render_markdown_contains_table_header():
    scores = [_score("users", 2)]
    result = render_score_markdown(scores)
    assert "| Table |" in result


def test_render_markdown_contains_table_name():
    scores = [_score("products", 4)]
    result = render_score_markdown(scores)
    assert "products" in result


def test_render_markdown_contains_total_score():
    scores = [_score("a", 3),
