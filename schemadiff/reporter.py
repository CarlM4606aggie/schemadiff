"""Human-readable report generation for schema diffs."""

from typing import List, Optional
from schemadiff.core import SchemaDiff, TableDiff, ColumnDiff, ChangeType


CHANGE_SYMBOLS = {
    ChangeType.ADDED: "+",
    ChangeType.REMOVED: "-",
    ChangeType.MODIFIED: "~",
}

CHANGE_LABELS = {
    ChangeType.ADDED: "ADDED",
    ChangeType.REMOVED: "REMOVED",
    ChangeType.MODIFIED: "MODIFIED",
}


def format_column_diff(col: ColumnDiff, indent: int = 4) -> str:
    """Format a single column diff as a readable string."""
    pad = " " * indent
    symbol = CHANGE_SYMBOLS[col.change_type]
    label = CHANGE_LABELS[col.change_type]
    line = f"{pad}{symbol} {col.column_name} [{label}]"
    if col.change_type == ChangeType.MODIFIED:
        details = []
        if col.old_type != col.new_type:
            details.append(f"type: {col.old_type} -> {col.new_type}")
        if col.old_nullable != col.new_nullable:
            details.append(f"nullable: {col.old_nullable} -> {col.new_nullable}")
        if details:
            line += f" ({', '.join(details)})"
    elif col.change_type == ChangeType.ADDED:
        line += f" (type: {col.new_type}, nullable: {col.new_nullable})"
    elif col.change_type == ChangeType.REMOVED:
        line += f" (type: {col.old_type}, nullable: {col.old_nullable})"
    return line


def format_table_diff(table: TableDiff) -> List[str]:
    """Format a table diff block as a list of lines."""
    symbol = CHANGE_SYMBOLS.get(table.change_type, "?")
    label = CHANGE_LABELS.get(table.change_type, "UNKNOWN")
    lines = [f"{symbol} Table: {table.table_name} [{label}]"]
    for col in table.column_diffs:
        lines.append(format_column_diff(col))
    return lines


def generate_report(
    diff: SchemaDiff,
    title: Optional[str] = None,
    show_summary: bool = True,
) -> str:
    """Generate a full human-readable migration diff report."""
    lines = []

    if title:
        lines.append(title)
        lines.append("=" * len(title))
    else:
        lines.append("Schema Migration Diff")
        lines.append("=" * 21)

    if not diff.table_diffs:
        lines.append("No differences found.")
        return "\n".join(lines)

    for table in diff.table_diffs:
        lines.extend(format_table_diff(table))
        lines.append("")

    if show_summary:
        added = sum(1 for t in diff.table_diffs if t.change_type == ChangeType.ADDED)
        removed = sum(1 for t in diff.table_diffs if t.change_type == ChangeType.REMOVED)
        modified = sum(1 for t in diff.table_diffs if t.change_type == ChangeType.MODIFIED)
        lines.append(f"Summary: {added} added, {removed} removed, {modified} modified table(s).")

    return "\n".join(lines)
