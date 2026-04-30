"""Tests for schemadiff.cache."""

import json
import os
import pytest
from unittest.mock import MagicMock, patch

from schemadiff.cache import DiffCache


def _make_snapshot(table_names, columns=None):
    snap = MagicMock()
    snap.table_names.return_value = table_names
    def get_table(name):
        return {"columns": columns or {"id": "int"}}
    snap.get_table.side_effect = get_table
    return snap


@pytest.fixture
def tmp_cache(tmp_path):
    path = str(tmp_path / "test_cache.json")
    return DiffCache(cache_path=path)


def test_cache_starts_empty(tmp_cache):
    assert len(tmp_cache) == 0


def test_cache_set_and_get(tmp_cache):
    tmp_cache.set("key1", "some diff output")
    assert tmp_cache.get("key1") == "some diff output"


def test_cache_has_returns_true_after_set(tmp_cache):
    tmp_cache.set("k", "v")
    assert tmp_cache.has("k") is True


def test_cache_has_returns_false_for_missing(tmp_cache):
    assert tmp_cache.has("nonexistent") is False


def test_cache_get_missing_returns_none(tmp_cache):
    assert tmp_cache.get("missing") is None


def test_cache_persists_to_disk(tmp_path):
    path = str(tmp_path / "persist.json")
    c1 = DiffCache(cache_path=path)
    c1.set("abc", "diff text")
    c2 = DiffCache(cache_path=path)
    assert c2.get("abc") == "diff text"


def test_cache_invalidate_removes_entry(tmp_cache):
    tmp_cache.set("x", "data")
    result = tmp_cache.invalidate("x")
    assert result is True
    assert tmp_cache.has("x") is False


def test_cache_invalidate_missing_returns_false(tmp_cache):
    assert tmp_cache.invalidate("ghost") is False


def test_cache_clear_removes_all(tmp_cache):
    tmp_cache.set("a", "1")
    tmp_cache.set("b", "2")
    count = tmp_cache.clear()
    assert count == 2
    assert len(tmp_cache) == 0


def test_make_key_is_deterministic():
    snap_a = _make_snapshot(["users"])
    snap_b = _make_snapshot(["orders"])
    k1 = DiffCache.make_key(snap_a, snap_b)
    k2 = DiffCache.make_key(snap_a, snap_b)
    assert k1 == k2


def test_make_key_differs_for_different_snapshots():
    snap_a = _make_snapshot(["users"])
    snap_b = _make_snapshot(["orders"])
    snap_c = _make_snapshot(["products"])
    assert DiffCache.make_key(snap_a, snap_b) != DiffCache.make_key(snap_a, snap_c)


def test_cache_repr(tmp_cache):
    tmp_cache.set("k", "v")
    r = repr(tmp_cache)
    assert "DiffCache" in r
    assert "entries=1" in r


def test_cache_loads_ignores_wrong_version(tmp_path):
    path = str(tmp_path / "bad_version.json")
    with open(path, "w") as f:
        json.dump({"version": 99, "entries": {"stale": "data"}}, f)
    c = DiffCache(cache_path=path)
    assert len(c) == 0
