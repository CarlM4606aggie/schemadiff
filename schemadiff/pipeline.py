"""High-level pipeline that chains compare → filter → sort → group → report."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from schemadiff.comparator import compare_snapshots
from schemadiff.core import TableDiff
from schemadiff.filter import filter_diffs
from schemadiff.grouper import group_by_change_type, group_by_risk, group_summary
from schemadiff.reporter import generate_report
from schemadiff.snapshot import SchemaSnapshot
from schemadiff.sorter import sort_diffs
from schemadiff.summary import build_summary


@dataclass
class PipelineResult:
    """Holds the output of a full diff pipeline run."""

    diffs: List[TableDiff]
    by_change_type: Dict[str, List[TableDiff]]
    by_risk: Dict[str, List[TableDiff]]
    change_type_counts: Dict[str, int]
    risk_counts: Dict[str, int]
    report: str
    summary_text: str


@dataclass
class PipelineConfig:
    """Configuration options for the diff pipeline."""

    tables: Optional[List[str]] = None          # restrict to these table names
    change_types: Optional[List[str]] = None    # restrict to these change types
    sort_by: str = "table_name"                 # sort field
    reverse: bool = False
    report_title: str = "Schema Migration Diff"
    report_format: str = "text"                 # 'text' or 'markdown'
    include_summary: bool = True


def run_pipeline(
    snapshot_a: SchemaSnapshot,
    snapshot_b: SchemaSnapshot,
    config: Optional[PipelineConfig] = None,
) -> PipelineResult:
    """Run the full diff pipeline and return a structured result.

    Steps:
        1. Compare snapshots to produce raw diffs.
        2. Filter diffs according to config.
        3. Sort diffs.
        4. Group diffs by change type and risk.
        5. Build report and summary text.
    """
    if config is None:
        config = PipelineConfig()

    # 1. Compare
    diffs: List[TableDiff] = compare_snapshots(snapshot_a, snapshot_b)

    # 2. Filter
    filter_kwargs = {}
    if config.tables:
        filter_kwargs["table_names"] = config.tables
    if config.change_types:
        filter_kwargs["change_types"] = config.change_types
    if filter_kwargs:
        diffs = filter_diffs(diffs, **filter_kwargs)

    # 3. Sort
    diffs = sort_diffs(diffs, sort_by=config.sort_by, reverse=config.reverse)

    # 4. Group
    by_change_type = group_by_change_type(diffs)
    by_risk = group_by_risk(diffs)

    # 5. Report & summary
    report = generate_report(
        diffs,
        title=config.report_title,
        include_summary=config.include_summary,
    )
    summary = build_summary(diffs)
    summary_text = (
        f"{summary.total_column_changes()} column change(s) across "
        f"{len(diffs)} table(s)."
    )

    return PipelineResult(
        diffs=diffs,
        by_change_type=by_change_type,
        by_risk=by_risk,
        change_type_counts=group_summary(by_change_type),
        risk_counts=group_summary(by_risk),
        report=report,
        summary_text=summary_text,
    )
