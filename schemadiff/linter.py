"""Linter for schema diffs — flags potential issues or anti-patterns in detected changes."""

from dataclasses import dataclass, field
from typing import List

from schemadiff.core import TableDiff, ColumnDiff, ChangeType


@dataclass
class LintWarning:
    table: str
    column: str | None
    message: str
    severity: str = "warning"  # "warning" or "error"

    def __str__(self) -> str:
        location = f"{self.table}.{self.column}" if self.column else self.table
        return f"[{self.severity.upper()}] {location}: {self.message}"


@dataclass
class LintResult:
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.warnings) > 0

    @property
    def error_count(self) -> int:
        return sum(1 for w in self.warnings if w.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for w in self.warnings if w.severity == "warning")

    def __str__(self) -> str:
        if not self.warnings:
            return "No lint issues found."
        lines = [str(w) for w in self.warnings]
        lines.append(f"\n{self.error_count} error(s), {self.warning_count} warning(s)")
        return "\n".join(lines)


def _lint_column_diff(table_name: str, col_diff: ColumnDiff) -> List[LintWarning]:
    issues: List[LintWarning] = []
    col = col_diff.column_name

    if col_diff.change_type == ChangeType.DROPPED:
        issues.append(LintWarning(
            table=table_name, column=col,
            message="Column dropped — ensure no application code references this column.",
            severity="error"
        ))

    if col_diff.change_type == ChangeType.MODIFIED:
        old = (col_diff.old_definition or {}).get("type", "")
        new = (col_diff.new_definition or {}).get("type", "")
        if old and new and old != new:
            issues.append(LintWarning(
                table=table_name, column=col,
                message=f"Column type changed from '{old}' to '{new}' — may cause data loss or require migration.",
                severity="error"
            ))

        old_nullable = (col_diff.old_definition or {}).get("nullable", True)
        new_nullable = (col_diff.new_definition or {}).get("nullable", True)
        if old_nullable and not new_nullable:
            issues.append(LintWarning(
                table=table_name, column=col,
                message="Column changed to NOT NULL — existing NULL values will cause migration failure.",
                severity="warning"
            ))

    return issues


def lint_diffs(diffs: List[TableDiff]) -> LintResult:
    """Run lint checks over a list of TableDiff objects and return a LintResult."""
    result = LintResult()

    for table_diff in diffs:
        if table_diff.change_type == ChangeType.DROPPED:
            result.warnings.append(LintWarning(
                table=table_diff.table_name, column=None,
                message="Table dropped — verify all foreign key references are removed.",
                severity="error"
            ))

        for col_diff in (table_diff.column_diffs or []):
            result.warnings.extend(_lint_column_diff(table_diff.table_name, col_diff))

    return result
