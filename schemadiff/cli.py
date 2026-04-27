"""Command-line interface for schemadiff."""

import argparse
import sys
from pathlib import Path

from schemadiff.snapshot import SchemaSnapshot
from schemadiff.core import diff_snapshots
from schemadiff.exporter import export_diff, SUPPORTED_FORMATS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="schemadiff",
        description="Compare database schema snapshots and output migration diffs.",
    )
    parser.add_argument("snapshot_v1", help="Path to the baseline schema snapshot (JSON).")
    parser.add_argument("snapshot_v2", help="Path to the target schema snapshot (JSON).")
    parser.add_argument(
        "--format",
        choices=SUPPORTED_FORMATS,
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.add_argument(
        "--title",
        default="Schema Migration Diff",
        help="Title for the diff report.",
    )
    parser.add_argument(
        "--no-summary",
        action="store_true",
        default=False,
        help="Omit the summary section from the report.",
    )
    return parser


def run(argv=None) -> int:
    """Entry point for the CLI. Returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    v1_path = Path(args.snapshot_v1)
    v2_path = Path(args.snapshot_v2)

    if not v1_path.exists():
        print(f"Error: snapshot file not found: {v1_path}", file=sys.stderr)
        return 1
    if not v2_path.exists():
        print(f"Error: snapshot file not found: {v2_path}", file=sys.stderr)
        return 1

    try:
        snap1 = SchemaSnapshot.load(str(v1_path))
        snap2 = SchemaSnapshot.load(str(v2_path))
    except Exception as exc:
        print(f"Error loading snapshots: {exc}", file=sys.stderr)
        return 1

    diffs = diff_snapshots(snap1, snap2)

    output = export_diff(
        diffs,
        output_format=args.format,
        output_path=args.output,
        title=args.title,
        include_summary=not args.no_summary,
    )

    if not args.output:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(run())
