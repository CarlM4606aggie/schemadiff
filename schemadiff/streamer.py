"""Stream diffs one at a time with optional filtering and transformation."""

from typing import Callable, Generator, Iterable, Optional
from schemadiff.core import TableDiff, ChangeType


class StreamOptions:
    """Configuration for diff streaming."""

    def __init__(
        self,
        change_types: Optional[list] = None,
        table_prefix: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        self.change_types = change_types
        self.table_prefix = table_prefix
        self.limit = limit


def _passes_filter(diff: TableDiff, opts: StreamOptions) -> bool:
    """Return True if diff matches all active filters in opts."""
    if opts.change_types and diff.change_type not in opts.change_types:
        return False
    if opts.table_prefix and not diff.table_name.lower().startswith(
        opts.table_prefix.lower()
    ):
        return False
    return True


def stream_diffs(
    diffs: Iterable[TableDiff],
    opts: Optional[StreamOptions] = None,
    transform: Optional[Callable[[TableDiff], TableDiff]] = None,
) -> Generator[TableDiff, None, None]:
    """Yield diffs one at a time, applying optional filtering and transformation.

    Args:
        diffs: Iterable of TableDiff objects.
        opts: Optional StreamOptions to filter results.
        transform: Optional callable applied to each yielded diff.

    Yields:
        TableDiff instances that pass all active filters.
    """
    opts = opts or StreamOptions()
    emitted = 0

    for diff in diffs:
        if opts.limit is not None and emitted >= opts.limit:
            break
        if not _passes_filter(diff, opts):
            continue
        if transform is not None:
            diff = transform(diff)
        yield diff
        emitted += 1


def collect_stream(
    diffs: Iterable[TableDiff],
    opts: Optional[StreamOptions] = None,
    transform: Optional[Callable[[TableDiff], TableDiff]] = None,
) -> list:
    """Convenience wrapper that collects stream_diffs into a list."""
    return list(stream_diffs(diffs, opts=opts, transform=transform))
