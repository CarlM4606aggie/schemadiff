"""Tests for schemadiff.exporter module."""

import json
import pytest
from unittest.mock import patch, MagicMock

from schemadiff.core import ChangeType, TableDiff, ColumnDiff
from schemadiff.exporter import export_diff, SUPPORTED_FORMATS


@pytest.fixture
def sample_diffs():
    col_diff = ColumnDiff(
        column_name="email",
        change_type=ChangeType.MODIFIED,
        old_definition={"type": "varchar(100)", "nullable": True},
        new_definition={"type": "varchar(255)", "nullable": False},
    )
    added_table = TableDiff(
        table_name="orders",
        change_type=ChangeType.ADDED,
        column_diffs=[],
    )
    modified_table = TableDiff(
        table_name="users",
        change_type=ChangeType.MODIFIED,
        column_diffs=[col_diff],
    )
    return [added_table, modified_table]


def test_export_diff_text_returns_string(sample_diffs):
    result = export_diff(sample_diffs, output_format="text")
    assert isinstance(result, str)
    assert len(result) > 0


def test_export_diff_markdown_returns_string(sample_diffs):
    result = export_diff(sample_diffs, output_format="markdown")
    assert isinstance(result, str)


def test_export_diff_json_is_valid(sample_diffs):
    result = export_diff(sample_diffs, output_format="json")
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert len(parsed) == 2


def test_export_diff_json_structure(sample_diffs):
    result = export_diff(sample_diffs, output_format="json")
    parsed = json.loads(result)
    tables = {entry["table"]: entry for entry in parsed}
    assert "orders" in tables
    assert "users" in tables
    assert tables["users"]["column_diffs"][0]["column"] == "email"


def test_export_diff_unsupported_format_raises(sample_diffs):
    with pytest.raises(ValueError, match="Unsupported format"):
        export_diff(sample_diffs, output_format="xml")


def test_supported_formats_constant():
    assert "json" in SUPPORTED_FORMATS
    assert "markdown" in SUPPORTED_FORMATS
    assert "text" in SUPPORTED_FORMATS


def test_export_diff_writes_to_file(sample_diffs, tmp_path):
    output_file = tmp_path / "output" / "diff.txt"
    export_diff(sample_diffs, output_format="text", output_path=str(output_file))
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert len(content) > 0


def test_export_diff_json_writes_to_file(sample_diffs, tmp_path):
    output_file = tmp_path / "diff.json"
    export_diff(sample_diffs, output_format="json", output_path=str(output_file))
    assert output_file.exists()
    parsed = json.loads(output_file.read_text())
    assert isinstance(parsed, list)


def test_export_diff_empty_diffs():
    result = export_diff([], output_format="json")
    parsed = json.loads(result)
    assert parsed == []
