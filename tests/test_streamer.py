"""Tests for schemadiff.streamer."""

import pytest
from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.streamer import StreamOptions, collect_stream, stream_diffs


def _col(name="id", old_type=None, new_type="int", nullable=False):
    return ColumnDiff(
        column_name=name,
        old_type=old_type,
        new_type=new_type,
        nullable_changed=nullable,
    )


def _make_diff(table_name, change_type=ChangeType.ADDED, cols=None):
    return TableDiff(
        table_name=table_name,
        change_type=change_type,
        column_diffs=cols or [],
    )


@pytest.fixture
def mixed_diffs():
    return [
        _make_diff("users", ChangeType.ADDED),
        _make_diff("orders", ChangeType.DROPPED),
        _make_diff("products", ChangeType.MODIFIED, cols=[_col()]),
        _make_diff("user_sessions", ChangeType.ADDED),
        _make_diff("audit_log", ChangeType.DROPPED),
    ]


def test_stream_diffs_yields_all_by_default(mixed_diffs):
    result = list(stream_diffs(mixed_diffs))
    assert len(result) == 5


def test_stream_diffs_returns_generator(mixed_diffs):
    gen = stream_diffs(mixed_diffs)
    import types
    assert isinstance(gen, types.GeneratorType)


def test_filter_by_change_type_added(mixed_diffs):
    opts = StreamOptions(change_types=[ChangeType.ADDED])
    result = collect_stream(mixed_diffs, opts=opts)
    assert all(d.change_type == ChangeType.ADDED for d in result)
    assert len(result) == 2


def test_filter_by_change_type_dropped(mixed_diffs):
    opts = StreamOptions(change_types=[ChangeType.DROPPED])
    result = collect_stream(mixed_diffs, opts=opts)
    assert len(result) == 2


def test_filter_by_table_prefix(mixed_diffs):
    opts = StreamOptions(table_prefix="user")
    result = collect_stream(mixed_diffs, opts=opts)
    assert len(result) == 2
    assert all(d.table_name.lower().startswith("user") for d in result)


def test_filter_by_table_prefix_case_insensitive(mixed_diffs):
    opts = StreamOptions(table_prefix="USER")
    result = collect_stream(mixed_diffs, opts=opts)
    assert len(result) == 2


def test_limit_caps_output(mixed_diffs):
    opts = StreamOptions(limit=2)
    result = collect_stream(mixed_diffs, opts=opts)
    assert len(result) == 2


def test_limit_zero_returns_empty(mixed_diffs):
    opts = StreamOptions(limit=0)
    result = collect_stream(mixed_diffs, opts=opts)
    assert result == []


def test_transform_applied_to_each_diff(mixed_diffs):
    def mark(diff):
        diff.table_name = diff.table_name.upper()
        return diff

    result = collect_stream(mixed_diffs, transform=mark)
    assert all(d.table_name == d.table_name.upper() for d in result)


def test_combined_filter_and_limit(mixed_diffs):
    opts = StreamOptions(change_types=[ChangeType.ADDED], limit=1)
    result = collect_stream(mixed_diffs, opts=opts)
    assert len(result) == 1
    assert result[0].change_type == ChangeType.ADDED


def test_collect_stream_returns_list(mixed_diffs):
    result = collect_stream(mixed_diffs)
    assert isinstance(result, list)


def test_stream_empty_input():
    result = collect_stream([])
    assert result == []
