"""Deduplicator: removes duplicate TableDiff entries from a diff list.

Two diffs are considered duplicates if they share the same table name
and change type. When duplicates exist the first occurrence is kept.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

from schemadiff.core import TableDiff


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass."""

    diffs: List[TableDiff]
    removed_count: int

    @property
    def had_duplicates(self) -> bool:
        return self.removed_count > 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"DeduplicateResult(kept={len(self.diffs)}, "
            f"removed={self.removed_count})"
        )


def _diff_key(diff: TableDiff) -> tuple:
    """Return a hashable key that identifies a diff uniquely."""
    return (diff.table_name, diff.change_type)


def deduplicate(diffs: Sequence[TableDiff]) -> DeduplicateResult:
    """Remove duplicate diffs, keeping the first occurrence of each key.

    Args:
        diffs: Sequence of TableDiff objects, possibly containing duplicates.

    Returns:
        DeduplicateResult with the deduplicated list and a count of removed items.
    """
    seen: set = set()
    unique: List[TableDiff] = []

    for diff in diffs:
        key = _diff_key(diff)
        if key not in seen:
            seen.add(key)
            unique.append(diff)

    removed = len(diffs) - len(unique)
    return DeduplicateResult(diffs=unique, removed_count=removed)


def deduplicate_summary(result: DeduplicateResult) -> str:
    """Return a human-readable summary of the deduplication result.

    Args:
        result: A DeduplicateResult instance.

    Returns:
        A plain-text summary string.
    """
    lines = [
        f"Deduplication complete.",
        f"  Unique diffs kept : {len(result.diffs)}",
        f"  Duplicates removed: {result.removed_count}",
    ]
    if not result.had_duplicates:
        lines.append("  No duplicates were found.")
    return "\n".join(lines)
