"""Truncates diff lists to a maximum number of entries, with summary metadata."""

from dataclasses import dataclass, field
from typing import List

from schemadiff.core import TableDiff


@dataclass
class TruncateResult:
    diffs: List[TableDiff]
    total: int
    truncated: int
    limit: int

    @property
    def was_truncated(self) -> bool:
        return self.truncated > 0

    def __repr__(self) -> str:
        return (
            f"TruncateResult(total={self.total}, kept={len(self.diffs)}, "
            f"truncated={self.truncated}, limit={self.limit})"
        )


def truncate_diffs(
    diffs: List[TableDiff],
    limit: int,
    prefer_breaking: bool = False,
) -> TruncateResult:
    """Truncate a list of diffs to at most *limit* entries.

    Args:
        diffs: Full list of TableDiff objects.
        limit: Maximum number of diffs to retain.
        prefer_breaking: When True, sort so that higher-risk (dropped/modified)
            changes are kept over additive ones before truncating.

    Returns:
        TruncateResult with the kept diffs and metadata.
    """
    if limit < 0:
        raise ValueError(f"limit must be >= 0, got {limit}")

    total = len(diffs)

    if total <= limit:
        return TruncateResult(diffs=list(diffs), total=total, truncated=0, limit=limit)

    candidates = list(diffs)

    if prefer_breaking:
        from schemadiff.core import ChangeType

        _priority = {
            ChangeType.DROPPED: 0,
            ChangeType.MODIFIED: 1,
            ChangeType.ADDED: 2,
        }
        candidates.sort(key=lambda d: _priority.get(d.change_type, 99))

    kept = candidates[:limit]
    truncated = total - limit

    return TruncateResult(diffs=kept, total=total, truncated=truncated, limit=limit)


def truncate_summary(result: TruncateResult) -> str:
    """Return a human-readable summary line for a TruncateResult."""
    if not result.was_truncated:
        return f"Showing all {result.total} diff(s)."
    return (
        f"Showing {len(result.diffs)} of {result.total} diff(s) "
        f"({result.truncated} truncated, limit={result.limit})."
    )
