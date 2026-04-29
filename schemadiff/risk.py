"""High-level risk assessment built on top of scorer."""

from dataclasses import dataclass
from enum import Enum
from typing import List

from schemadiff.core import TableDiff
from schemadiff.scorer import score_diffs, total_score, DiffScore


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_THRESHOLDS = [
    (30, RiskLevel.CRITICAL),
    (15, RiskLevel.HIGH),
    (6, RiskLevel.MEDIUM),
    (0, RiskLevel.LOW),
]


@dataclass
class RiskReport:
    level: RiskLevel
    total: int
    top_scores: List[DiffScore]

    def summary(self) -> str:
        lines = [
            f"Risk level : {self.level.value.upper()}",
            f"Total score: {self.total}",
            "",
            "Top contributors:",
        ]
        for s in self.top_scores:
            lines.append(f"  {s.table_name:<30} score={s.score}")
        return "\n".join(lines)


def _classify(score: int) -> RiskLevel:
    for threshold, level in _THRESHOLDS:
        if score > threshold:
            return level
    return RiskLevel.LOW


def assess_risk(diffs: List[TableDiff], top_n: int = 5) -> RiskReport:
    """Assess the overall migration risk for a list of diffs.

    Args:
        diffs: List of TableDiff objects to evaluate.
        top_n: Number of highest-scoring tables to include in the report.

    Returns:
        A RiskReport with a risk level, total score, and top contributors.
    """
    scores = score_diffs(diffs)
    combined = total_score(diffs)
    level = _classify(combined)
    return RiskReport(
        level=level,
        total=combined,
        top_scores=scores[:top_n],
    )
