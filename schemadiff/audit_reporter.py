"""Human-readable reports for audit logs."""

from __future__ import annotations

from typing import List

from schemadiff.auditor import AuditEntry, AuditLog


def _format_entry(entry: AuditEntry, index: int) -> str:
    lines = [
        f"#{index}  {entry.timestamp}",
        f"  User      : {entry.user}",
        f"  Snapshot A: {entry.snapshot_a}",
        f"  Snapshot B: {entry.snapshot_b}",
        f"  Diffs     : {entry.diff_count}",
        f"  Changes   : {', '.join(entry.change_types) if entry.change_types else 'none'}",
    ]
    if entry.note:
        lines.append(f"  Note      : {entry.note}")
    return "\n".join(lines)


def render_audit_text(log: AuditLog) -> str:
    """Render an audit log as plain text."""
    if not log.entries:
        return "No audit entries recorded."
    sections = ["=== Schema Diff Audit Log ==="]
    for i, entry in enumerate(log.entries, start=1):
        sections.append(_format_entry(entry, i))
    return "\n\n".join(sections)


def render_audit_markdown(log: AuditLog) -> str:
    """Render an audit log as a Markdown table."""
    if not log.entries:
        return "_No audit entries recorded._"

    header = "| # | Timestamp | User | Snapshot A | Snapshot B | Diffs | Changes |"
    separator = "|---|-----------|------|------------|------------|-------|---------|"
    rows = [header, separator]
    for i, e in enumerate(log.entries, start=1):
        changes = ", ".join(e.change_types) if e.change_types else "—"
        rows.append(
            f"| {i} | {e.timestamp} | {e.user} | {e.snapshot_a} "
            f"| {e.snapshot_b} | {e.diff_count} | {changes} |"
        )
    return "\n".join(rows)


def diff_entries(log: AuditLog, snapshot_a: str = "", snapshot_b: str = "") -> List[AuditEntry]:
    """Filter entries by snapshot name substring."""
    return [
        e for e in log.entries
        if (not snapshot_a or snapshot_a in e.snapshot_a)
        and (not snapshot_b or snapshot_b in e.snapshot_b)
    ]
