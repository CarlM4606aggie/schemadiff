"""High-level differ: compares two snapshots and produces a patch script."""

from typing import Optional
from schemadiff.snapshot import SchemaSnapshot
from schemadiff.comparator import compare_snapshots
from schemadiff.filter import filter_diffs
from schemadiff.patcher import generate_patch


def diff_and_patch(
    snapshot_a: SchemaSnapshot,
    snapshot_b: SchemaSnapshot,
    tables: Optional[list] = None,
    change_types: Optional[list] = None,
) -> str:
    """
    Compare two snapshots and return a SQL patch script.

    Optionally filter by table names or change types before generating patch.

    Args:
        snapshot_a: The baseline (older) snapshot.
        snapshot_b: The target (newer) snapshot.
        tables: Optional list of table name patterns to include.
        change_types: Optional list of ChangeType values to include.

    Returns:
        A SQL patch script as a string.
    """
    if snapshot_a is None or snapshot_b is None:
        raise ValueError("Both snapshot_a and snapshot_b must be provided.")

    diffs = compare_snapshots(snapshot_a, snapshot_b)

    if tables or change_types:
        diffs = filter_diffs(
            diffs,
            table_names=tables,
            change_types=change_types,
        )

    return generate_patch(diffs)


def diff_summary_and_patch(
    snapshot_a: SchemaSnapshot,
    snapshot_b: SchemaSnapshot,
) -> dict:
    """
    Return both a summary dict and a SQL patch script.

    Args:
        snapshot_a: The baseline (older) snapshot.
        snapshot_b: The target (newer) snapshot.

    Returns:
        dict with keys 'total_changes', 'patch'
    """
    if snapshot_a is None or snapshot_b is None:
        raise ValueError("Both snapshot_a and snapshot_b must be provided.")

    diffs = compare_snapshots(snapshot_a, snapshot_b)
    patch = generate_patch(diffs)
    return {
        "total_changes": len(diffs),
        "patch": patch,
    }
