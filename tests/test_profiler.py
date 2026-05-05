"""Tests for schemadiff.profiler."""

import pytest

from schemadiff.profiler import ColumnTypeStats, SchemaProfile, profile_snapshot
from schemadiff.snapshot import SchemaSnapshot


def _make_snapshot(tables: dict) -> SchemaSnapshot:
    return SchemaSnapshot({"tables": tables})


# ---------------------------------------------------------------------------
# ColumnTypeStats
# ---------------------------------------------------------------------------

def test_nullable_ratio_zero_count():
    stats = ColumnTypeStats(type_name="int", count=0, nullable_count=0)
    assert stats.nullable_ratio() == 0.0


def test_nullable_ratio_calculation():
    stats = ColumnTypeStats(type_name="varchar", count=4, nullable_count=1)
    assert stats.nullable_ratio() == 0.25


# ---------------------------------------------------------------------------
# profile_snapshot
# ---------------------------------------------------------------------------

@pytest.fixture()
def rich_snapshot():
    return _make_snapshot({
        "users": {
            "columns": {
                "id": {"type": "int", "nullable": False},
                "email": {"type": "varchar", "nullable": False},
                "bio": {"type": "text", "nullable": True},
            }
        },
        "orders": {
            "columns": {
                "id": {"type": "int", "nullable": False},
                "total": {"type": "decimal", "nullable": True},
            }
        },
        "empty_table": {"columns": {}},
    })


def test_profile_table_count(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert profile.table_count == 3


def test_profile_total_columns(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert profile.total_columns == 5


def test_profile_avg_columns_per_table(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert profile.avg_columns_per_table == round(5 / 3, 2)


def test_profile_most_column_rich_table(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert profile.most_column_rich_table == "users"
    assert profile.most_column_rich_count == 3


def test_profile_tables_with_no_columns(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert "empty_table" in profile.tables_with_no_columns


def test_profile_type_distribution_keys(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert "int" in profile.type_distribution
    assert "varchar" in profile.type_distribution
    assert "text" in profile.type_distribution
    assert "decimal" in profile.type_distribution


def test_profile_nullable_count_in_type_dist(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    assert profile.type_distribution["text"].nullable_count == 1
    assert profile.type_distribution["int"].nullable_count == 0


def test_profile_empty_snapshot():
    snapshot = _make_snapshot({})
    profile = profile_snapshot(snapshot)
    assert profile.table_count == 0
    assert profile.total_columns == 0
    assert profile.avg_columns_per_table == 0.0
    assert profile.most_column_rich_table == ""


def test_profile_summary_returns_string(rich_snapshot):
    profile = profile_snapshot(rich_snapshot)
    summary = profile.summary()
    assert isinstance(summary, str)
    assert "Tables" in summary
    assert "users" in summary
