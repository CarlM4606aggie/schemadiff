"""Cache: stores and retrieves digest-keyed diff results to avoid redundant comparisons."""

import json
import os
from typing import Optional, Dict, Any

from schemadiff.digester import digest_snapshot
from schemadiff.snapshot import SchemaSnapshot

_CACHE_VERSION = 1


class DiffCache:
    """Simple file-backed cache keyed by snapshot pair digests."""

    def __init__(self, cache_path: str = ".schemadiff_cache.json"):
        self.cache_path = cache_path
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("version") == _CACHE_VERSION:
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {"version": _CACHE_VERSION, "entries": {}}

    def _save(self) -> None:
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    @staticmethod
    def make_key(snap_a: SchemaSnapshot, snap_b: SchemaSnapshot) -> str:
        """Build a deterministic cache key from two snapshots."""
        ha = digest_snapshot(snap_a)
        hb = digest_snapshot(snap_b)
        return f"{ha}:{hb}"

    def get(self, key: str) -> Optional[str]:
        """Return cached diff text for key, or None if missing."""
        return self._data["entries"].get(key)

    def set(self, key: str, value: str) -> None:
        """Store diff text under key and persist to disk."""
        self._data["entries"][key] = value
        self._save()

    def has(self, key: str) -> bool:
        return key in self._data["entries"]

    def invalidate(self, key: str) -> bool:
        """Remove a single entry. Returns True if it existed."""
        if key in self._data["entries"]:
            del self._data["entries"][key]
            self._save()
            return True
        return False

    def clear(self) -> int:
        """Remove all cached entries. Returns count removed."""
        count = len(self._data["entries"])
        self._data["entries"] = {}
        self._save()
        return count

    def __len__(self) -> int:
        return len(self._data["entries"])

    def __repr__(self) -> str:
        return f"DiffCache(path={self.cache_path!r}, entries={len(self)})"
