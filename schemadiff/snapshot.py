"""Schema snapshot loading and parsing utilities."""

import json
from pathlib import Path
from typing import Any


class SchemaSnapshot:
    """Represents a parsed database schema snapshot."""

    def __init__(self, tables: dict[str, dict[str, Any]], source: str = ""):
        self.tables = tables
        self.source = source

    def table_names(self) -> set[str]:
        return set(self.tables.keys())

    def get_table(self, name: str) -> dict[str, Any] | None:
        return self.tables.get(name)

    def __repr__(self) -> str:
        return f"SchemaSnapshot(tables={list(self.tables.keys())}, source={self.source!r})"


def load_snapshot(path: str | Path) -> SchemaSnapshot:
    """Load a schema snapshot from a JSON file.

    Expected format:
    {
        "tables": {
            "users": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": false, "default": null},
                    "email": {"type": "VARCHAR(255)", "nullable": false, "default": null}
                },
                "indexes": [...],
                "primary_key": ["id"]
            }
        }
    }
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot file not found: {path}")
    if path.suffix not in (".json",):
        raise ValueError(f"Unsupported snapshot format: {path.suffix}")

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        raise ValueError("Snapshot root must be a JSON object")

    tables = raw.get("tables", {})
    if not isinstance(tables, dict):
        raise ValueError("'tables' must be a JSON object")

    return SchemaSnapshot(tables=tables, source=str(path))


def load_snapshot_from_dict(data: dict[str, Any], source: str = "<dict>") -> SchemaSnapshot:
    """Load a schema snapshot from an already-parsed dictionary."""
    tables = data.get("tables", {})
    if not isinstance(tables, dict):
        raise ValueError("'tables' must be a dict")
    return SchemaSnapshot(tables=tables, source=source)
