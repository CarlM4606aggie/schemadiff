"""Tests for schemadiff.snapshot."""

import json
import pytest
from pathlib import Path

from schemadiff.snapshot import SchemaSnapshot
from schemadiff.validator import ValidationError


FIXTURES = Path(__file__).parent / "fixtures"


def test_load_snapshot_from_file():
    snap = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    assert isinstance(snap, SchemaSnapshot)
    assert len(snap.table_names) > 0


def test_snapshot_get_table():
    snap = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    table = snap.get_table(snap.table_names[0])
    assert table is not None
    assert "columns" in table


def test_snapshot_get_missing_table_returns_none():
    snap = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    assert snap.get_table("nonexistent_table_xyz") is None


def test_load_snapshot_file_not_found():
    with pytest.raises(FileNotFoundError):
        SchemaSnapshot.from_file(FIXTURES / "does_not_exist.json")


def test_load_snapshot_unsupported_format(tmp_path):
    bad = tmp_path / "schema.yaml"
    bad.write_text("tables: {}")
    with pytest.raises(ValueError, match="Unsupported snapshot format"):
        SchemaSnapshot.from_file(bad)


def test_load_snapshot_invalid_json(tmp_path):
    bad = tmp_path / "schema.json"
    bad.write_text("{not valid json")
    with pytest.raises(ValueError, match="Invalid JSON"):
        SchemaSnapshot.from_file(bad)


def test_load_snapshot_invalid_structure():
    with pytest.raises(ValidationError, match="unknown type"):
        SchemaSnapshot.from_file(FIXTURES / "snapshot_invalid.json")


def test_from_dict_valid():
    data = {"tables": {"users": {"columns": {"id": {"type": "integer"}}}}}
    snap = SchemaSnapshot.from_dict(data, source="test")
    assert "users" in snap.table_names


def test_from_dict_invalid_raises():
    data = {"tables": {"users": {"columns": {"id": {"type": "faketype"}}}}}
    with pytest.raises(ValidationError):
        SchemaSnapshot.from_dict(data, source="test")


def test_snapshot_repr():
    snap = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    r = repr(snap)
    assert "SchemaSnapshot" in r
    assert "snapshot_v1.json" in r


def test_snapshot_equality():
    snap1 = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    snap2 = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    assert snap1 == snap2


def test_snapshot_inequality():
    snap1 = SchemaSnapshot.from_file(FIXTURES / "snapshot_v1.json")
    snap2 = SchemaSnapshot.from_file(FIXTURES / "snapshot_v2.json")
    assert snap1 != snap2
