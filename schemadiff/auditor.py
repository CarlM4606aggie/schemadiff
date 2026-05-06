"""Audit trail for schema diff operations — records who compared what and when."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp: str
    user: str
    snapshot_a: str
    snapshot_b: str
    diff_count: int
    change_types: List[str]
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "user": self.user,
            "snapshot_a": self.snapshot_a,
            "snapshot_b": self.snapshot_b,
            "diff_count": self.diff_count,
            "change_types": self.change_types,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEntry":
        return cls(
            timestamp=data["timestamp"],
            user=data["user"],
            snapshot_a=data["snapshot_a"],
            snapshot_b=data["snapshot_b"],
            diff_count=data["diff_count"],
            change_types=data.get("change_types", []),
            note=data.get("note"),
        )


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "AuditLog":
        return cls(entries=[AuditEntry.from_dict(e) for e in data.get("entries", [])])


def _current_user() -> str:
    return os.environ.get("SCHEMADIFF_USER") or os.environ.get("USER") or "unknown"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_diff(diffs: list, snapshot_a: str, snapshot_b: str, note: Optional[str] = None) -> AuditEntry:
    """Build an AuditEntry from a completed diff operation."""
    change_types = sorted({d.change_type.value for d in diffs})
    return AuditEntry(
        timestamp=_now_iso(),
        user=_current_user(),
        snapshot_a=snapshot_a,
        snapshot_b=snapshot_b,
        diff_count=len(diffs),
        change_types=change_types,
        note=note,
    )


def load_audit_log(path: str) -> AuditLog:
    """Load an audit log from a JSON file, returning empty log if missing."""
    if not os.path.exists(path):
        return AuditLog()
    with open(path, "r", encoding="utf-8") as fh:
        return AuditLog.from_dict(json.load(fh))


def save_audit_log(log: AuditLog, path: str) -> None:
    """Persist an audit log to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(log.to_dict(), fh, indent=2)
