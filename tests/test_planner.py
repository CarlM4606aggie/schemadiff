"""Tests for schemadiff.planner."""

import pytest
from schemadiff.core import ChangeType, ColumnDiff, TableDiff
from schemadiff.planner import MigrationStep, MigrationPlan, build_plan


def _make_diff(table: str, change: ChangeType, col_diffs=None) -> TableDiff:
    return TableDiff(
        table_name=table,
        change_type=change,
        column_diffs=col_diffs or [],
    )


@pytest.fixture
def mixed_diffs():
    return [
        _make_diff("orders", ChangeType.DROPPED),
        _make_diff("users", ChangeType.ADDED),
        _make_diff("products", ChangeType.MODIFIED),
    ]


def test_build_plan_returns_migration_plan(mixed_diffs):
    plan = build_plan(mixed_diffs)
    assert isinstance(plan, MigrationPlan)


def test_build_plan_step_count_matches_diffs(mixed_diffs):
    plan = build_plan(mixed_diffs)
    assert len(plan.steps) == 3


def test_build_plan_steps_are_ordered_added_before_dropped(mixed_diffs):
    plan = build_plan(mixed_diffs)
    change_types = [s.change_type for s in plan.steps]
    assert change_types.index(ChangeType.ADDED) < change_types.index(ChangeType.DROPPED)


def test_build_plan_modified_before_dropped(mixed_diffs):
    plan = build_plan(mixed_diffs)
    change_types = [s.change_type for s in plan.steps]
    assert change_types.index(ChangeType.MODIFIED) < change_types.index(ChangeType.DROPPED)


def test_empty_diffs_returns_empty_plan():
    plan = build_plan([])
    assert plan.is_empty()
    assert plan.warnings == []


def test_dropped_table_generates_warning():
    diff = _make_diff("legacy", ChangeType.DROPPED)
    plan = build_plan([diff])
    assert any("Destructive" in w for w in plan.warnings)


def test_dropped_column_generates_warning():
    col = ColumnDiff(
        column_name="email",
        change_type=ChangeType.DROPPED,
        old_column={"type": "varchar", "nullable": True},
        new_column=None,
    )
    diff = _make_diff("users", ChangeType.MODIFIED, col_diffs=[col])
    plan = build_plan([diff])
    assert any("email" in w for w in plan.warnings)


def test_type_change_generates_note():
    col = ColumnDiff(
        column_name="age",
        change_type=ChangeType.MODIFIED,
        old_column={"type": "int", "nullable": True},
        new_column={"type": "bigint", "nullable": True},
    )
    diff = _make_diff("users", ChangeType.MODIFIED, col_diffs=[col])
    plan = build_plan([diff])
    step = plan.steps[0]
    assert any("int" in n and "bigint" in n for n in step.notes)


def test_nullable_tightened_generates_note():
    col = ColumnDiff(
        column_name="status",
        change_type=ChangeType.MODIFIED,
        old_column={"type": "varchar", "nullable": True},
        new_column={"type": "varchar", "nullable": False},
    )
    diff = _make_diff("orders", ChangeType.MODIFIED, col_diffs=[col])
    plan = build_plan([diff])
    assert any("Nullable tightened" in n for n in plan.steps[0].notes)


def test_phases_returns_sorted_unique_phases(mixed_diffs):
    plan = build_plan(mixed_diffs)
    phases = plan.phases()
    assert phases == sorted(set(phases))


def test_steps_for_phase_filters_correctly(mixed_diffs):
    plan = build_plan(mixed_diffs)
    added_steps = plan.steps_for_phase(1)
    assert all(s.change_type == ChangeType.ADDED for s in added_steps)


def test_migration_step_repr():
    diff = _make_diff("foo", ChangeType.ADDED)
    step = MigrationStep(phase=1, table_name="foo", change_type=ChangeType.ADDED, diff=diff)
    assert "foo" in repr(step)
    assert "added" in repr(step)
