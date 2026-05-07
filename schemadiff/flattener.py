"""Flatten nested schema diffs into a simple list of labeled change records."""

from dataclasses import dataclass
from typing import List

from schemadiff.core import TableDiff, ColumnDiff, ChangeType


@dataclass
class FlatDiffRecord:
    """A single flattened change record derived from a TableDiff."""

    table_name: str
    change_type: ChangeType
    column_name: str | None
    column_change: str | None
    label: str

    def to_dict(self) -> dict:
        return {
            "table": self.table_name,
            "change_type": self.change_type.value,
            "column": self.column_name,
            "column_change": self.column_change,
            "label": self.label,
        }


def _column_change_summary(col_diff: ColumnDiff) -> str:
    parts = []
    if col_diff.old_type != col_diff.new_type:
        parts.append(f"type: {col_diff.old_type} -> {col_diff.new_type}")
    if col_diff.old_nullable != col_diff.new_nullable:
        parts.append(f"nullable: {col_diff.old_nullable} -> {col_diff.new_nullable}")
    return "; ".join(parts) if parts else "modified"


def flatten_diff(table_diff: TableDiff) -> List[FlatDiffRecord]:
    """Expand a single TableDiff into one or more FlatDiffRecords."""
    records: List[FlatDiffRecord] = []

    if table_diff.change_type in (ChangeType.ADDED, ChangeType.DROPPED):
        verb = "Added" if table_diff.change_type == ChangeType.ADDED else "Dropped"
        records.append(
            FlatDiffRecord(
                table_name=table_diff.table_name,
                change_type=table_diff.change_type,
                column_name=None,
                column_change=None,
                label=f"{verb} table `{table_diff.table_name}`",
            )
        )
        return records

    # MODIFIED — expand per column diff
    for col_diff in table_diff.column_diffs:
        if col_diff.change_type == ChangeType.ADDED:
            label = f"Added column `{col_diff.column_name}` to `{table_diff.table_name}`"
            col_change = f"type: {col_diff.new_type}, nullable: {col_diff.new_nullable}"
        elif col_diff.change_type == ChangeType.DROPPED:
            label = f"Dropped column `{col_diff.column_name}` from `{table_diff.table_name}`"
            col_change = f"type: {col_diff.old_type}, nullable: {col_diff.old_nullable}"
        else:
            summary = _column_change_summary(col_diff)
            label = f"Modified column `{col_diff.column_name}` in `{table_diff.table_name}`"
            col_change = summary

        records.append(
            FlatDiffRecord(
                table_name=table_diff.table_name,
                change_type=col_diff.change_type,
                column_name=col_diff.column_name,
                column_change=col_change,
                label=label,
            )
        )

    return records


def flatten_diffs(table_diffs: List[TableDiff]) -> List[FlatDiffRecord]:
    """Flatten a list of TableDiffs into a flat list of FlatDiffRecords."""
    result: List[FlatDiffRecord] = []
    for diff in table_diffs:
        result.extend(flatten_diff(diff))
    return result
