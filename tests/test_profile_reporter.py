"""Tests for schemadiff.profile_reporter."""

import pytest

from schemadiff.profiler import profile_snapshot
from schemadiff.profile_reporter import render_profile_markdown, render_profile_text
from schemadiff.snapshot import SchemaSnapshot


def _make_snapshot(tables: dict) -> SchemaSnapshot:
    return SchemaSnapshot({"tables": tables})


@pytest.fixture()
def profile():
    snap = _make_snapshot({
        "users": {
            "columns": {
                "id": {"type": "int", "nullable": False},
                "name": {"type": "varchar", "nullable": True},
            }
        },
        "logs": {
            "columns": {
                "id": {"type": "int", "nullable": False},
                "message": {"type": "text", "nullable": True},
                "created_at": {"type": "datetime", "nullable": False},
            }
        },
        "staging": {"columns": {}},
    })
    return profile_snapshot(snap)


# ---------------------------------------------------------------------------
# render_profile_text
# ---------------------------------------------------------------------------

def test_render_text_returns_string(profile):
    result = render_profile_text(profile)
    assert isinstance(result, str)


def test_render_text_contains_table_count(profile):
    result = render_profile_text(profile)
    assert "3" in result


def test_render_text_contains_widest_table(profile):
    result = render_profile_text(profile)
    assert "logs" in result


def test_render_text_lists_empty_table(profile):
    result = render_profile_text(profile)
    assert "staging" in result


def test_render_text_type_distribution_present(profile):
    result = render_profile_text(profile)
    assert "int" in result
    assert "varchar" in result
    assert "text" in result


def test_render_text_empty_profile():
    snap = _make_snapshot({})
    p = profile_snapshot(snap)
    result = render_profile_text(p)
    assert "0" in result


# ---------------------------------------------------------------------------
# render_profile_markdown
# ---------------------------------------------------------------------------

def test_render_markdown_returns_string(profile):
    result = render_profile_markdown(profile)
    assert isinstance(result, str)


def test_render_markdown_has_heading(profile):
    result = render_profile_markdown(profile)
    assert "## Schema Profile" in result


def test_render_markdown_has_table_syntax(profile):
    result = render_profile_markdown(profile)
    assert "|" in result


def test_render_markdown_lists_empty_table(profile):
    result = render_profile_markdown(profile)
    assert "`staging`" in result


def test_render_markdown_type_section(profile):
    result = render_profile_markdown(profile)
    assert "### Column Types" in result
    assert "`int`" in result


def test_render_markdown_nullable_percentage(profile):
    result = render_profile_markdown(profile)
    # varchar: 1 nullable out of 1 => 100%
    assert "100.0%" in result
