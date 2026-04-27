"""Validates schema snapshots for structural correctness before diffing."""

from typing import Any

REQUIRED_TOP_LEVEL_KEYS = {"tables"}
REQUIRED_COLUMN_KEYS = {"type"}
VALID_COLUMN_TYPES = {
    "integer", "bigint", "smallint", "serial", "bigserial",
    "varchar", "text", "char",
    "boolean",
    "float", "double precision", "numeric", "decimal",
    "date", "timestamp", "timestamptz", "time",
    "json", "jsonb",
    "uuid",
    "bytea",
}


class ValidationError(Exception):
    """Raised when a schema snapshot fails validation."""
    pass


def validate_snapshot_dict(data: Any, source: str = "<unknown>") -> None:
    """Validate a raw snapshot dictionary.

    Args:
        data: The parsed snapshot data.
        source: A label used in error messages (e.g. filename).

    Raises:
        ValidationError: If the snapshot structure is invalid.
    """
    if not isinstance(data, dict):
        raise ValidationError(f"{source}: snapshot must be a JSON object, got {type(data).__name__}")

    missing = REQUIRED_TOP_LEVEL_KEYS - data.keys()
    if missing:
        raise ValidationError(f"{source}: missing required keys: {sorted(missing)}")

    tables = data["tables"]
    if not isinstance(tables, dict):
        raise ValidationError(f"{source}: 'tables' must be an object, got {type(tables).__name__}")

    for table_name, table_def in tables.items():
        _validate_table(table_name, table_def, source)


def _validate_table(table_name: str, table_def: Any, source: str) -> None:
    if not isinstance(table_def, dict):
        raise ValidationError(
            f"{source}: table '{table_name}' must be an object, got {type(table_def).__name__}"
        )

    columns = table_def.get("columns", {})
    if not isinstance(columns, dict):
        raise ValidationError(
            f"{source}: table '{table_name}' columns must be an object"
        )

    for col_name, col_def in columns.items():
        _validate_column(table_name, col_name, col_def, source)


def _validate_column(table_name: str, col_name: str, col_def: Any, source: str) -> None:
    if not isinstance(col_def, dict):
        raise ValidationError(
            f"{source}: column '{table_name}.{col_name}' must be an object"
        )

    missing = REQUIRED_COLUMN_KEYS - col_def.keys()
    if missing:
        raise ValidationError(
            f"{source}: column '{table_name}.{col_name}' missing keys: {sorted(missing)}"
        )

    col_type = col_def["type"].lower().split("(")[0].strip()
    if col_type not in VALID_COLUMN_TYPES:
        raise ValidationError(
            f"{source}: column '{table_name}.{col_name}' has unknown type '{col_def['type']}'"
        )
