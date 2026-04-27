"""Export schema diffs to various output formats (JSON, Markdown, plain text)."""

import json
from pathlib import Path
from typing import Optional

from schemadiff.core import TableDiff
from schemadiff.formatter import format_diff
from schemadiff.reporter import generate_report


SUPPORTED_FORMATS = ("json", "markdown", "text")


def export_diff(
    diffs: list[TableDiff],
    output_format: str = "text",
    output_path: Optional[str] = None,
    title: str = "Schema Migration Diff",
    include_summary: bool = True,
) -> str:
    """Export a list of TableDiff objects to the specified format.

    Args:
        diffs: List of TableDiff objects to export.
        output_format: One of 'json', 'markdown', or 'text'.
        output_path: Optional file path to write output to.
        title: Title used in report-style formats.
        include_summary: Whether to include a summary section.

    Returns:
        The formatted diff as a string.

    Raises:
        ValueError: If output_format is not supported.
    """
    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{output_format}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    if output_format == "json":
        result = _export_json(diffs)
    elif output_format == "markdown":
        result = format_diff(diffs, fmt="markdown")
    else:
        result = generate_report(diffs, title=title, include_summary=include_summary)

    if output_path:
        _write_to_file(result, output_path)

    return result


def _export_json(diffs: list[TableDiff]) -> str:
    """Serialize diffs to a JSON string."""
    payload = []
    for td in diffs:
        entry = {
            "table": td.table_name,
            "change_type": td.change_type.value,
            "column_diffs": [
                {
                    "column": cd.column_name,
                    "change_type": cd.change_type.value,
                    "old": cd.old_definition,
                    "new": cd.new_definition,
                }
                for cd in (td.column_diffs or [])
            ],
        }
        payload.append(entry)
    return json.dumps(payload, indent=2)


def _write_to_file(content: str, path: str) -> None:
    """Write content to a file, creating parent directories as needed."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
