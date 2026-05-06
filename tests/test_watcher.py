"""Tests for schemadiff.watcher."""

import json
import time
import threading
from pathlib import Path

import pytest

from schemadiff.watcher import WatchEvent, watch_snapshot, _get_mtime
from schemadiff.core import TableDiff, ChangeType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(name: str = "users") -> TableDiff:
    return TableDiff(table_name=name, change_type=ChangeType.ADDED, column_diffs=[])


_SNAPSHOT_V1 = {
    "tables": {
        "users": {
            "columns": {
                "id": {"type": "integer", "nullable": False}
            }
        }
    }
}

_SNAPSHOT_V2 = {
    "tables": {
        "users": {
            "columns": {
                "id": {"type": "integer", "nullable": False},
                "email": {"type": "varchar", "nullable": True}
            }
        }
    }
}


# ---------------------------------------------------------------------------
# WatchEvent
# ---------------------------------------------------------------------------

def test_watch_event_has_changes_true():
    event = WatchEvent("a.json", "b.json", [_make_diff()])
    assert event.has_changes is True


def test_watch_event_has_changes_false():
    event = WatchEvent("a.json", "b.json", [])
    assert event.has_changes is False


def test_watch_event_repr_contains_diff_count():
    event = WatchEvent("a.json", "b.json", [_make_diff(), _make_diff("orders")])
    assert "2" in repr(event)


def test_watch_event_timestamp_is_set_automatically():
    before = time.time()
    event = WatchEvent("a.json", "b.json", [])
    after = time.time()
    assert before <= event.timestamp <= after


def test_watch_event_stores_snapshot_paths():
    """WatchEvent should preserve the base and current snapshot paths as provided."""
    event = WatchEvent("base.json", "current.json", [])
    assert event.base_snapshot == "base.json"
    assert event.current_snapshot == "current.json"


# ---------------------------------------------------------------------------
# _get_mtime
# ---------------------------------------------------------------------------

def test_get_mtime_returns_float_for_existing_file(tmp_path):
    f = tmp_path / "snap.json"
    f.write_text("{}")
    result = _get_mtime(str(f))
    assert isinstance(result, float)


def test_get_mtime_returns_none_for_missing_file():
    assert _get_mtime("/nonexistent/path/file.json") is None


# ---------------------------------------------------------------------------
# watch_snapshot integration
# ---------------------------------------------------------------------------

def test_watch_snapshot_detects_file_change(tmp_path):
    base = tmp_path / "v1.json"
    current = tmp_path / "v2.json"

    base.write_text(json.dumps(_SNAPSHOT_V1))
    current.write_text(json.dumps(_SNAPSHOT_V1))

    collected: list = []

    def _callback(event: WatchEvent) -> None:
        collected.append(event)

    def _update_file():
        time.sleep(0.05)
        current.write_text(json.dumps(_SNAPSHOT_V2))
        # bump mtime explicitly for fast filesystems
        t = time.time() + 1
        import os
        os.utime(str(current), (t, t))

    thread = threading.Thr
