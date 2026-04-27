"""Schema snapshot loading and representation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from schemadiff.validator import validate_snapshot_dict, ValidationError  # noqa: F401


class SchemaSnapshot:
    """Represents a database schema at a point in time."""

    def __init__(self, data: Dict[str, Any], source: str = "<unknown>") -> None:
        self._data = data
        self.source = source

    @property
    def table_names(self) -> List[str]:
        return list(self._data.get("tables", {}).keys())

    def get_table(self, name: str) -> Optional[Dict[str, Any]]:
        return self._data.get("tables", {}).get(name)

    def __repr__(self) -> str:
        return f"SchemaSnapshot(source={self.source!r}, tables={len(self.table_names)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SchemaSnapshot):
            return NotImplemented
        return self._data == other._data

    @classmethod
    def from_dict(cls, data: Dict[str, Any], source: str = "<dict>") -> "SchemaSnapshot":
        """Create a snapshot from a dictionary, validating structure first."""
        validate_snapshot_dict(data, source)
        return cls(data, source=source)

    @classmethod
    def from_file(cls, path: str | Path) -> "SchemaSnapshot":
        """Load a snapshot from a JSON file.

        Args:
            path: Path to the JSON snapshot file.

        Returns:
            A validated SchemaSnapshot instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is unsupported or JSON is invalid.
            ValidationError: If the snapshot structure is invalid.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Snapshot file not found: {path}")

        if path.suffix.lower() != ".json":
            raise ValueError(f"Unsupported snapshot format: {path.suffix!r}. Only .json is supported.")

        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in snapshot file {path}: {exc}") from exc

        validate_snapshot_dict(data, source=str(path))
        return cls(data, source=str(path))
