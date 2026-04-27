"""Comparator module for diffing two SchemaSnapshot instances."""

from typing import List
from schemadiff.core import (
    ChangeType,
    ColumnDiff,
    TableDiff,
)
from schemadiff.snapshot import SchemaSnapshot


def compare_snapshots(old: SchemaSnapshot, new: SchemaSnapshot) -> List[TableDiff]:
    """Compare two schema snapshots and return a list of TableDiff objects.

    Args:
        old: The baseline schema snapshot.
        new: The target schema snapshot to compare against.

    Returns:
        A list of TableDiff objects describing all detected changes.
    """
    diffs: List[TableDiff] = []

    old_tables = set(old.table_names())
    new_tables = set(new.table_names())

    # Detect dropped tables
    for table_name in sorted(old_tables - new_tables):
        table = old.get_table(table_name)
        diffs.append(
            TableDiff(
                table_name=table_name,
                change_type=ChangeType.DROPPED,
                columns=[],
                old_columns=list(table.get("columns", {}).keys()),
            )
        )

    # Detect added tables
    for table_name in sorted(new_tables - old_tables):
        table = new.get_table(table_name)
        diffs.append(
            TableDiff(
                table_name=table_name,
                change_type=ChangeType.ADDED,
                columns=list(table.get("columns", {}).keys()),
                old_columns=[],
            )
        )

    # Detect modified tables
    for table_name in sorted(old_tables & new_tables):
        column_diffs = _compare_columns(
            old.get_table(table_name),
            new.get_table(table_name),
        )
        if column_diffs:
            diffs.append(
                TableDiff(
                    table_name=table_name,
                    change_type=ChangeType.MODIFIED,
                    columns=[],
                    old_columns=[],
                    column_diffs=column_diffs,
                )
            )

    return diffs


def _compare_columns(old_table: dict, new_table: dict) -> List[ColumnDiff]:
    """Compare columns between two table definitions."""
    diffs: List[ColumnDiff] = []
    old_cols = old_table.get("columns", {})
    new_cols = new_table.get("columns", {})

    old_names = set(old_cols.keys())
    new_names = set(new_cols.keys())

    for col in sorted(old_names - new_names):
        diffs.append(ColumnDiff(name=col, change_type=ChangeType.DROPPED, old=old_cols[col], new=None))

    for col in sorted(new_names - old_names):
        diffs.append(ColumnDiff(name=col, change_type=ChangeType.ADDED, old=None, new=new_cols[col]))

    for col in sorted(old_names & new_names):
        if old_cols[col] != new_cols[col]:
            diffs.append(ColumnDiff(name=col, change_type=ChangeType.MODIFIED, old=old_cols[col], new=new_cols[col]))

    return diffs
