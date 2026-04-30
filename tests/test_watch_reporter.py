"""Tests for schemadiff.watch_reporter."""

import time
import pytest

from schemadiff.watcher import WatchEvent
from schemadiff.watch_reporter import format_watch_event, print_watch_event
from schemadiff.core import TableDiff, ChangeType, ColumnDiff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _added_table(name: str = "users") -> TableDiff:
    return TableDiff(table_name=name, change_type=ChangeType.ADDED, column_diffs=[])


def _dropped_table(name: str = "legacy") -> TableDiff:
    return TableDiff(table_name=name, change_type=ChangeType.DROPPED, column_diffs=[])


def _modified_table(name: str = "orders") -> TableDiff:
    col = ColumnDiff(
        column_name="amount",
        change_type=ChangeType.MODIFIED,
        old_definition={"type": "integer", "nullable": True},
        new_definition={"type": "numeric", "nullable": True},
    )
    return TableDiff(table_name=name, change_type=ChangeType.MODIFIED, column_diffs=[col])


# ---------------------------------------------------------------------------
# format_watch_event
# ---------------------------------------------------------------------------

def test_format_watch_event_returns_string():
    event = WatchEvent("a.json", "b.json", [_added_table()])
    result = format_watch_event(event, use_color=False)
    assert isinstance(result, str)


def test_format_watch_event_no_changes_message():
    event = WatchEvent("a.json", "b.json", [])
    result = format_watch_event(event, use_color=False)
    assert "No schema differences" in result


def test_format_watch_event_contains_paths():
    event = WatchEvent("base.json", "current.json", [])
    result = format_watch_event(event, use_color=False)
    assert "base.json" in result
    assert "current.json" in result


def test_format_watch_event_added_count_shown():
    event = WatchEvent("a.json", "b.json", [_added_table(), _added_table("products")])
    result = format_watch_event(event, use_color=False)
    assert "+2 added" in result


def test_format_watch_event_dropped_count_shown():
    event = WatchEvent("a.json", "b.json", [_dropped_table()])
    result = format_watch_event(event, use_color=False)
    assert "-1 dropped" in result


def test_format_watch_event_modified_count_shown():
    event = WatchEvent("a.json", "b.json", [_modified_table()])
    result = format_watch_event(event, use_color=False)
    assert "~1 modified" in result


def test_format_watch_event_contains_timestamp():
    ts = time.mktime(time.strptime("2024-06-01 12:00:00", "%Y-%m-%d %H:%M:%S"))
    event = WatchEvent("a.json", "b.json", [], timestamp=ts)
    result = format_watch_event(event, use_color=False)
    assert "2024-06-01" in result


def test_format_watch_event_with_color_includes_ansi():
    event = WatchEvent("a.json", "b.json", [_added_table()])
    result = format_watch_event(event, use_color=True)
    assert "\033[" in result


def test_print_watch_event_runs_without_error(capsys):
    event = WatchEvent("a.json", "b.json", [_added_table()])
    print_watch_event(event, use_color=False)
    captured = capsys.readouterr()
    assert len(captured.out) > 0
