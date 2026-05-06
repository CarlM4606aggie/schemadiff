"""Pipeline helpers that integrate scoring into a full diff workflow."""

from dataclasses import dataclass, field
from typing import List, Optional

from schemadiff.core import TableDiff
from schemadiff.scorer import DiffScore, score_diffs
from schemadiff.scorer_reporter import render_score_text, render_score_markdown


@dataclass
class ScorePipelineResult:
    diffs: List[TableDiff]
    scores: List[DiffScore]
    total_score: int
    report_text: str
    report_markdown: str

    def is_high_risk(self, threshold: int = 8) -> bool:
        """Return True if the total score meets or exceeds *threshold*."""
        return self.total_score >= threshold


def run_score_pipeline(
    diffs: List[TableDiff],
    threshold: Optional[int] = None,
) -> ScorePipelineResult:
    """Score *diffs* and produce text + markdown reports.

    Args:
        diffs: List of TableDiff objects from the comparator.
        threshold: Optional risk threshold forwarded to ``is_high_risk``.

    Returns:
        A :class:`ScorePipelineResult` with scores and rendered reports.
    """
    scores = score_diffs(diffs)
    total = sum(s.score for s in scores)
    text = render_score_text(scores)
    md = render_score_markdown(scores)

    return ScorePipelineResult(
        diffs=diffs,
        scores=scores,
        total_score=total,
        report_text=text,
        report_markdown=md,
    )
