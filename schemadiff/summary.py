"""Summarise a list of TableDiff objects into high-level statistics."""

from dataclasses import dataclass, field
from typing import List, Dict
from schemadiff.core import TableDiff, ChangeType


@dataclass
class DiffSummary:
    """Aggregated statistics for a set of schema diffs."""

    total_changes: int = 0
    added_tables: List[str] = field(default_factory=list)
    dropped_tables: List[str] = field(default_factory=list)
    modified_tables: List[str] = field(default_factory=list)
    column_additions: int = 0
    column_drops: int = 0
    column_modifications: int = 0

    def change_counts_by_type(self) -> Dict[str, int]:
        """Return a mapping of change type label to count."""
        return {
            "added_tables": len(self.added_tables),
            "dropped_tables": len(self.dropped_tables),
            "modified_tables": len(self.modified_tables),
            "column_additions": self.column_additions,
            "column_drops": self.column_drops,
            "column_modifications": self.column_modifications,
        }

    def has_changes(self) -> bool:
        """Return True if any changes are present."""
        return self.total_changes > 0

    def total_column_changes(self) -> int:
        """Return the total number of column-level changes across all tables."""
        return self.column_additions + self.column_drops + self.column_modifications


def build_summary(diffs: List[TableDiff]) -> DiffSummary:
    """Build a DiffSummary from a list of TableDiff objects.

    Args:
        diffs: List of TableDiff objects produced by the comparator.

    Returns:
        A populated DiffSummary instance.
    """
    summary = DiffSummary()

    for diff in diffs:
        summary.total_changes += 1

        if diff.change_type == ChangeType.ADDED:
            summary.added_tables.append(diff.table_name)
        elif diff.change_type == ChangeType.DROPPED:
            summary.dropped_tables.append(diff.table_name)
        elif diff.change_type == ChangeType.MODIFIED:
            summary.modified_tables.append(diff.table_name)

        for col_diff in diff.column_diffs:
            if col_diff.change_type == ChangeType.ADDED:
                summary.column_additions += 1
            elif col_diff.change_type == ChangeType.DROPPED:
                summary.column_drops += 1
            elif col_diff.change_type == ChangeType.MODIFIED:
                summary.column_modifications += 1

    return summary
