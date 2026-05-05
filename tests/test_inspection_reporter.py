"""Tests for schemadiff.inspection_reporter."""

import pytest
from unittest.mock import MagicMock

from schemadiff.inspector import inspect_snapshot
from schemadiff.inspection_reporter import render_inspection_text, render_inspection_markdown


def _make_snapshot(tables: dict):
    snap = MagicMock()
    snap.table_names.return_value = list(tables.keys())
    snap.get_table.side_effect = lambda name: tables.get(name)
    return snap


_TABLES = {
    "users": {
        "columns": {
            "id": {"type": "integer", "nullable": False},
            "email": {"type": "varchar", "nullable": False},
            "bio": {"type": "text", "nullable": True},
        }
    },
    "orders": {
        "columns": {
            "id": {"type": "integer", "nullable": False},
            "amount": {"type": "numeric", "nullable": True},
        }
    },
}


@pytest.fixture
def report():
    snap = _make_snapshot(_TABLES)
    return inspect_snapshot(snap)


def test_render_text_returns_string(report):
    result = render_inspection_text(report)
    assert isinstance(result, str)


def test_render_text_contains_table_count(report):
    result = render_inspection_text(report)
    assert "2" in result


def test_render_text_contains_widest_table(report):
    result = render_inspection_text(report)
    assert "users" in result


def test_render_text_contains_type_info(report):
    result = render_inspection_text(report)
    assert "integer" in result
    assert "varchar" in result


def test_render_text_contains_per_table_section(report):
    result = render_inspection_text(report)
    assert "Per-table breakdown" in result
    assert "orders" in result


def test_render_markdown_returns_string(report):
    result = render_inspection_markdown(report)
    assert isinstance(result, str)


def test_render_markdown_has_heading(report):
    result = render_inspection_markdown(report)
    assert result.startswith("# Schema Inspection Report")


def test_render_markdown_contains_table_row(report):
    result = render_inspection_markdown(report)
    assert "`users`" in result
    assert "`orders`" in result


def test_render_markdown_contains_type_backticks(report):
    result = render_inspection_markdown(report)
    assert "`integer`" in result


def test_render_text_empty_snapshot():
    snap = _make_snapshot({})
    report = inspect_snapshot(snap)
    result = render_inspection_text(report)
    assert "0" in result


def test_render_markdown_empty_snapshot():
    snap = _make_snapshot({})
    report = inspect_snapshot(snap)
    result = render_inspection_markdown(report)
    assert "0" in result
