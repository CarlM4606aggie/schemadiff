"""Labels diffs with human-readable migration intent strings."""

from dataclasses import dataclass, field
from typing import List, Optional

from schemadiff.core import ChangeType, TableDiff


@dataclass
class LabeledDiff:
    diff: TableDiff
    label: str
    intent: str
    detail: Optional[str] = None

    def __repr__(self) -> str:
        return f"LabeledDiff(table={self.diff.table_name!r}, label={self.label!r})"


def _label_for_diff(diff: TableDiff) -> str:
    """Return a short label summarizing the migration intent."""
    if diff.change_type == ChangeType.ADDED:
        return "CREATE TABLE"
    if diff.change_type == ChangeType.DROPPED:
        return "DROP TABLE"

    # MODIFIED — inspect column diffs
    added = [c for c in diff.column_diffs if c.change_type == ChangeType.ADDED]
    dropped = [c for c in diff.column_diffs if c.change_type == ChangeType.DROPPED]
    modified = [c for c in diff.column_diffs if c.change_type == ChangeType.MODIFIED]

    parts = []
    if added:
        parts.append(f"ADD COLUMN x{len(added)}")
    if dropped:
        parts.append(f"DROP COLUMN x{len(dropped)}")
    if modified:
        parts.append(f"ALTER COLUMN x{len(modified)}")

    return ", ".join(parts) if parts else "ALTER TABLE"


def _intent_for_diff(diff: TableDiff) -> str:
    """Return a sentence describing the migration intent."""
    if diff.change_type == ChangeType.ADDED:
        return f"Create new table '{diff.table_name}'."
    if diff.change_type == ChangeType.DROPPED:
        return f"Remove table '{diff.table_name}' entirely."

    added = [c for c in diff.column_diffs if c.change_type == ChangeType.ADDED]
    dropped = [c for c in diff.column_diffs if c.change_type == ChangeType.DROPPED]
    modified = [c for c in diff.column_diffs if c.change_type == ChangeType.MODIFIED]

    sentences = []
    if added:
        names = ", ".join(c.column_name for c in added)
        sentences.append(f"Add column(s): {names}.")
    if dropped:
        names = ", ".join(c.column_name for c in dropped)
        sentences.append(f"Drop column(s): {names}.")
    if modified:
        names = ", ".join(c.column_name for c in modified)
        sentences.append(f"Modify column(s): {names}.")

    return " ".join(sentences) if sentences else f"Alter table '{diff.table_name}'."


def label_diff(diff: TableDiff) -> LabeledDiff:
    """Attach a label and intent string to a single TableDiff."""
    return LabeledDiff(
        diff=diff,
        label=_label_for_diff(diff),
        intent=_intent_for_diff(diff),
    )


def label_diffs(diffs: List[TableDiff]) -> List[LabeledDiff]:
    """Label all diffs in a list."""
    return [label_diff(d) for d in diffs]
