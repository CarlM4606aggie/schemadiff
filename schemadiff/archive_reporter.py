"""Generate human-readable reports from a DiffArchive."""

from __future__ import annotations

from typing import List, Optional

from schemadiff.archiver import ArchiveEntry, DiffArchive


def _format_entry(entry: ArchiveEntry, index: int) -> str:
    lines = [
        f"  [{index}] {entry.label}",
        f"      timestamp    : {entry.timestamp}",
        f"      digest       : {entry.digest[:16]}...",
        f"      total changes: {entry.total_changes}",
    ]
    if entry.diffs:
        lines.append("      tables affected:")
        for d in entry.diffs:
            lines.append(f"        - {d['table']} ({d['change_type']})")
    return "\n".join(lines)


def report_archive(
    archive: DiffArchive,
    title: str = "Schema Diff Archive",
    max_entries: Optional[int] = None,
) -> str:
    """Return a formatted text report of all archive entries."""
    entries = archive.entries
    if max_entries is not None:
        entries = entries[:max_entries]

    lines: List[str] = [
        f"=== {title} ===",
        f"Total entries: {len(archive.entries)}",
    ]

    if not entries:
        lines.append("  (no entries recorded)")
        return "\n".join(lines)

    lines.append("")
    for i, entry in enumerate(entries):
        lines.append(_format_entry(entry, i))
        lines.append("")

    return "\n".join(lines).rstrip()


def diff_entries(
    entry_a: ArchiveEntry,
    entry_b: ArchiveEntry,
) -> str:
    """Return a brief comparison between two archive entries."""
    lines = [
        "--- Archive Entry Comparison ---",
        f"  A: {entry_a.label} ({entry_a.timestamp})",
        f"  B: {entry_b.label} ({entry_b.timestamp})",
        "",
    ]

    if entry_a.digest == entry_b.digest:
        lines.append("  Result: IDENTICAL (same digest)")
        return "\n".join(lines)

    delta = entry_b.total_changes - entry_a.total_changes
    direction = "+" if delta >= 0 else ""
    lines.append(f"  Change delta: {direction}{delta}")

    tables_a = {d["table"] for d in entry_a.diffs}
    tables_b = {d["table"] for d in entry_b.diffs}
    new_tables = tables_b - tables_a
    removed_tables = tables_a - tables_b

    if new_tables:
        lines.append(f"  New tables in B  : {', '.join(sorted(new_tables))}")
    if removed_tables:
        lines.append(f"  Removed from B   : {', '.join(sorted(removed_tables))}")
    if not new_tables and not removed_tables:
        lines.append("  Same tables affected, contents differ.")

    return "\n".join(lines)
