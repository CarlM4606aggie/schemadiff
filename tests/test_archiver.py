"""Tests for schemadiff.archiver."""

import json
import os
import pytest

from schemadiff.archiver import (
    ArchiveEntry,
    DiffArchive,
    archive_diffs,
    load_archive,
    save_archive,
)
from schemadiff.core import ChangeType, TableDiff, ColumnDiff


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_added_table(name: str = "users") -> TableDiff:
    return TableDiff(
        table_name=name,
        change_type=ChangeType.ADDED,
        column_diffs=[],
    )


def _make_dropped_table(name: str = "orders") -> TableDiff:
    return TableDiff(
        table_name=name,
        change_type=ChangeType.DROPPED,
        column_diffs=[],
    )


@pytest.fixture()
def sample_diffs():
    return [_make_added_table("users"), _make_dropped_table("orders")]


@pytest.fixture()
def sample_archive(sample_diffs):
    archive = DiffArchive()
    archive_diffs(sample_diffs, label="v1", archive=archive)
    archive_diffs(sample_diffs, label="v2", archive=archive)
    return archive


# ---------------------------------------------------------------------------
# ArchiveEntry tests
# ---------------------------------------------------------------------------


def test_archive_entry_to_dict_has_required_keys():
    entry = ArchiveEntry(
        timestamp="2024-01-01T00:00:00+00:00",
        label="release-1",
        digest="abc123",
        total_changes=3,
        diffs=[],
    )
    d = entry.to_dict()
    assert set(d.keys()) == {"timestamp", "label", "digest", "total_changes", "diffs"}


def test_archive_entry_roundtrip():
    entry = ArchiveEntry(
        timestamp="2024-06-01T12:00:00+00:00",
        label="sprint-42",
        digest="deadbeef",
        total_changes=7,
        diffs=[{"table": "foo", "change_type": "added"}],
    )
    restored = ArchiveEntry.from_dict(entry.to_dict())
    assert restored.label == entry.label
    assert restored.digest == entry.digest
    assert restored.total_changes == entry.total_changes


# ---------------------------------------------------------------------------
# DiffArchive tests
# ---------------------------------------------------------------------------


def test_diff_archive_starts_empty():
    archive = DiffArchive()
    assert archive.entries == []


def test_diff_archive_find_by_label(sample_archive):
    entry = sample_archive.find_by_label("v1")
    assert entry is not None
    assert entry.label == "v1"


def test_diff_archive_find_by_label_missing_returns_none(sample_archive):
    assert sample_archive.find_by_label("nonexistent") is None


def test_diff_archive_find_by_digest(sample_archive):
    digest = sample_archive.entries[0].digest
    entry = sample_archive.find_by_digest(digest)
    assert entry is not None
    assert entry.digest == digest


def test_diff_archive_roundtrip(sample_archive):
    restored = DiffArchive.from_dict(sample_archive.to_dict())
    assert len(restored.entries) == len(sample_archive.entries)
    assert restored.entries[0].label == sample_archive.entries[0].label


# ---------------------------------------------------------------------------
# archive_diffs tests
# ---------------------------------------------------------------------------


def test_archive_diffs_returns_entry(sample_diffs):
    entry = archive_diffs(sample_diffs, label="test-run")
    assert isinstance(entry, ArchiveEntry)


def test_archive_diffs_label_stored(sample_diffs):
    entry = archive_diffs(sample_diffs, label="my-label")
    assert entry.label == "my-label"


def test_archive_diffs_digest_is_string(sample_diffs):
    entry = archive_diffs(sample_diffs, label="x")
    assert isinstance(entry.digest, str) and len(entry.digest) > 0


def test_archive_diffs_adds_to_provided_archive(sample_diffs):
    archive = DiffArchive()
    archive_diffs(sample_diffs, label="a", archive=archive)
    archive_diffs(sample_diffs, label="b", archive=archive)
    assert len(archive.entries) == 2


def test_archive_diffs_total_changes_positive(sample_diffs):
    entry = archive_diffs(sample_diffs, label="chk")
    assert entry.total_changes > 0


# ---------------------------------------------------------------------------
# save / load tests
# ---------------------------------------------------------------------------


def test_save_and_load_archive(tmp_path, sample_diffs):
    path = str(tmp_path / "archive.json")
    archive = DiffArchive()
    archive_diffs(sample_diffs, label="persist", archive=archive)
    save_archive(archive, path)
    loaded = load_archive(path)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].label == "persist"


def test_load_archive_missing_file_returns_empty(tmp_path):
    path = str(tmp_path / "missing.json")
    archive = load_archive(path)
    assert isinstance(archive, DiffArchive)
    assert archive.entries == []


def test_save_archive_creates_valid_json(tmp_path, sample_diffs):
    path = str(tmp_path / "out.json")
    archive = DiffArchive()
    archive_diffs(sample_diffs, label="json-check", archive=archive)
    save_archive(archive, path)
    with open(path) as fh:
        data = json.load(fh)
    assert "entries" in data
    assert isinstance(data["entries"], list)
