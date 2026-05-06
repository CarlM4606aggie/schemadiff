"""Split a list of TableDiff objects into batches for staged migrations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from schemadiff.core import ChangeType, TableDiff


@dataclass
class DiffBatch:
    """A named batch of TableDiff objects representing one migration stage."""

    name: str
    diffs: List[TableDiff] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.diffs)

    def __repr__(self) -> str:
        return f"DiffBatch(name={self.name!r}, count={len(self)})"

    def is_empty(self) -> bool:
        return len(self.diffs) == 0


def split_by_change_type(diffs: List[TableDiff]) -> List[DiffBatch]:
    """Return one batch per ChangeType, ordered: ADDED, MODIFIED, DROPPED.

    Empty batches are omitted.
    """
    order = [ChangeType.ADDED, ChangeType.MODIFIED, ChangeType.DROPPED]
    buckets: dict[ChangeType, List[TableDiff]] = {ct: [] for ct in order}

    for diff in diffs:
        if diff.change_type in buckets:
            buckets[diff.change_type].append(diff)

    batches = []
    for ct in order:
        items = buckets[ct]
        if items:
            batches.append(DiffBatch(name=ct.value, diffs=items))
    return batches


def split_by_size(diffs: List[TableDiff], batch_size: int) -> List[DiffBatch]:
    """Partition diffs into fixed-size batches.

    Args:
        diffs: The full list of TableDiff objects to split.
        batch_size: Maximum number of diffs per batch (must be >= 1).

    Returns:
        A list of DiffBatch objects.
    """
    if batch_size < 1:
        raise ValueError(f"batch_size must be >= 1, got {batch_size}")

    batches = []
    for i in range(0, len(diffs), batch_size):
        chunk = diffs[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        batches.append(DiffBatch(name=f"batch_{batch_num}", diffs=chunk))
    return batches


def split_by_prefix(diffs: List[TableDiff], delimiter: str = "_") -> List[DiffBatch]:
    """Group diffs into batches by the table-name prefix before *delimiter*.

    Tables with no delimiter in their name are placed in a batch named
    ``"default"``.
    """
    buckets: dict[str, List[TableDiff]] = {}

    for diff in diffs:
        if delimiter in diff.table_name:
            prefix = diff.table_name.split(delimiter, 1)[0]
        else:
            prefix = "default"
        buckets.setdefault(prefix, []).append(diff)

    return [
        DiffBatch(name=prefix, diffs=items)
        for prefix, items in sorted(buckets.items())
    ]
