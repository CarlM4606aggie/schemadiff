"""Prune reporter: renders pruning results as text or Markdown."""

from __future__ import annotations

from typing import List

from schemadiff.core import TableDiff, ChangeType
from schemadiff.pruner import PruneOptions, prune_diffs, prune_summary


def _change_label(ct: ChangeType) -> str:
    return ct.value if hasattr(ct, "value") else str(ct)


def render_prune_text(
    original: List[TableDiff],
    options: PruneOptions,
) -> str:
    """Return a plain-text report describing what pruning would remove."""
    pruned = prune_diffs(original, options)
    lines: List[str] = []
    lines.append("=== Prune Report ===")
    lines.append(prune_summary(original, pruned))

    removed = [d for d in original if d not in pruned]
    if removed:
        lines.append("\nRemoved diffs:")
        for diff in removed:
            lines.append(f"  - [{_change_label(diff.change_type)}] {diff.table_name}")
    else:
        lines.append("\nNo diffs were removed.")

    lines.append("\nRetained diffs:")
    if pruned:
        for diff in pruned:
            lines.append(f"  + [{_change_label(diff.change_type)}] {diff.table_name}")
    else:
        lines.append("  (none)")

    return "\n".join(lines)


def render_prune_markdown(
    original: List[TableDiff],
    options: PruneOptions,
) -> str:
    """Return a Markdown report describing what pruning would remove."""
    pruned = prune_diffs(original, options)
    removed = [d for d in original if d not in pruned]

    lines: List[str] = []
    lines.append("## Prune Report")
    lines.append("")
    lines.append(prune_summary(original, pruned))
    lines.append("")

    if removed:
        lines.append("### Removed")
        for diff in removed:
            lines.append(f"- `{diff.table_name}` — {_change_label(diff.change_type)}")
        lines.append("")

    lines.append("### Retained")
    if pruned:
        for diff in pruned:
            lines.append(f"- `{diff.table_name}` — {_change_label(diff.change_type)}")
    else:
        lines.append("_No diffs retained._")

    return "\n".join(lines)
