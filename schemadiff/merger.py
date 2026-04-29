"""Merge two schema snapshots into a single combined snapshot."""

from typing import Optional
from schemadiff.snapshot import SchemaSnapshot


def merge_snapshots(
    base: SchemaSnapshot,
    override: SchemaSnapshot,
    conflict: str = "override",
) -> SchemaSnapshot:
    """Merge two SchemaSnapshots into one.

    Args:
        base: The base snapshot whose tables are used as the starting point.
        override: The snapshot whose tables take precedence on conflict.
        conflict: Strategy for handling table name collisions.
                  - "override": tables in *override* replace those in *base*.
                  - "keep": tables in *base* are kept when a name collision occurs.
                  - "error": raise ValueError on any table name collision.

    Returns:
        A new SchemaSnapshot containing the merged table definitions.

    Raises:
        ValueError: If *conflict* is ``"error"`` and overlapping table names exist,
                    or if an unknown conflict strategy is supplied.
    """
    if conflict not in ("override", "keep", "error"):
        raise ValueError(
            f"Unknown conflict strategy {conflict!r}. "
            "Choose one of: 'override', 'keep', 'error'."
        )

    base_names = set(base.table_names())
    override_names = set(override.table_names())
    shared = base_names & override_names

    if conflict == "error" and shared:
        raise ValueError(
            f"Table name collision(s) detected: {sorted(shared)}. "
            "Use conflict='override' or conflict='keep' to resolve."
        )

    merged_tables: dict = {}

    for name in base.table_names():
        merged_tables[name] = base.get_table(name)

    for name in override.table_names():
        if name in shared and conflict == "keep":
            continue
        merged_tables[name] = override.get_table(name)

    return _build_snapshot(merged_tables)


def _build_snapshot(tables: dict) -> SchemaSnapshot:
    """Construct a SchemaSnapshot from a plain dict of table definitions."""
    raw = {"tables": tables}
    return SchemaSnapshot(raw)
