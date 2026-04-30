"""Format and display WatchEvents for console output."""

from typing import List

from schemadiff.watcher import WatchEvent
from schemadiff.reporter import generate_report
from schemadiff.summary import build_summary


def format_watch_event(event: WatchEvent, use_color: bool = True) -> str:
    """Return a human-readable string describing a WatchEvent.

    Args:
        event: The WatchEvent to format.
        use_color: Whether to include ANSI colour codes.

    Returns:
        Formatted multi-line string suitable for console output.
    """
    GREEN = "\033[32m" if use_color else ""
    YELLOW = "\033[33m" if use_color else ""
    RED = "\033[31m" if use_color else ""
    RESET = "\033[0m" if use_color else ""
    BOLD = "\033[1m" if use_color else ""

    import datetime
    ts = datetime.datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S")

    header = f"{BOLD}[schemadiff watcher]{RESET} Change detected at {ts}"
    source = f"  Baseline : {event.previous_path}"
    target = f"  Current  : {event.current_path}"

    if not event.has_changes:
        body = f"{GREEN}No schema differences found.{RESET}"
        return "\n".join([header, source, target, body])

    summary = build_summary(event.diffs)
    counts = summary.change_counts_by_type()

    count_parts: List[str] = []
    if counts.get("added", 0):
        count_parts.append(f"{GREEN}+{counts['added']} added{RESET}")
    if counts.get("dropped", 0):
        count_parts.append(f"{RED}-{counts['dropped']} dropped{RESET}")
    if counts.get("modified", 0):
        count_parts.append(f"{YELLOW}~{counts['modified']} modified{RESET}")

    summary_line = "  Changes  : " + ", ".join(count_parts)
    report = generate_report(event.diffs, title=None, include_summary=False)

    return "\n".join([header, source, target, summary_line, "", report])


def print_watch_event(event: WatchEvent, use_color: bool = True) -> None:
    """Print a formatted WatchEvent to stdout."""
    print(format_watch_event(event, use_color=use_color))
    print()
