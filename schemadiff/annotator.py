"""Annotate a list of TaggedDiffs with human-readable notes."""

from typing import Callable, Dict, List, Optional
from schemadiff.core import ChangeType
from schemadiff.tagger import TaggedDiff


AnnotatorFn = Callable[[TaggedDiff], Optional[str]]


# Default note generators keyed by tag name
_DEFAULT_NOTES: Dict[str, str] = {
    "breaking": "⚠️  Breaking change — review before deploying.",
    "additive": "✅  Additive change — generally safe to apply.",
    "destructive": "🗑️  Column(s) will be dropped — ensure data is migrated.",
}


@dataclass_workaround := None  # noqa — plain class below


class AnnotatedDiff:
    """A TaggedDiff enriched with a list of annotation notes."""

    def __init__(self, tagged: TaggedDiff, notes: List[str]) -> None:
        self.tagged = tagged
        self.notes = notes

    @property
    def diff(self):
        return self.tagged.diff

    @property
    def tags(self):
        return self.tagged.tags

    def __repr__(self) -> str:
        return (
            f"AnnotatedDiff(table={self.diff.table_name!r}, "
            f"notes={self.notes})"
        )


def annotate(
    tagged_diffs: List[TaggedDiff],
    custom_notes: Optional[Dict[str, str]] = None,
) -> List[AnnotatedDiff]:
    """Attach notes to each TaggedDiff based on its tags.

    Args:
        tagged_diffs: Output from :func:`schemadiff.tagger.tag_diffs`.
        custom_notes: Optional mapping of tag -> note string to override or
            extend the built-in defaults.

    Returns:
        List of AnnotatedDiff instances.
    """
    note_map = {**_DEFAULT_NOTES, **(custom_notes or {})}
    result: List[AnnotatedDiff] = []
    for td in tagged_diffs:
        notes = [note_map[tag] for tag in td.tags if tag in note_map]
        result.append(AnnotatedDiff(tagged=td, notes=notes))
    return result


def format_annotated(annotated_diffs: List[AnnotatedDiff]) -> str:
    """Render annotated diffs as a plain-text summary."""
    lines: List[str] = []
    for ad in annotated_diffs:
        change = ad.diff.change_type.value.upper()
        lines.append(f"[{change}] {ad.diff.table_name}")
        for note in ad.notes:
            lines.append(f"  {note}")
    return "\n".join(lines)
