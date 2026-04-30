"""Archive and retrieve schema diff history entries."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from schemadiff.core import TableDiff
from schemadiff.digester import digest_diffs
from schemadiff.summary import build_summary


@dataclass
class ArchiveEntry:
    timestamp: str
    label: str
    digest: str
    total_changes: int
    diffs: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "label": self.label,
            "digest": self.digest,
            "total_changes": self.total_changes,
            "diffs": self.diffs,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ArchiveEntry":
        return cls(
            timestamp=data["timestamp"],
            label=data["label"],
            digest=data["digest"],
            total_changes=data["total_changes"],
            diffs=data.get("diffs", []),
        )


@dataclass
class DiffArchive:
    entries: List[ArchiveEntry] = field(default_factory=list)

    def add(self, entry: ArchiveEntry) -> None:
        self.entries.append(entry)

    def find_by_label(self, label: str) -> Optional[ArchiveEntry]:
        for entry in self.entries:
            if entry.label == label:
                return entry
        return None

    def find_by_digest(self, digest: str) -> Optional[ArchiveEntry]:
        for entry in self.entries:
            if entry.digest == digest:
                return entry
        return None

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "DiffArchive":
        entries = [ArchiveEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(entries=entries)


def archive_diffs(
    diffs: List[TableDiff],
    label: str,
    archive: Optional[DiffArchive] = None,
) -> ArchiveEntry:
    """Create an ArchiveEntry from a list of diffs and add it to the archive."""
    if archive is None:
        archive = DiffArchive()
    summary = build_summary(diffs)
    digest = digest_diffs(diffs)
    timestamp = datetime.now(timezone.utc).isoformat()
    entry = ArchiveEntry(
        timestamp=timestamp,
        label=label,
        digest=digest,
        total_changes=summary.total_column_changes + len(diffs),
        diffs=[{"table": d.table_name, "change_type": d.change_type.value} for d in diffs],
    )
    archive.add(entry)
    return entry


def save_archive(archive: DiffArchive, path: str) -> None:
    """Persist a DiffArchive to a JSON file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(archive.to_dict(), fh, indent=2)


def load_archive(path: str) -> DiffArchive:
    """Load a DiffArchive from a JSON file."""
    if not os.path.exists(path):
        return DiffArchive()
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return DiffArchive.from_dict(data)
