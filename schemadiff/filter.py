"""Filter utilities for schema diffs — allows narrowing results by table name or change type."""

from typing import List, Optional
from schemadiff.core import TableDiff, ChangeType


def filter_diffs(
    diffs: List[TableDiff],
    tables: Optional[List[str]] = None,
    change_types: Optional[List[ChangeType]] = None,
    exclude_tables: Optional[List[str]] = None,
) -> List[TableDiff]:
    """Filter a list of TableDiff objects by table name and/or change type.

    Args:
        diffs: List of TableDiff objects to filter.
        tables: If provided, only include diffs for these table names.
        change_types: If provided, only include diffs matching these ChangeType values.
        exclude_tables: If provided, exclude diffs for these table names.

    Returns:
        A filtered list of TableDiff objects.
    """
    result = list(diffs)

    if tables is not None:
        normalized = [t.lower() for t in tables]
        result = [d for d in result if d.table_name.lower() in normalized]

    if exclude_tables is not None:
        normalized_exclude = [t.lower() for t in exclude_tables]
        result = [d for d in result if d.table_name.lower() not in normalized_exclude]

    if change_types is not None:
        result = [d for d in result if d.change_type in change_types]

    return result


def filter_by_pattern(diffs: List[TableDiff], pattern: str) -> List[TableDiff]:
    """Filter diffs where the table name contains the given substring (case-insensitive).

    Args:
        diffs: List of TableDiff objects to filter.
        pattern: Substring to match against table names.

    Returns:
        A filtered list of TableDiff objects.
    """
    pattern_lower = pattern.lower()
    return [d for d in diffs if pattern_lower in d.table_name.lower()]
