"""Render a SchemaProfile as human-readable text or Markdown."""

from schemadiff.profiler import SchemaProfile


def _section(title: str, lines: list) -> str:
    return f"### {title}\n" + "\n".join(lines)


def render_profile_text(profile: SchemaProfile) -> str:
    """Return a plain-text report for the given SchemaProfile."""
    lines = [
        "Schema Profile",
        "=" * 40,
        f"Tables              : {profile.table_count}",
        f"Total columns       : {profile.total_columns}",
        f"Avg columns/table   : {profile.avg_columns_per_table}",
    ]

    if profile.most_column_rich_table:
        lines.append(
            f"Widest table        : {profile.most_column_rich_table} "
            f"({profile.most_column_rich_count} columns)"
        )

    if profile.tables_with_no_columns:
        lines.append("")
        lines.append("Tables with no columns:")
        for t in sorted(profile.tables_with_no_columns):
            lines.append(f"  - {t}")

    if profile.type_distribution:
        lines.append("")
        lines.append("Column type distribution:")
        for type_name, stats in sorted(profile.type_distribution.items()):
            lines.append(
                f"  {type_name:<20} count={stats.count:<6} "
                f"nullable={stats.nullable_count} "
                f"({stats.nullable_ratio():.1%})"
            )

    return "\n".join(lines)


def render_profile_markdown(profile: SchemaProfile) -> str:
    """Return a Markdown report for the given SchemaProfile."""
    lines = [
        "## Schema Profile",
        "",
        "| Metric | Value |",
        "|--------|-------|" ,
        f"| Tables | {profile.table_count} |",
        f"| Total columns | {profile.total_columns} |",
        f"| Avg columns/table | {profile.avg_columns_per_table} |",
    ]

    if profile.most_column_rich_table:
        lines.append(
            f"| Widest table | {profile.most_column_rich_table} "
            f"({profile.most_column_rich_count} cols) |"
        )

    if profile.tables_with_no_columns:
        lines.append("")
        lines.append("### Empty Tables")
        for t in sorted(profile.tables_with_no_columns):
            lines.append(f"- `{t}`")

    if profile.type_distribution:
        lines.append("")
        lines.append("### Column Types")
        lines.append("")
        lines.append("| Type | Count | Nullable | Nullable % |")
        lines.append("|------|-------|----------|------------|")
        for type_name, stats in sorted(profile.type_distribution.items()):
            lines.append(
                f"| `{type_name}` | {stats.count} | "
                f"{stats.nullable_count} | {stats.nullable_ratio():.1%} |"
            )

    return "\n".join(lines)
