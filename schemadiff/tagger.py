"""Tag diffs with user-defined labels for categorization and filtering."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from schemadiff.core import TableDiff, ChangeType


@dataclass
class TaggedDiff:
    """A TableDiff decorated with a set of string tags."""

    diff: TableDiff
    tags: List[str] = field(default_factory=list)

    def has_tag(self, tag: str) -> bool:
        return tag.lower() in (t.lower() for t in self.tags)

    def __repr__(self) -> str:
        return f"TaggedDiff(table={self.diff.table_name!r}, tags={self.tags})"


# Built-in automatic tagging rules
_AUTO_RULES: Dict[str, object] = {
    "breaking": lambda d: d.change_type == ChangeType.DROPPED
    or any(
        c.old_type != c.new_type
        for c in (d.column_diffs or [])
        if c.old_type and c.new_type
    ),
    "additive": lambda d: d.change_type == ChangeType.ADDED,
    "destructive": lambda d: any(
        c.change_type == ChangeType.DROPPED for c in (d.column_diffs or [])
    ),
}


def auto_tag(diff: TableDiff) -> List[str]:
    """Return automatically derived tags for a TableDiff."""
    return [tag for tag, rule in _AUTO_RULES.items() if rule(diff)]


def tag_diffs(
    diffs: List[TableDiff],
    extra_tags: Optional[Dict[str, List[str]]] = None,
) -> List[TaggedDiff]:
    """Wrap each diff in a TaggedDiff, applying auto tags and any extra_tags.

    Args:
        diffs: List of TableDiff objects to tag.
        extra_tags: Optional mapping of table_name -> list of additional tags.

    Returns:
        List of TaggedDiff instances.
    """
    extra_tags = extra_tags or {}
    result: List[TaggedDiff] = []
    for diff in diffs:
        tags = auto_tag(diff)
        tags += extra_tags.get(diff.table_name, [])
        result.append(TaggedDiff(diff=diff, tags=tags))
    return result


def filter_by_tag(tagged: List[TaggedDiff], tag: str) -> List[TaggedDiff]:
    """Return only TaggedDiffs that carry the given tag."""
    return [td for td in tagged if td.has_tag(tag)]
