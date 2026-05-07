"""High-level pipeline combining comparison, reporting, and optional filtering."""

from dataclasses import dataclass, field
from typing import List, Optional

from schemadiff.snapshot import SchemaSnapshot
from schemadiff.comparator import compare_snapshots
from schemadiff.filter import filter_diffs
from schemadiff.core import TableDiff
from schemadiff.comparator_reporter import render_comparator_text, render_comparator_markdown
from schemadiff.summary import build_summary, DiffSummary


@dataclass
class ComparatorPipelineConfig:
    title: str = "Schema Comparison"
    output_format: str = "text"  # "text" or "markdown"
    table_filter: Optional[List[str]] = None
    change_type_filter: Optional[str] = None  # "added", "dropped", "modified"


@dataclass
class ComparatorPipelineResult:
    diffs: List[TableDiff]
    summary: DiffSummary
    report: str
    config: ComparatorPipelineConfig = field(repr=False)

    @property
    def has_changes(self) -> bool:
        return self.summary.has_changes


def run_comparator_pipeline(
    snapshot_a: SchemaSnapshot,
    snapshot_b: SchemaSnapshot,
    config: Optional[ComparatorPipelineConfig] = None,
) -> ComparatorPipelineResult:
    """Compare two snapshots and return a structured pipeline result."""
    if config is None:
        config = ComparatorPipelineConfig()

    diffs = compare_snapshots(snapshot_a, snapshot_b)

    if config.table_filter or config.change_type_filter:
        diffs = filter_diffs(
            diffs,
            table_names=config.table_filter,
            change_type=config.change_type_filter,
        )

    summary = build_summary(diffs)

    if config.output_format == "markdown":
        report = render_comparator_markdown(diffs, title=config.title)
    else:
        report = render_comparator_text(diffs, title=config.title)

    return ComparatorPipelineResult(
        diffs=diffs,
        summary=summary,
        report=report,
        config=config,
    )
