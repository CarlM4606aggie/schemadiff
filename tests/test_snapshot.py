"""Tests for schemadiff.snapshot module."""

import json
import pytest
from pathlib import Path

from schemadiff.snapshot import load_snapshot, load_snapshot_from_dict, SchemaSnapshot

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_load_snapshot_from_file():
    snapshot = load_snapshot(FIXTURES_DIR / "snapshot_v1.json")
    assert isinstance(snapshot, SchemaSnapshot)
    assert "users" in snapshot.table_names()
    assert "posts" in snapshot.table_names()
    assert snapshot.source.endswith("snapshot_v1.json")


def test_snapshot_get_table():
    snapshot = load_snapshot(FIXTURES_DIR / "snapshot_v1.json")
    users = snapshot.get_table("users")
    assert users is not None
    assert "columns" in users
    assert "id" in users["columns"]
    assert users["columns"]["id"]["type"] == "INTEGER"


def test_snapshot_get_missing_table_returns_none():
    snapshot = load_snapshot(FIXTURES_DIR / "snapshot_v1.json")
    assert snapshot.get_table("nonexistent") is None


def test_load_snapshot_file_not_found():
    with pytest.raises(FileNotFoundError, match="Snapshot file not found"):
        load_snapshot("/tmp/does_not_exist_xyz.json")


def test_load_snapshot_unsupported_format(tmp_path):
    bad_file = tmp_path / "schema.yaml"
    bad_file.write_text("tables: {}")
    with pytest.raises(ValueError, match="Unsupported snapshot format"):
        load_snapshot(bad_file)


def test_load_snapshot_invalid_root(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps(["not", "an", "object"]))
    with pytest.raises(ValueError, match="root must be a JSON object"):
        load_snapshot(bad_file)


def test_load_snapshot_from_dict():
    data = {
        "tables": {
            "orders": {
                "columns": {
                    "id": {"type": "INTEGER", "nullable": False, "default": None}
                },
                "indexes": [],
                "primary_key": ["id"]
            }
        }
    }
    snapshot = load_snapshot_from_dict(data, source="test")
    assert "orders" in snapshot.table_names()
    assert snapshot.source == "test"


def test_load_snapshot_from_dict_missing_tables():
    snapshot = load_snapshot_from_dict({}, source="empty")
    assert snapshot.table_names() == set()


def test_snapshot_repr():
    snapshot = load_snapshot_from_dict({"tables": {"foo": {}}}, source="test")
    assert "foo" in repr(snapshot)
    assert "test" in repr(snapshot)
