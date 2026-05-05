"""Migration planner: orders diffs into a safe execution plan."""

from dataclasses import dataclass, field
from typing import List

from schemadiff.core import ChangeType, TableDiff


# Execution phases — lower phase runs first
_PHASE_ORDER = {
    ChangeType.ADDED: 1,
    ChangeType.MODIFIED: 2,
    ChangeType.DROPPED: 3,
}


@dataclass
class MigrationStep:
    """A single ordered step in the migration plan."""

    phase: int
    table_name: str
    change_type: ChangeType
    diff: TableDiff
    notes: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"MigrationStep(phase={self.phase}, table={self.table_name!r}, "
            f"change={self.change_type.value})"
        )


@dataclass
class MigrationPlan:
    """Ordered list of migration steps with optional warnings."""

    steps: List[MigrationStep] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def phases(self) -> List[int]:
        """Return the distinct phase numbers present in the plan."""
        return sorted({s.phase for s in self.steps})

    def steps_for_phase(self, phase: int) -> List[MigrationStep]:
        return [s for s in self.steps if s.phase == phase]


def _build_notes(diff: TableDiff) -> List[str]:
    notes = []
    if diff.change_type == ChangeType.DROPPED:
        notes.append("Destructive: table will be permanently removed.")
    for col_diff in diff.column_diffs:
        if col_diff.change_type == ChangeType.DROPPED:
            notes.append(f"Destructive: column '{col_diff.column_name}' will be dropped.")
        elif col_diff.change_type == ChangeType.MODIFIED:
            old = col_diff.old_column or {}
            new = col_diff.new_column or {}
            if old.get("type") != new.get("type"):
                notes.append(
                    f"Type change on '{col_diff.column_name}': "
                    f"{old.get('type')} -> {new.get('type')}"
                )
            if new.get("nullable") is False and old.get("nullable") is True:
                notes.append(
                    f"Nullable tightened on '{col_diff.column_name}': may fail if NULLs exist."
                )
    return notes


def build_plan(diffs: List[TableDiff]) -> MigrationPlan:
    """Build an ordered MigrationPlan from a list of TableDiff objects."""
    plan = MigrationPlan()
    for diff in diffs:
        phase = _PHASE_ORDER.get(diff.change_type, 2)
        notes = _build_notes(diff)
        step = MigrationStep(
            phase=phase,
            table_name=diff.table_name,
            change_type=diff.change_type,
            diff=diff,
            notes=notes,
        )
        plan.steps.append(step)
        if notes:
            plan.warnings.extend(notes)
    plan.steps.sort(key=lambda s: (s.phase, s.table_name))
    return plan
