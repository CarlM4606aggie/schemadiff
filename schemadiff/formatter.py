"""Output formatters for schema diff reports."""

import json
from typing import Literal
from schemadiff.core import SchemaDiff, ChangeType
from schemadiff.reporter import generate_report


OutputFormat = Literal["text", "json", "markdown"]

VALID_FORMATS: tuple[str, ...] = ("text", "json", "markdown")


def _diff_to_dict(diff: SchemaDiff) -> dict:
    """Serialize a SchemaDiff to a plain dictionary."""
    tables = []
    for table in diff.table_diffs:
        columns = []
        for col in table.column_diffs:
            columns.append({
                "column": col.column_name,
                "change": col.change_type.value,
                "old_type": col.old_type,
                "new_type": col.new_type,
                "old_nullable": col.old_nullable,
                "new_nullable": col.new_nullable,
            })
        tables.append({
            "table": table.table_name,
            "change": table.change_type.value,
            "columns": columns,
        })
    return {"tables": tables}


def _format_markdown(diff: SchemaDiff, title: str = "Schema Migration Diff") -> str:
    """Format diff as a Markdown document."""
    lines = [f"# {title}", ""]
    if not diff.table_diffs:
        lines.append("_No differences found._")
        return "\n".join(lines)

    for table in diff.table_diffs:
        lines.append(f"## `{table.table_name}` — {table.change_type.value.upper()}")
        if table.column_diffs:
            lines.append("")
            lines.append("| Column | Change | Old Type | New Type | Nullable Change |")
            lines.append("|--------|--------|----------|----------|-----------------|")
            for col in table.column_diffs:
                nullable_change = (
                    f"{col.old_nullable} → {col.new_nullable}"
                    if col.old_nullable != col.new_nullable
                    else "-"
                )
                lines.append(
                    f"| `{col.column_name}` | {col.change_type.value} "
                    f"| {col.old_type or '-'} | {col.new_type or '-'} | {nullable_change} |"
                )
        lines.append("")
    return "\n".join(lines)


def format_diff(
    diff: SchemaDiff,
    output_format: OutputFormat = "text",
    title: str = "Schema Migration Diff",
) -> str:
    """Format a SchemaDiff into the requested output format.

    Args:
        diff: The SchemaDiff object to format.
        output_format: One of 'text', 'json', or 'markdown'. Defaults to 'text'.
        title: A title string used in text and markdown output.

    Returns:
        A formatted string representation of the diff.

    Raises:
        ValueError: If an unsupported output format is provided.
    """
    if output_format == "text":
        return generate_report(diff, title=title)
    elif output_format == "json":
        return json.dumps(_diff_to_dict(diff), indent=2)
    elif output_format == "markdown":
        return _format_markdown(diff, title=title)
    else:
        raise ValueError(
            f"Unsupported output format: {output_format!r}. "
            f"Valid formats are: {', '.join(VALID_FORMATS)}"
        )
