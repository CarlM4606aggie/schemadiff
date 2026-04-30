"""CLI integration helpers for the renderer module."""

import sys
from typing import List, Optional
from schemadiff.core import TableDiff
from schemadiff.renderer import RenderOptions, render_diff_list


def _supports_color(stream=None) -> bool:
    """Detect whether the output stream likely supports ANSI color codes."""
    stream = stream or sys.stdout
    return hasattr(stream, "isatty") and stream.isatty()


def render_to_console(
    diffs: List[TableDiff],
    *,
    color: Optional[bool] = None,
    show_column_details: bool = True,
    indent: str = "  ",
    stream=None,
) -> None:
    """Render a list of TableDiff objects to the console.

    Args:
        diffs: List of TableDiff instances to render.
        color: Force color on/off. Defaults to auto-detect from TTY.
        show_column_details: Whether to include per-column diff lines.
        indent: Indentation string for column detail lines.
        stream: Output stream. Defaults to sys.stdout.
    """
    stream = stream or sys.stdout
    use_color = color if color is not None else _supports_color(stream)
    opts = RenderOptions(
        use_color=use_color,
        show_column_details=show_column_details,
        indent=indent,
    )
    output = render_diff_list(diffs, opts)
    stream.write(output + "\n")


def render_to_string(
    diffs: List[TableDiff],
    *,
    color: bool = False,
    show_column_details: bool = True,
    indent: str = "  ",
) -> str:
    """Render diffs to a plain string (no side effects).

    Args:
        diffs: List of TableDiff instances.
        color: Whether to include ANSI color codes.
        show_column_details: Whether to include per-column diff lines.
        indent: Indentation string for column detail lines.

    Returns:
        Rendered string.
    """
    opts = RenderOptions(
        use_color=color,
        show_column_details=show_column_details,
        indent=indent,
    )
    return render_diff_list(diffs, opts)
