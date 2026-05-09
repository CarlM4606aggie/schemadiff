"""Summarizes a list of TableDiff objects into a human-readable text block."""

from typing import List
from schemadiff.core import TableDiff, ChangeType
from schemadiff.summary import DiffSummary, build_summary


def _change_type_label(change_type: ChangeType) -> str:
    labels = {
        ChangeType.ADDED: "Added",
        ChangeType.DROPPED: "Dropped",
        ChangeType.MODIFIED: "Modified",
    }
    return labels.get(change_type, str(change_type))


def summarize_diffs(diffs: List[TableDiff], title: str = "Schema Diff Summary") -> str:
    """Return a concise plain-text summary of schema diffs."""
    lines = [f"=== {title} ===", ""]

    if not diffs:
        lines.append("No schema changes detected.")
        return "\n".join(lines)

    summary: DiffSummary = build_summary(diffs)
    counts = summary.change_counts_by_type()

    lines.append(f"Total changes : {summary.total_column_changes() + len(diffs)}")
    for change_type, count in counts.items():
        lines.append(f"  {_change_type_label(change_type):<10}: {count} table(s)")

    lines.append("")
    lines.append("Tables affected:")
    for diff in diffs:
        label = _change_type_label(diff.change_type)
        col_info = ""
        if diff.change_type == ChangeType.MODIFIED and diff.column_diffs:
            col_info = f" ({len(diff.column_diffs)} column change(s))"
        lines.append(f"  [{label}] {diff.table_name}{col_info}")

    return "\n".join(lines)


def summarize_to_dict(diffs: List[TableDiff]) -> dict:
    """Return a structured dict representation of the diff summary."""
    summary: DiffSummary = build_summary(diffs)
    counts = summary.change_counts_by_type()

    return {
        "has_changes": summary.has_changes(),
        "total_column_changes": summary.total_column_changes(),
        "change_counts": {
            _change_type_label(ct).lower(): n for ct, n in counts.items()
        },
        "tables": [
            {
                "name": d.table_name,
                "change_type": _change_type_label(d.change_type).lower(),
                "column_changes": len(d.column_diffs) if d.column_diffs else 0,
            }
            for d in diffs
        ],
    }
