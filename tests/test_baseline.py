"""Tests for schemadiff.baseline module."""

import json
import pytest
from pathlib import Path

from schemadiff.baseline import (
    BaselineEntry,
    Baseline,
    build_baseline,
    save_baseline,
    load_baseline,
    filter_new_diffs,
    is_clean,
)
from schemadiff.core import TableDiff, ChangeType


def _make_diff(name: str, change_type: ChangeType) -> TableDiff:
    return TableDiff(table_name=name, change_type=change_type, column_diffs=[])


@pytest.fixture
def sample_diffs():
    return [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.MODIFIED),
        _make_diff("products", ChangeType.DROPPED),
    ]


@pytest.fixture
def sample_baseline(sample_diffs):
    return build_baseline(sample_diffs)


def test_build_baseline_returns_baseline_instance(sample_diffs):
    result = build_baseline(sample_diffs)
    assert isinstance(result, Baseline)


def test_build_baseline_entry_count(sample_diffs):
    result = build_baseline(sample_diffs)
    assert len(result.entries) == 3


def test_build_baseline_entry_fields(sample_diffs):
    result = build_baseline(sample_diffs)
    entry = result.entries[0]
    assert isinstance(entry, BaselineEntry)
    assert entry.table_name == "users"
    assert entry.change_type == ChangeType.ADDED.value


def test_baseline_to_dict_structure(sample_baseline):
    d = sample_baseline.to_dict()
    assert "entries" in d
    assert isinstance(d["entries"], list)
    assert d["entries"][0]["table_name"] == "users"


def test_baseline_round_trip(sample_baseline):
    d = sample_baseline.to_dict()
    restored = Baseline.from_dict(d)
    assert restored._key_set() == sample_baseline._key_set()


def test_save_and_load_baseline(tmp_path, sample_baseline):
    path = str(tmp_path / "baseline.json")
    save_baseline(sample_baseline, path)
    loaded = load_baseline(path)
    assert loaded._key_set() == sample_baseline._key_set()


def test_save_baseline_creates_valid_json(tmp_path, sample_baseline):
    path = str(tmp_path / "baseline.json")
    save_baseline(sample_baseline, path)
    content = json.loads(Path(path).read_text())
    assert "entries" in content


def test_filter_new_diffs_removes_known(sample_diffs, sample_baseline):
    result = filter_new_diffs(sample_diffs, sample_baseline)
    assert result == []


def test_filter_new_diffs_returns_unknown():
    baseline = build_baseline([_make_diff("users", ChangeType.ADDED)])
    diffs = [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.MODIFIED),
    ]
    result = filter_new_diffs(diffs, baseline)
    assert len(result) == 1
    assert result[0].table_name == "orders"


def test_is_clean_true_when_all_known(sample_diffs, sample_baseline):
    assert is_clean(sample_diffs, sample_baseline) is True


def test_is_clean_false_when_new_diff_present():
    baseline = build_baseline([_make_diff("users", ChangeType.ADDED)])
    diffs = [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("logs", ChangeType.DROPPED),
    ]
    assert is_clean(diffs, baseline) is False


def test_empty_baseline_filter_returns_all(sample_diffs):
    empty = Baseline()
    result = filter_new_diffs(sample_diffs, empty)
    assert result == sample_diffs
