"""Watch a snapshot file for changes and emit diffs when it updates."""

import time
import os
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from schemadiff.snapshot import SchemaSnapshot
from schemadiff.comparator import compare_snapshots
from schemadiff.core import TableDiff


@dataclass
class WatchEvent:
    """Emitted when a snapshot file changes and diffs are detected."""
    previous_path: str
    current_path: str
    diffs: List[TableDiff]
    timestamp: float = field(default_factory=time.time)

    @property
    def has_changes(self) -> bool:
        return len(self.diffs) > 0

    def __repr__(self) -> str:
        return (
            f"WatchEvent(diffs={len(self.diffs)}, "
            f"timestamp={self.timestamp:.2f})"
        )


def _get_mtime(path: str) -> Optional[float]:
    """Return file modification time, or None if file doesn't exist."""
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def watch_snapshot(
    baseline_path: str,
    current_path: str,
    callback: Callable[[WatchEvent], None],
    poll_interval: float = 2.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll current_path for changes and invoke callback with a WatchEvent.

    Compares current_path against baseline_path whenever the file's
    modification time changes.  Designed for use in long-running processes
    or CI watch-mode scripts.

    Args:
        baseline_path: Path to the reference (older) snapshot JSON.
        current_path: Path to the snapshot being monitored.
        callback: Callable invoked with a WatchEvent on each detected change.
        poll_interval: Seconds between filesystem polls.
        max_iterations: Stop after this many iterations (None = run forever).
    """
    last_mtime: Optional[float] = _get_mtime(current_path)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break

        time.sleep(poll_interval)
        iterations += 1

        current_mtime = _get_mtime(current_path)
        if current_mtime is None or current_mtime == last_mtime:
            continue

        last_mtime = current_mtime
        try:
            baseline = SchemaSnapshot.load(baseline_path)
            current = SchemaSnapshot.load(current_path)
            diffs = compare_snapshots(baseline, current)
        except Exception:
            continue

        event = WatchEvent(
            previous_path=baseline_path,
            current_path=current_path,
            diffs=diffs,
        )
        callback(event)
