"""Tests for schemadiff.annotator."""

import pytest
from schemadiff.core import ChangeType, TableDiff, ColumnDiff
from schemadiff.tagger import tag_diffs
from schemadiff.annotator import AnnotatedDiff, annotate, format_annotated


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def added_diff():
    return TableDiff(table_name="accounts", change_type=ChangeType.ADDED)


@pytest.fixture
def dropped_diff():
    return TableDiff(table_name="sessions", change_type=ChangeType.DROPPED)


@pytest.fixture
def modified_with_type_change():
    col = ColumnDiff(
        column_name="score",
        change_type=ChangeType.MODIFIED,
        old_type="int",
        new_type="float",
    )
    return TableDiff(
        table_name="metrics",
        change_type=ChangeType.MODIFIED,
        column_diffs=[col],
    )


@pytest.fixture
def tagged_sample(added_diff, dropped_diff, modified_with_type_change):
    return tag_diffs([added_diff, dropped_diff, modified_with_type_change])


# ---------------------------------------------------------------------------
# annotate
# ---------------------------------------------------------------------------

def test_annotate_returns_annotated_diff_instances(tagged_sample):
    result = annotate(tagged_sample)
    assert all(isinstance(a, AnnotatedDiff) for a in result)
    assert len(result) == 3


def test_annotate_additive_note_present(tagged_sample):
    result = annotate(tagged_sample)
    accounts = next(a for a in result if a.diff.table_name == "accounts")
    assert any("Additive" in n or "safe" in n for n in accounts.notes)


def test_annotate_breaking_note_present(tagged_sample):
    result = annotate(tagged_sample)
    sessions = next(a for a in result if a.diff.table_name == "sessions")
    assert any("Breaking" in n or "review" in n for n in sessions.notes)


def test_annotate_custom_note_overrides_default(tagged_sample):
    custom = {"additive": "Custom additive message."}
    result = annotate(tagged_sample, custom_notes=custom)
    accounts = next(a for a in result if a.diff.table_name == "accounts")
    assert "Custom additive message." in accounts.notes


def test_annotate_no_notes_for_untagged():
    plain = TableDiff(table_name="plain", change_type=ChangeType.MODIFIED)
    tagged = tag_diffs([plain])
    result = annotate(tagged)
    assert result[0].notes == []


# ---------------------------------------------------------------------------
# format_annotated
# ---------------------------------------------------------------------------

def test_format_annotated_returns_string(tagged_sample):
    annotated = annotate(tagged_sample)
    output = format_annotated(annotated)
    assert isinstance(output, str)


def test_format_annotated_contains_table_names(tagged_sample):
    annotated = annotate(tagged_sample)
    output = format_annotated(annotated)
    assert "accounts" in output
    assert "sessions" in output
    assert "metrics" in output


def test_format_annotated_contains_change_type(tagged_sample):
    annotated = annotate(tagged_sample)
    output = format_annotated(annotated)
    assert "ADDED" in output
    assert "DROPPED" in output


def test_annotated_diff_repr(tagged_sample):
    annotated = annotate(tagged_sample)
    r = repr(annotated[0])
    assert "AnnotatedDiff" in r
    assert "accounts" in r
