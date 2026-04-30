"""Groups TableDiff objects by various criteria for reporting and analysis."""

from collections import defaultdict
from typing import Dict, List, Optional

from schemadiff.core import ChangeType, TableDiff


def group_by_change_type(diffs: List[TableDiff]) -> Dict[str, List[TableDiff]]:
    """Group diffs by their change type string label."""
    groups: Dict[str, List[TableDiff]] = defaultdict(list)
    for diff in diffs:
        key = diff.change_type.value
        groups[key].append(diff)
    return dict(groups)


def group_by_prefix(diffs: List[TableDiff], separator: str = "_") -> Dict[str, List[TableDiff]]:
    """Group diffs by table name prefix (e.g. 'users' from 'users_roles')."""
    groups: Dict[str, List[TableDiff]] = defaultdict(list)
    for diff in diffs:
        parts = diff.table_name.split(separator, 1)
        prefix = parts[0] if len(parts) > 1 else diff.table_name
        groups[prefix].append(diff)
    return dict(groups)


def group_by_risk(diffs: List[TableDiff]) -> Dict[str, List[TableDiff]]:
    """Group diffs into 'high', 'medium', and 'low' risk buckets.

    High:   dropped tables, columns with type changes or NOT NULL additions
    Medium: modified tables with dropped columns
    Low:    added tables or purely additive column changes
    """
    groups: Dict[str, List[TableDiff]] = {"high": [], "medium": [], "low": []}

    for diff in diffs:
        if diff.change_type == ChangeType.DROPPED:
            groups["high"].append(diff)
            continue

        if diff.change_type == ChangeType.ADDED:
            groups["low"].append(diff)
            continue

        # MODIFIED — inspect column diffs
        has_type_change = any(
            cd.old_type != cd.new_type
            for cd in diff.column_diffs
            if cd.old_type is not None and cd.new_type is not None
        )
        has_dropped_col = any(
            cd.new_type is None for cd in diff.column_diffs
        )
        has_nullable_tightened = any(
            cd.old_nullable is True and cd.new_nullable is False
            for cd in diff.column_diffs
            if cd.old_nullable is not None and cd.new_nullable is not None
        )

        if has_type_change or has_nullable_tightened:
            groups["high"].append(diff)
        elif has_dropped_col:
            groups["medium"].append(diff)
        else:
            groups["low"].append(diff)

    return groups


def group_summary(groups: Dict[str, List[TableDiff]]) -> Dict[str, int]:
    """Return a count summary for each group key."""
    return {key: len(items) for key, items in groups.items()}
