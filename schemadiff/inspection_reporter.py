"""Render InspectionReport to human-readable text or markdown."""

from schemadiff.inspector import InspectionReport


def _section(title: str, char: str = "-") -> str:
    return f"\n{title}\n{char * len(title)}"


def render_inspection_text(report: InspectionReport) -> str:
    """Render an InspectionReport as plain text."""
    lines = []
    lines.append("Schema Inspection Report")
    lines.append("=" * 24)
    lines.append(f"Tables : {report.table_count}")
    lines.append(f"Columns: {report.total_columns}")

    widest = report.widest_table()
    if widest:
        lines.append(f"Widest table: {widest} ({report.inspections[widest].column_count} columns)")

    all_types = report.all_column_types()
    if all_types:
        lines.append(f"Column types used: {', '.join(all_types)}")

    strict = report.tables_with_no_nullable_columns()
    if strict:
        lines.append(f"Fully non-nullable tables: {', '.join(sorted(strict))}")

    lines.append(_section("Per-table breakdown"))
    for name, insp in sorted(report.inspections.items()):
        lines.append(f"  {name}")
        lines.append(f"    columns      : {insp.column_count}")
        lines.append(f"    nullable     : {len(insp.nullable_columns)} ({insp.nullable_ratio:.0%})")
        lines.append(f"    types        : {', '.join(insp.unique_types) or 'n/a'}")

    return "\n".join(lines)


def render_inspection_markdown(report: InspectionReport) -> str:
    """Render an InspectionReport as Markdown."""
    lines = []
    lines.append("# Schema Inspection Report")
    lines.append(f"- **Tables**: {report.table_count}")
    lines.append(f"- **Total columns**: {report.total_columns}")

    widest = report.widest_table()
    if widest:
        lines.append(f"- **Widest table**: `{widest}` ({report.inspections[widest].column_count} columns)")

    all_types = report.all_column_types()
    if all_types:
        lines.append(f"- **Types used**: {', '.join(f'`{t}`' for t in all_types)}")

    strict = report.tables_with_no_nullable_columns()
    if strict:
        lines.append(f"- **Fully non-nullable**: {', '.join(f'`{t}`' for t in sorted(strict))}")

    lines.append("\n## Per-table breakdown\n")
    lines.append("| Table | Columns | Nullable | Types |")
    lines.append("|-------|---------|----------|-------|")
    for name, insp in sorted(report.inspections.items()):
        nullable_str = f"{len(insp.nullable_columns)} ({insp.nullable_ratio:.0%})"
        types_str = ", ".join(f"`{t}`" for t in insp.unique_types) or "n/a"
        lines.append(f"| `{name}` | {insp.column_count} | {nullable_str} | {types_str} |")

    return "\n".join(lines)
