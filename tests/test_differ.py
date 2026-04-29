"""Tests for schemadiff.differ module."""

import pytest
from unittest.mock import patch, MagicMock
from schemadiff.differ import diff_and_patch, diff_summary_and_patch
from schemadiff.core import ChangeType, TableDiff, ColumnDiff


@pytest.fixture
def mock_snapshot_a():
    return MagicMock(name="snapshot_a")


@pytest.fixture
def mock_snapshot_b():
    return MagicMock(name="snapshot_b")


@pytest.fixture
def sample_diffs():
    return [
        TableDiff(
            table_name="users",
            change_type=ChangeType.MODIFIED,
            column_diffs=[
                ColumnDiff(
                    column_name="email",
                    change_type=ChangeType.ADDED,
                    old_value=None,
                    new_value={"type": "TEXT", "nullable": True},
                )
            ],
        ),
        TableDiff(
            table_name="sessions",
            change_type=ChangeType.DROPPED,
            column_diffs=[],
        ),
    ]


def test_diff_and_patch_returns_string(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert isinstance(result, str)
    assert len(result) > 0


def test_diff_and_patch_contains_sql(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert "DROP TABLE" in result or "ADD COLUMN" in result


def test_diff_and_patch_with_table_filter(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_and_patch(mock_snapshot_a, mock_snapshot_b, tables=["users"])
    assert isinstance(result, str)
    assert "sessions" not in result


def test_diff_and_patch_with_change_type_filter(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_and_patch(
            mock_snapshot_a,
            mock_snapshot_b,
            change_types=[ChangeType.DROPPED],
        )
    assert "DROP TABLE" in result


def test_diff_and_patch_no_filter_applies_all(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert "users" in result or "sessions" in result


def test_diff_summary_and_patch_returns_dict(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_summary_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert isinstance(result, dict)
    assert "total_changes" in result
    assert "patch" in result


def test_diff_summary_total_changes(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_summary_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert result["total_changes"] == 2


def test_diff_summary_patch_is_string(mock_snapshot_a, mock_snapshot_b, sample_diffs):
    with patch("schemadiff.differ.compare_snapshots", return_value=sample_diffs):
        result = diff_summary_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert isinstance(result["patch"], str)


def test_diff_and_patch_empty_diffs(mock_snapshot_a, mock_snapshot_b):
    with patch("schemadiff.differ.compare_snapshots", return_value=[]):
        result = diff_and_patch(mock_snapshot_a, mock_snapshot_b)
    assert isinstance(result, str)
    assert "Auto-generated" in result
