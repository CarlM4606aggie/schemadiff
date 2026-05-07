"""Tests for schemadiff.comparator_pipeline."""

import pytest
from unittest.mock import MagicMock
from schemadiff.snapshot import SchemaSnapshot
from schemadiff.core import ChangeType, TableDiff
from schemadiff.comparator_pipeline import (
    ComparatorPipelineConfig,
    ComparatorPipelineResult,
    run_comparator_pipeline,
)


def _make_snapshot(tables: dict) -> SchemaSnapshot:
    snap = MagicMock(spec=SchemaSnapshot)
    snap.table_names.return_value = list(tables.keys())
    snap.get_table.side_effect = lambda name: tables.get(name)
    return snap


@pytest.fixture
def snapshot_a():
    return _make_snapshot({"users": {"id": {"type": "int", "nullable": False}}})


@pytest.fixture
def snapshot_b():
    return _make_snapshot({
        "users": {"id": {"type": "int", "nullable": False}},
        "orders": {"order_id": {"type": "int", "nullable": False}},
    })


def test_run_pipeline_returns_result(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    assert isinstance(result, ComparatorPipelineResult)


def test_run_pipeline_diffs_is_list(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    assert isinstance(result.diffs, list)


def test_run_pipeline_detects_added_table(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    table_names = [d.table_name for d in result.diffs]
    assert "orders" in table_names


def test_run_pipeline_has_changes_true(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    assert result.has_changes is True


def test_run_pipeline_no_changes(snapshot_a):
    result = run_comparator_pipeline(snapshot_a, snapshot_a)
    assert result.has_changes is False


def test_run_pipeline_report_is_string(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    assert isinstance(result.report, str)


def test_run_pipeline_default_format_is_text(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    assert "Schema Comparison" in result.report
    assert "#" not in result.report.splitlines()[0]


def test_run_pipeline_markdown_format(snapshot_a, snapshot_b):
    config = ComparatorPipelineConfig(output_format="markdown")
    result = run_comparator_pipeline(snapshot_a, snapshot_b, config=config)
    assert result.report.startswith("# ")


def test_run_pipeline_custom_title(snapshot_a, snapshot_b):
    config = ComparatorPipelineConfig(title="Prod vs Dev")
    result = run_comparator_pipeline(snapshot_a, snapshot_b, config=config)
    assert "Prod vs Dev" in result.report


def test_run_pipeline_table_filter(snapshot_a, snapshot_b):
    config = ComparatorPipelineConfig(table_filter=["users"])
    result = run_comparator_pipeline(snapshot_a, snapshot_b, config=config)
    table_names = [d.table_name for d in result.diffs]
    assert "orders" not in table_names


def test_run_pipeline_summary_total_matches_diffs(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b)
    assert result.summary.total_changes == len(result.diffs)


def test_run_pipeline_default_config_used_when_none(snapshot_a, snapshot_b):
    result = run_comparator_pipeline(snapshot_a, snapshot_b, config=None)
    assert result.config.output_format == "text"
