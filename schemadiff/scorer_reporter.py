"""Renders DiffScore results as human-readable text or markdown."""

from typing import List
from schemadiff.scorer import DiffScore, score_diffs


def _risk_label(score: int) -> str:
    if score == 0:
        return "none"
    elif score <= 3:
        return "low"
    elif score <= 7:
        return "medium"
    else:
        return "high"


def _section(title: str, char: str = "-") -> str:
    return f"{title}\n{char * len(title)}"


def render_score_text(scores: List[DiffScore]) -> str:
    """Render a list of DiffScore objects as plain text."""
    if not scores:
        return "No diffs to score.\n"

    lines = [_section("Migration Risk Scores"), ""]
    total = sum(s.score for s in scores)

    for ds in scores:
        label = _risk_label(ds.score)
        lines.append(f"  [{label.upper():6s}] {ds.table_name} (score: {ds.score})")
        if ds.reasons:
            for reason in ds.reasons:
                lines.append(f"           - {reason}")

    lines.append("")
    lines.append(f"Total risk score : {total}")
    lines.append(f"Overall risk     : {_risk_label(total).upper()}")
    lines.append("")
    return "\n".join(lines)


def render_score_markdown(scores: List[DiffScore]) -> str:
    """Render a list of DiffScore objects as markdown."""
    if not scores:
        return "_No diffs to score._\n"

    total = sum(s.score for s in scores)
    lines = ["## Migration Risk Scores", ""]
    lines.append("| Table | Score | Risk | Reasons |")
    lines.append("|-------|-------|------|---------|")

    for ds in scores:
        label = _risk_label(ds.score)
        reasons = "; ".join(ds.reasons) if ds.reasons else "—"
        lines.append(f"| `{ds.table_name}` | {ds.score} | {label} | {reasons} |")

    lines.append("")
    lines.append(f"**Total score:** {total} &nbsp; **Overall risk:** {_risk_label(total)}")
    lines.append("")
    return "\n".join(lines)
