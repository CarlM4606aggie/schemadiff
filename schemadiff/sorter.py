"""Sorting utilities for schema diffs."""

from typing import List, Optional
from schemadiff.core import TableDiff, ChangeType


SORT_KEYS = ("table", "change_type", "column_count")


def sort_diffs(
    diffs: List[TableDiff],
    by: str = "table",
    reverse: bool = False,
) -> List[TableDiff]:
    """Return a sorted copy of the diff list.

    Args:
        diffs: List of TableDiff objects to sort.
        by: Sort key — one of 'table', 'change_type', or 'column_count'.
        reverse: If True, sort in descending order.

    Returns:
        A new sorted list of TableDiff objects.

    Raises:
        ValueError: If an unsupported sort key is provided.
    """
    if by not in SORT_KEYS:
        raise ValueError(
            f"Unsupported sort key '{by}'. Choose from: {', '.join(SORT_KEYS)}"
        )

    key_fn = _make_key_fn(by)
    return sorted(diffs, key=key_fn, reverse=reverse)


def _make_key_fn(by: str):
    """Return a key function for the given sort field."""
    if by == "table":
        return lambda d: d.table_name.lower()
    if by == "change_type":
        # Sort by the string value of the ChangeType enum for consistency
        return lambda d: d.change_type.value
    if by == "column_count":
        return lambda d: len(d.column_diffs)
    raise ValueError(f"Unknown sort key: {by}")


def group_by_change_type(
    diffs: List[TableDiff],
) -> dict:
    """Group diffs by their ChangeType.

    Args:
        diffs: List of TableDiff objects.

    Returns:
        A dict mapping ChangeType -> list of TableDiff.
    """
    groups: dict = {ct: [] for ct in ChangeType}
    for diff in diffs:
        groups[diff.change_type].append(diff)
    # Remove empty groups
    return {ct: items for ct, items in groups.items() if items}
