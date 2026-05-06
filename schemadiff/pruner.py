"""Pruner: removes stale or irrelevant diffs based on configurable criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from schemadiff.core import TableDiff, ChangeType


@dataclass
class PruneOptions:
    """Configuration for pruning behaviour."""
    exclude_change_types: List[ChangeType] = field(default_factory=list)
    exclude_table_prefixes: List[str] = field(default_factory=list)
    max_column_changes: Optional[int] = None
    keep_only_breaking: bool = False


_BREAKING_TYPES = {ChangeType.DROPPED, ChangeType.MODIFIED}


def _is_breaking(diff: TableDiff) -> bool:
    """Return True if the diff is considered a breaking change."""
    if diff.change_type == ChangeType.DROPPED:
        return True
    if diff.change_type == ChangeType.MODIFIED:
        for col in diff.column_diffs:
            if col.change_type in (ChangeType.DROPPED, ChangeType.MODIFIED):
                return True
    return False


def _matches_prefix(table_name: str, prefixes: List[str]) -> bool:
    lower = table_name.lower()
    return any(lower.startswith(p.lower()) for p in prefixes)


def prune_diffs(diffs: List[TableDiff], options: Optional[PruneOptions] = None) -> List[TableDiff]:
    """Return a filtered list of diffs according to *options*.

    Args:
        diffs: The full list of TableDiff objects to prune.
        options: A PruneOptions instance controlling which diffs are removed.
                 If *None*, the original list is returned unchanged.

    Returns:
        A new list containing only the diffs that survive pruning.
    """
    if options is None:
        return list(diffs)

    result: List[TableDiff] = []
    for diff in diffs:
        if diff.change_type in options.exclude_change_types:
            continue
        if options.exclude_table_prefixes and _matches_prefix(diff.table_name, options.exclude_table_prefixes):
            continue
        if options.max_column_changes is not None:
            if len(diff.column_diffs) > options.max_column_changes:
                continue
        if options.keep_only_breaking and not _is_breaking(diff):
            continue
        result.append(diff)
    return result


def prune_summary(original: List[TableDiff], pruned: List[TableDiff]) -> str:
    """Return a human-readable summary of what was pruned."""
    removed = len(original) - len(pruned)
    if removed == 0:
        return "Pruner: no diffs were removed."
    return (
        f"Pruner: removed {removed} of {len(original)} diff(s); "
        f"{len(pruned)} remaining."
    )
