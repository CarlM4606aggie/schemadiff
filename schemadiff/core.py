"""Core module for schemadiff.

Provides the main diffing logic for comparing database schema snapshots
across environments and generating human-readable migration diffs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ChangeType(Enum):
    """Types of schema changes that can be detected."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass
class ColumnDiff:
    """Represents a diff for a single column."""
    name: str
    change_type: ChangeType
    old_definition: dict[str, Any] | None = None
    new_definition: dict[str, Any] | None = None

    def describe(self) -> str:
        """Return a human-readable description of the column change."""
        if self.change_type == ChangeType.ADDED:
            return f"  + ADD COLUMN {self.name}: {self.new_definition}"
        elif self.change_type == ChangeType.REMOVED:
            return f"  - DROP COLUMN {self.name}: {self.old_definition}"
        elif self.change_type == ChangeType.MODIFIED:
            return (
                f"  ~ MODIFY COLUMN {self.name}:\n"
                f"      before: {self.old_definition}\n"
                f"      after:  {self.new_definition}"
            )
        return ""


@dataclass
class TableDiff:
    """Represents a diff for a single table."""
    name: str
    change_type: ChangeType
    column_diffs: list[ColumnDiff] = field(default_factory=list)

    def describe(self) -> str:
        """Return a human-readable description of the table change."""
        lines = []
        if self.change_type == ChangeType.ADDED:
            lines.append(f"[+] TABLE ADDED: {self.name}")
        elif self.change_type == ChangeType.REMOVED:
            lines.append(f"[-] TABLE REMOVED: {self.name}")
        elif self.change_type == ChangeType.MODIFIED:
            lines.append(f"[~] TABLE MODIFIED: {self.name}")

        for col_diff in self.column_diffs:
            lines.append(col_diff.describe())

        return "\n".join(lines)


@dataclass
class SchemaDiff:
    """Top-level container for all differences between two schema snapshots."""
    source_env: str
    target_env: str
    table_diffs: list[TableDiff] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        """Return True if any differences were detected."""
        return len(self.table_diffs) > 0

    def summary(self) -> str:
        """Return a concise summary of all detected changes."""
        if not self.has_changes:
            return f"No differences found between '{self.source_env}' and '{self.target_env}'."

        lines = [
            f"Schema diff: '{self.source_env}' → '{self.target_env}'",
            f"{'=' * 50}",
        ]
        for table_diff in self.table_diffs:
            lines.append(table_diff.describe())
            lines.append("")

        added = sum(1 for t in self.table_diffs if t.change_type == ChangeType.ADDED)
        removed = sum(1 for t in self.table_diffs if t.change_type == ChangeType.REMOVED)
        modified = sum(1 for t in self.table_diffs if t.change_type == ChangeType.MODIFIED)
        lines.append(
            f"Summary: {added} table(s) added, {removed} removed, {modified} modified."
        )
        return "\n".join(lines)


def diff_schemas(
    source: dict[str, Any],
    target: dict[str, Any],
    source_env: str = "source",
    target_env: str = "target",
) -> SchemaDiff:
    """Compare two schema snapshots and return a SchemaDiff.

    Args:
        source: Schema snapshot dict mapping table names to column definitions.
        target: Schema snapshot dict mapping table names to column definitions.
        source_env: Label for the source environment.
        target_env: Label for the target environment.

    Returns:
        A SchemaDiff object describing all detected changes.
    """
    result = SchemaDiff(source_env=source_env, target_env=target_env)

    all_tables = set(source.keys()) | set(target.keys())

    for table_name in sorted(all_tables):
        if table_name not in source:
            result.table_diffs.append(TableDiff(name=table_name, change_type=ChangeType.ADDED))
        elif table_name not in target:
            result.table_diffs.append(TableDiff(name=table_name, change_type=ChangeType.REMOVED))
        else:
            column_diffs = _diff_columns(source[table_name], target[table_name])
            if column_diffs:
                result.table_diffs.append(
                    TableDiff(
                        name=table_name,
                        change_type=ChangeType.MODIFIED,
                        column_diffs=column_diffs,
                    )
                )

    return result


def _diff_columns(
    source_cols: dict[str, Any],
    target_cols: dict[str, Any],
) -> list[ColumnDiff]:
    """Compare column definitions between two tables."""
    diffs = []
    all_cols = set(source_cols.keys()) | set(target_cols.keys())

    for col_name in sorted(all_cols):
        if col_name not in source_cols:
            diffs.append(ColumnDiff(col_name, ChangeType.ADDED, new_definition=target_cols[col_name]))
        elif col_name not in target_cols:
            diffs.append(ColumnDiff(col_name, ChangeType.REMOVED, old_definition=source_cols[col_name]))
        elif source_cols[col_name] != target_cols[col_name]:
            diffs.append(
                ColumnDiff(
                    col_name,
                    ChangeType.MODIFIED,
                    old_definition=source_cols[col_name],
                    new_definition=target_cols[col_name],
                )
            )

    return diffs
