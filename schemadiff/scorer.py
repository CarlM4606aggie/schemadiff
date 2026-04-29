"""Scores schema diffs by severity to help prioritize migration work."""

from dataclasses import dataclass, field
from typing import List, Dict

from schemadiff.core import ChangeType, TableDiff, ColumnDiff

# Severity weights for different change types
_TABLE_WEIGHTS: Dict[ChangeType, int] = {
    ChangeType.DROPPED: 10,
    ChangeType.ADDED: 3,
    ChangeType.MODIFIED: 5,
}

_COLUMN_WEIGHTS: Dict[ChangeType, int] = {
    ChangeType.DROPPED: 6,
    ChangeType.ADDED: 2,
    ChangeType.MODIFIED: 4,
}


@dataclass
class DiffScore:
    table_name: str
    score: int
    reasons: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"DiffScore(table={self.table_name!r}, score={self.score})"


def score_table_diff(diff: TableDiff) -> DiffScore:
    """Compute a severity score for a single TableDiff."""
    reasons: List[str] = []
    total = 0

    base = _TABLE_WEIGHTS.get(diff.change_type, 1)
    total += base
    reasons.append(f"table {diff.change_type.value} (+{base})")

    for col_diff in diff.column_diffs:
        weight = _COLUMN_WEIGHTS.get(col_diff.change_type, 1)
        total += weight
        reasons.append(
            f"column '{col_diff.column_name}' {col_diff.change_type.value} (+{weight})"
        )

        # Extra penalty when a column becomes NOT NULL (risky migration)
        if (
            col_diff.change_type == ChangeType.MODIFIED
            and col_diff.new_definition
            and col_diff.old_definition
        ):
            old_null = col_diff.old_definition.get("nullable", True)
            new_null = col_diff.new_definition.get("nullable", True)
            if old_null and not new_null:
                total += 3
                reasons.append(f"column '{col_diff.column_name}' nullable→not-null (+3)")

    return DiffScore(table_name=diff.table_name, score=total, reasons=reasons)


def score_diffs(diffs: List[TableDiff]) -> List[DiffScore]:
    """Score all diffs and return sorted list (highest severity first)."""
    scores = [score_table_diff(d) for d in diffs]
    return sorted(scores, key=lambda s: s.score, reverse=True)


def total_score(diffs: List[TableDiff]) -> int:
    """Return the combined severity score across all diffs."""
    return sum(s.score for s in score_diffs(diffs))
