"""Profile schema snapshots to produce statistical summaries."""

from dataclasses import dataclass, field
from typing import Dict, List

from schemadiff.snapshot import SchemaSnapshot


@dataclass
class ColumnTypeStats:
    type_name: str
    count: int
    nullable_count: int

    def nullable_ratio(self) -> float:
        if self.count == 0:
            return 0.0
        return round(self.nullable_count / self.count, 4)


@dataclass
class SchemaProfile:
    table_count: int
    total_columns: int
    avg_columns_per_table: float
    type_distribution: Dict[str, ColumnTypeStats] = field(default_factory=dict)
    tables_with_no_columns: List[str] = field(default_factory=list)
    most_column_rich_table: str = ""
    most_column_rich_count: int = 0

    def summary(self) -> str:
        lines = [
            f"Tables          : {self.table_count}",
            f"Total columns   : {self.total_columns}",
            f"Avg cols/table  : {self.avg_columns_per_table}",
        ]
        if self.most_column_rich_table:
            lines.append(
                f"Widest table    : {self.most_column_rich_table} "
                f"({self.most_column_rich_count} cols)"
            )
        if self.tables_with_no_columns:
            lines.append(f"Empty tables    : {', '.join(self.tables_with_no_columns)}")
        if self.type_distribution:
            lines.append("Column types:")
            for type_name, stats in sorted(self.type_distribution.items()):
                lines.append(
                    f"  {type_name:<20} count={stats.count}  "
                    f"nullable_ratio={stats.nullable_ratio():.2%}"
                )
        return "\n".join(lines)


def profile_snapshot(snapshot: SchemaSnapshot) -> SchemaProfile:
    """Analyse a SchemaSnapshot and return a SchemaProfile."""
    table_names = snapshot.table_names()
    table_count = len(table_names)
    total_columns = 0
    type_dist: Dict[str, ColumnTypeStats] = {}
    tables_with_no_columns: List[str] = []
    most_rich_table = ""
    most_rich_count = 0

    for name in table_names:
        table = snapshot.get_table(name)
        if table is None:
            continue
        columns = table.get("columns", {})
        col_count = len(columns)
        total_columns += col_count

        if col_count == 0:
            tables_with_no_columns.append(name)

        if col_count > most_rich_count:
            most_rich_count = col_count
            most_rich_table = name

        for col_name, col_def in columns.items():
            col_type = col_def.get("type", "unknown").lower()
            nullable = bool(col_def.get("nullable", False))
            if col_type not in type_dist:
                type_dist[col_type] = ColumnTypeStats(
                    type_name=col_type, count=0, nullable_count=0
                )
            type_dist[col_type].count += 1
            if nullable:
                type_dist[col_type].nullable_count += 1

    avg = round(total_columns / table_count, 2) if table_count else 0.0

    return SchemaProfile(
        table_count=table_count,
        total_columns=total_columns,
        avg_columns_per_table=avg,
        type_distribution=type_dist,
        tables_with_no_columns=tables_with_no_columns,
        most_column_rich_table=most_rich_table,
        most_column_rich_count=most_rich_count,
    )
