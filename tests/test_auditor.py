"""Tests for schemadiff.auditor and schemadiff.audit_reporter."""

import json
import os
from unittest.mock import patch

import pytest

from schemadiff.auditor import (
    AuditEntry,
    AuditLog,
    load_audit_log,
    record_diff,
    save_audit_log,
)
from schemadiff.audit_reporter import diff_entries, render_audit_markdown, render_audit_text
from schemadiff.core import ChangeType, TableDiff


def _make_diff(name: str, change_type: ChangeType) -> TableDiff:
    return TableDiff(table_name=name, change_type=change_type, column_diffs=[])


@pytest.fixture
def sample_entry() -> AuditEntry:
    return AuditEntry(
        timestamp="2024-01-01T00:00:00+00:00",
        user="alice",
        snapshot_a="prod_v1",
        snapshot_b="prod_v2",
        diff_count=3,
        change_types=["added", "modified"],
        note="routine deploy",
    )


@pytest.fixture
def sample_log(sample_entry) -> AuditLog:
    log = AuditLog()
    log.add(sample_entry)
    return log


def test_audit_entry_to_dict_has_required_keys(sample_entry):
    d = sample_entry.to_dict()
    for key in ("timestamp", "user", "snapshot_a", "snapshot_b", "diff_count", "change_types"):
        assert key in d


def test_audit_entry_round_trip(sample_entry):
    restored = AuditEntry.from_dict(sample_entry.to_dict())
    assert restored.user == sample_entry.user
    assert restored.diff_count == sample_entry.diff_count
    assert restored.note == sample_entry.note


def test_audit_log_add_increases_entry_count(sample_entry):
    log = AuditLog()
    log.add(sample_entry)
    assert len(log.entries) == 1


def test_audit_log_round_trip(sample_log):
    restored = AuditLog.from_dict(sample_log.to_dict())
    assert len(restored.entries) == len(sample_log.entries)
    assert restored.entries[0].user == "alice"


def test_record_diff_captures_change_types():
    diffs = [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.DROPPED),
    ]
    entry = record_diff(diffs, "snap_a", "snap_b")
    assert "added" in entry.change_types
    assert "dropped" in entry.change_types
    assert entry.diff_count == 2


def test_record_diff_uses_env_user():
    with patch.dict(os.environ, {"SCHEMADIFF_USER": "ci-bot"}):
        entry = record_diff([], "a", "b")
    assert entry.user == "ci-bot"


def test_save_and_load_audit_log(tmp_path, sample_log):
    path = str(tmp_path / "audit.json")
    save_audit_log(sample_log, path)
    loaded = load_audit_log(path)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].snapshot_a == "prod_v1"


def test_load_audit_log_missing_file_returns_empty(tmp_path):
    log = load_audit_log(str(tmp_path / "nonexistent.json"))
    assert log.entries == []


def test_render_audit_text_contains_user(sample_log):
    output = render_audit_text(sample_log)
    assert "alice" in output


def test_render_audit_text_empty_log():
    output = render_audit_text(AuditLog())
    assert "No audit entries" in output


def test_render_audit_markdown_contains_header(sample_log):
    output = render_audit_markdown(sample_log)
    assert "Timestamp" in output
    assert "alice" in output


def test_diff_entries_filters_by_snapshot_a(sample_log):
    results = diff_entries(sample_log, snapshot_a="prod_v1")
    assert len(results) == 1


def test_diff_entries_no_match_returns_empty(sample_log):
    results = diff_entries(sample_log, snapshot_a="staging")
    assert results == []
