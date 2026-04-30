"""Baseline management: save and compare diffs against a known-good baseline."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from schemadiff.core import TableDiff, ChangeType


@dataclass
class BaselineEntry:
    table_name: str
    change_type: str

    def to_dict(self) -> dict:
        return {"table_name": self.table_name, "change_type": self.change_type}

    @classmethod
    def from_dict(cls, data: dict) -> "BaselineEntry":
        return cls(table_name=data["table_name"], change_type=data["change_type"])


@dataclass
class Baseline:
    entries: List[BaselineEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    @classmethod
    def from_dict(cls, data: dict) -> "Baseline":
        entries = [BaselineEntry.from_dict(e) for e in data.get("entries", [])]
        return cls(entries=entries)

    def _key_set(self) -> set:
        return {(e.table_name, e.change_type) for e in self.entries}


def build_baseline(diffs: List[TableDiff]) -> Baseline:
    """Create a Baseline from a list of TableDiff objects."""
    entries = [
        BaselineEntry(
            table_name=d.table_name,
            change_type=d.change_type.value,
        )
        for d in diffs
    ]
    return Baseline(entries=entries)


def save_baseline(baseline: Baseline, path: str) -> None:
    """Persist a baseline to a JSON file."""
    Path(path).write_text(json.dumps(baseline.to_dict(), indent=2))


def load_baseline(path: str) -> Baseline:
    """Load a baseline from a JSON file."""
    data = json.loads(Path(path).read_text())
    return Baseline.from_dict(data)


def filter_new_diffs(diffs: List[TableDiff], baseline: Baseline) -> List[TableDiff]:
    """Return only diffs that are NOT present in the baseline."""
    known = baseline._key_set()
    return [
        d for d in diffs
        if (d.table_name, d.change_type.value) not in known
    ]


def is_clean(diffs: List[TableDiff], baseline: Baseline) -> bool:
    """Return True if all diffs are accounted for in the baseline."""
    return len(filter_new_diffs(diffs, baseline)) == 0
