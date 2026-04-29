"""Generates SQL patch statements from schema diffs."""

from typing import List
from schemadiff.core import TableDiff, ColumnDiff, ChangeType


def _column_def(col: dict) -> str:
    """Format a column definition string from column metadata."""
    col_type = col.get("type", "TEXT")
    nullable = col.get("nullable", True)
    null_clause = "NULL" if nullable else "NOT NULL"
    default = col.get("default")
    default_clause = f" DEFAULT {default}" if default is not None else ""
    return f"{col_type} {null_clause}{default_clause}"


def patch_for_column_diff(table_name: str, col_diff: ColumnDiff) -> str:
    """Return a SQL statement for a single column change."""
    col = col_diff.column_name
    if col_diff.change_type == ChangeType.ADDED:
        defn = _column_def(col_diff.new_value or {})
        return f"ALTER TABLE {table_name} ADD COLUMN {col} {defn};"
    elif col_diff.change_type == ChangeType.DROPPED:
        return f"ALTER TABLE {table_name} DROP COLUMN {col};"
    elif col_diff.change_type == ChangeType.MODIFIED:
        defn = _column_def(col_diff.new_value or {})
        return f"ALTER TABLE {table_name} MODIFY COLUMN {col} {defn};"
    return ""


def patch_for_table_diff(table_diff: TableDiff) -> List[str]:
    """Return a list of SQL statements for a table-level diff."""
    statements = []
    table = table_diff.table_name

    if table_diff.change_type == ChangeType.ADDED:
        statements.append(f"-- Table '{table}' was added (manual CREATE TABLE required).")
    elif table_diff.change_type == ChangeType.DROPPED:
        statements.append(f"DROP TABLE IF EXISTS {table};")
    elif table_diff.change_type == ChangeType.MODIFIED:
        for col_diff in table_diff.column_diffs:
            stmt = patch_for_column_diff(table, col_diff)
            if stmt:
                statements.append(stmt)

    return statements


def generate_patch(diffs: List[TableDiff]) -> str:
    """Generate a full SQL patch script from a list of TableDiff objects."""
    lines = ["-- Auto-generated migration patch", "-- Review before applying\n"]
    for table_diff in diffs:
        stmts = patch_for_table_diff(table_diff)
        lines.extend(stmts)
    return "\n".join(lines)
