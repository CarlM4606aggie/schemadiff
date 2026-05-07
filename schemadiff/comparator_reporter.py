"""Renders human-readable reports from raw comparator output."""

from typing import List
from schemadiff.core import TableDiff, ChangeType
from schemadiff.summary import build_summary


def _change_symbol(change_type: ChangeType) -> str:
    symbols = {
        ChangeType.ADDED: "+",
        ChangeType.DROPPED: "-",
        ChangeType.MODIFIED: "~",
    }
    return symbols.get(change_type, "?")


def _format_table_entry(diff: TableDiff) -> str:
    symbol = _change_symbol(diff.change_type)
    lines = [f"  [{symbol}] {diff.table_name}"]
    for col_diff in diff.column_diffs:
        col_symbol = _change_symbol(col_diff.change_type)
        lines.append(f"      [{col_symbol}] column: {col_diff.column_name}")
        if col_diff.old_definition:
            lines.append(f"          before: {col_diff.old_definition}")
        if col_diff.new_definition:
            lines.append(f"          after:  {col_diff.new_definition}")
    return "\n".join(lines)


def render_comparator_text(diffs: List[TableDiff], title: str = "Schema Comparison") -> str:
    """Render a plain-text report from a list of TableDiff objects."""
    lines = [title, "=" * len(title), ""]
    if not diffs:
        lines.append("No differences found.")
        return "\n".join(lines)
    summary = build_summary(diffs)
    lines.append(f"Summary: {summary.total_changes} table change(s) detected")
    lines.append("")
    for diff in diffs:
        lines.append(_format_table_entry(diff))
    return "\n".join(lines)


def render_comparator_markdown(diffs: List[TableDiff], title: str = "Schema Comparison") -> str:
    """Render a Markdown report from a list of TableDiff objects."""
    lines = [f"# {title}", ""]
    if not diffs:
        lines.append("_No differences found._")
        return "\n".join(lines)
    summary = build_summary(diffs)
    lines.append(f"**{summary.total_changes} table change(s) detected**")
    lines.append("")
    lines.append("| Symbol | Table | Columns Changed |")
    lines.append("|--------|-------|-----------------|")
    for diff in diffs:
        symbol = _change_symbol(diff.change_type)
        col_count = len(diff.column_diffs)
        lines.append(f"| `{symbol}` | `{diff.table_name}` | {col_count} |")
    return "\n".join(lines)
