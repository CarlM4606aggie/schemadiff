"""Tests for reporter and formatter modules."""

import json
import pytest
from schemadiff.snapshot import SchemaSnapshot
from schemadiff.core import diff_snapshots, ChangeType
from schemadiff.reporter import generate_report, format_column_diff, format_table_diff
from schemadiff.formatter import format_diff


V1_PATH = "tests/fixtures/snapshot_v1.json"
V2_PATH = "tests/fixtures/snapshot_v2.json"


@pytest.fixture
def schema_diff():
    v1 = SchemaSnapshot.load(V1_PATH)
    v2 = SchemaSnapshot.load(V2_PATH)
    return diff_snapshots(v1, v2)


def test_generate_report_returns_string(schema_diff):
    report = generate_report(schema_diff)
    assert isinstance(report, str)
    assert len(report) > 0


def test_report_contains_summary(schema_diff):
    report = generate_report(schema_diff, show_summary=True)
    assert "Summary:" in report


def test_report_no_summary(schema_diff):
    report = generate_report(schema_diff, show_summary=False)
    assert "Summary:" not in report


def test_report_custom_title(schema_diff):
    report = generate_report(schema_diff, title="My Custom Title")
    assert "My Custom Title" in report


def test_report_empty_diff():
    v1 = SchemaSnapshot.load(V1_PATH)
    diff = diff_snapshots(v1, v1)
    report = generate_report(diff)
    assert "No differences found" in report


def test_format_diff_text(schema_diff):
    output = format_diff(schema_diff, output_format="text")
    assert "Schema Migration Diff" in output


def test_format_diff_json(schema_diff):
    output = format_diff(schema_diff, output_format="json")
    data = json.loads(output)
    assert "tables" in data
    assert isinstance(data["tables"], list)


def test_format_diff_json_structure(schema_diff):
    output = format_diff(schema_diff, output_format="json")
    data = json.loads(output)
    for entry in data["tables"]:
        assert "table" in entry
        assert "change" in entry
        assert "columns" in entry


def test_format_diff_markdown(schema_diff):
    output = format_diff(schema_diff, output_format="markdown")
    assert output.startswith("#")
    assert "Schema Migration Diff" in output


def test_format_diff_unsupported_format(schema_diff):
    with pytest.raises(ValueError, match="Unsupported output format"):
        format_diff(schema_diff, output_format="xml")


def test_markdown_contains_table_headers(schema_diff):
    output = format_diff(schema_diff, output_format="markdown")
    assert "| Column |" in output
