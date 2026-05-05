"""Inspector: analyze a SchemaSnapshot and produce structural insights."""

from dataclasses import dataclass, field
from typing import Dict, List

from schemadiff.snapshot import SchemaSnapshot


@dataclass
class TableInspection:
    table_name: str
    column_count: int
    nullable_columns: List[str]
    non_nullable_columns: List[str]
    unique_types: List[str]

    @property
    def nullable_ratio(self) -> float:
        if self.column_count == 0:
            return 0.0
        return len(self.nullable_columns) / self.column_count


@dataclass
class InspectionReport:
    table_count: int
    total_columns: int
    inspections: Dict[str, TableInspection] = field(default_factory=dict)

    def widest_table(self) -> str | None:
        if not self.inspections:
            return None
        return max(self.inspections, key=lambda t: self.inspections[t].column_count)

    def tables_with_no_nullable_columns(self) -> List[str]:
        return [
            name
            for name, insp in self.inspections.items()
            if len(insp.nullable_columns) == 0
        ]

    def all_column_types(self) -> List[str]:
        seen = set()
        types = []
        for insp in self.inspections.values():
            for t in insp.unique_types:
                if t not in seen:
                    seen.add(t)
                    types.append(t)
        return sorted(types)


def _inspect_table(table_name: str, table: dict) -> TableInspection:
    columns = table.get("columns", {})
    nullable = []
    non_nullable = []
    types_seen = set()

    for col_name, col_def in columns.items():
        if col_def.get("nullable", True):
            nullable.append(col_name)
        else:
            non_nullable.append(col_name)
        col_type = col_def.get("type", "unknown")
        types_seen.add(col_type)

    return TableInspection(
        table_name=table_name,
        column_count=len(columns),
        nullable_columns=sorted(nullable),
        non_nullable_columns=sorted(non_nullable),
        unique_types=sorted(types_seen),
    )


def inspect_snapshot(snapshot: SchemaSnapshot) -> InspectionReport:
    """Produce a full InspectionReport from a SchemaSnapshot."""
    inspections: Dict[str, TableInspection] = {}
    total_columns = 0

    for table_name in snapshot.table_names():
        table = snapshot.get_table(table_name)
        if table is None:
            continue
        insp = _inspect_table(table_name, table)
        inspections[table_name] = insp
        total_columns += insp.column_count

    return InspectionReport(
        table_count=len(inspections),
        total_columns=total_columns,
        inspections=inspections,
    )
