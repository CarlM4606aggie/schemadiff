"""Tests for schemadiff.tagger."""

import pytest
from schemadiff.core import ChangeType, TableDiff, ColumnDiff
from schemadiff.tagger import (
    TaggedDiff,
    auto_tag,
    tag_diffs,
    filter_by_tag,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def added_table():
    return TableDiff(table_name="users", change_type=ChangeType.ADDED)


@pytest.fixture
def dropped_table():
    return TableDiff(table_name="legacy", change_type=ChangeType.DROPPED)


@pytest.fixture
def modified_with_dropped_col():
    col = ColumnDiff(
        column_name="email",
        change_type=ChangeType.DROPPED,
        old_type="varchar",
        new_type=None,
    )
    return TableDiff(
        table_name="orders",
        change_type=ChangeType.MODIFIED,
        column_diffs=[col],
    )


@pytest.fixture
def modified_with_type_change():
    col = ColumnDiff(
        column_name="amount",
        change_type=ChangeType.MODIFIED,
        old_type="int",
        new_type="bigint",
    )
    return TableDiff(
        table_name="payments",
        change_type=ChangeType.MODIFIED,
        column_diffs=[col],
    )


# ---------------------------------------------------------------------------
# auto_tag
# ---------------------------------------------------------------------------

def test_auto_tag_added_table_is_additive(added_table):
    tags = auto_tag(added_table)
    assert "additive" in tags


def test_auto_tag_dropped_table_is_breaking(dropped_table):
    tags = auto_tag(dropped_table)
    assert "breaking" in tags


def test_auto_tag_dropped_column_is_destructive(modified_with_dropped_col):
    tags = auto_tag(modified_with_dropped_col)
    assert "destructive" in tags


def test_auto_tag_type_change_is_breaking(modified_with_type_change):
    tags = auto_tag(modified_with_type_change)
    assert "breaking" in tags


# ---------------------------------------------------------------------------
# tag_diffs
# ---------------------------------------------------------------------------

def test_tag_diffs_returns_tagged_diff_instances(added_table, dropped_table):
    result = tag_diffs([added_table, dropped_table])
    assert all(isinstance(td, TaggedDiff) for td in result)
    assert len(result) == 2


def test_tag_diffs_applies_extra_tags(added_table):
    result = tag_diffs([added_table], extra_tags={"users": ["core", "pii"]})
    assert result[0].has_tag("core")
    assert result[0].has_tag("pii")


def test_tag_diffs_extra_tags_case_insensitive(added_table):
    result = tag_diffs([added_table], extra_tags={"users": ["PII"]})
    assert result[0].has_tag("pii")


def test_tag_diffs_no_extra_tags_for_other_tables(added_table, dropped_table):
    result = tag_diffs(
        [added_table, dropped_table], extra_tags={"users": ["core"]}
    )
    legacy_td = next(td for td in result if td.diff.table_name == "legacy")
    assert not legacy_td.has_tag("core")


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

def test_filter_by_tag_returns_matching(added_table, dropped_table):
    tagged = tag_diffs([added_table, dropped_table])
    breaking = filter_by_tag(tagged, "breaking")
    assert all(td.has_tag("breaking") for td in breaking)


def test_filter_by_tag_empty_when_no_match(added_table):
    tagged = tag_diffs([added_table])
    result = filter_by_tag(tagged, "nonexistent")
    assert result == []


def test_tagged_diff_repr(added_table):
    td = TaggedDiff(diff=added_table, tags=["additive"])
    assert "users" in repr(td)
    assert "additive" in repr(td)
