"""Renders schema diffs into various human-readable formats with optional coloring."""

from dataclasses import dataclass
from typing import List, Optional
from schemadiff.core import TableDiff, ChangeType

ANSI_RESET = "\033[0m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"
ANSI_BOLD = "\033[1m"

CHANGE_SYMBOLS = {
    ChangeType.ADDED: "+",
    ChangeType.DROPPED: "-",
    ChangeType.MODIFIED: "~",
}

CHANGE_COLORS = {
    ChangeType.ADDED: ANSI_GREEN,
    ChangeType.DROPPED: ANSI_RED,
    ChangeType.MODIFIED: ANSI_YELLOW,
}


@dataclass
class RenderOptions:
    use_color: bool = False
    show_column_details: bool = True
    indent: str = "  "


def _colorize(text: str, color: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{color}{text}{ANSI_RESET}"


def render_table_diff(diff: TableDiff, options: Optional[RenderOptions] = None) -> str:
    opts = options or RenderOptions()
    symbol = CHANGE_SYMBOLS.get(diff.change_type, "?")
    color = CHANGE_COLORS.get(diff.change_type, "")
    header = _colorize(
        f"{symbol} TABLE {diff.table_name} [{diff.change_type.value}]",
        color,
        opts.use_color,
    )
    lines = [header]

    if opts.show_column_details and diff.column_diffs:
        for col in diff.column_diffs:
            col_symbol = CHANGE_SYMBOLS.get(col.change_type, "?")
            col_color = CHANGE_COLORS.get(col.change_type, "")
            detail = f"{opts.indent}{col_symbol} {col.column_name}"
            if col.old_definition and col.new_definition:
                detail += f": {col.old_definition} -> {col.new_definition}"
            elif col.new_definition:
                detail += f": {col.new_definition}"
            elif col.old_definition:
                detail += f": {col.old_definition}"
            lines.append(_colorize(detail, col_color, opts.use_color))

    return "\n".join(lines)


def render_diff_list(
    diffs: List[TableDiff], options: Optional[RenderOptions] = None
) -> str:
    opts = options or RenderOptions()
    if not diffs:
        return "No schema differences found."
    sections = [render_table_diff(d, opts) for d in diffs]
    return "\n\n".join(sections)
