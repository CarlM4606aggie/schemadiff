"""Normalize schema snapshots for consistent comparison.

Provides utilities to canonicalize column types, strip whitespace,
and lowercase identifiers so that cosmetic differences don't produce
spurious diffs.
"""

from __future__ import annotations

from typing import Dict, Any

from schemadiff.snapshot import SchemaSnapshot

# Map of common type aliases to a canonical form
_TYPE_ALIASES: Dict[str, str] = {
    "int": "integer",
    "int4": "integer",
    "int8": "bigint",
    "int2": "smallint",
    "bool": "boolean",
    "varchar": "character varying",
    "char": "character",
    "float4": "real",
    "float8": "double precision",
    "text": "text",
    "serial": "integer",
    "bigserial": "bigint",
}


def normalize_type(raw_type: str) -> str:
    """Return the canonical form of a SQL column type string."""
    cleaned = raw_type.strip().lower()
    # Strip trailing size qualifiers for alias lookup, e.g. "varchar(255)"
    base = cleaned.split("(")[0].strip()
    return _TYPE_ALIASES.get(base, cleaned)


def normalize_column(col: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new column dict with normalised field values."""
    return {
        "type": normalize_type(col.get("type", "")),
        "nullable": bool(col.get("nullable", True)),
        "default": col.get("default"),
    }


def normalize_snapshot(snapshot: SchemaSnapshot) -> SchemaSnapshot:
    """Return a new SchemaSnapshot with all column types normalised.

    The original snapshot is not mutated.
    """
    normalised_tables: Dict[str, Any] = {}
    for table_name in snapshot.table_names():
        table = snapshot.get_table(table_name)
        if table is None:
            continue
        normalised_columns = {
            col_name: normalize_column(col_def)
            for col_name, col_def in table.items()
        }
        normalised_tables[table_name] = normalised_columns

    return SchemaSnapshot({"tables": normalised_tables})
