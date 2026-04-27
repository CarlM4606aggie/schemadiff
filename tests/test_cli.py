"""Tests for the schemadiff CLI interface."""

import pytest
import argparse
from unittest.mock import patch, MagicMock
from io import StringIO

from schemadiff.cli import build_parser, run


@pytest.fixture
def parser():
    return build_parser()


@pytest.fixture
def snapshot_v1_path(tmp_path):
    import shutil
    src = "tests/fixtures/snapshot_v1.json"
    dest = tmp_path / "snapshot_v1.json"
    shutil.copy(src, dest)
    return str(dest)


@pytest.fixture
def snapshot_v2_path(tmp_path):
    import shutil
    src = "tests/fixtures/snapshot_v2.json"
    dest = tmp_path / "snapshot_v2.json"
    shutil.copy(src, dest)
    return str(dest)


class TestBuildParser:
    def test_parser_returns_argument_parser(self, parser):
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_requires_snapshot_args(self, parser):
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parser_accepts_two_snapshots(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json"])
        assert args.snapshot1 == "snap1.json"
        assert args.snapshot2 == "snap2.json"

    def test_parser_default_format_is_text(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json"])
        assert args.format == "text"

    def test_parser_accepts_format_option(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json", "--format", "markdown"])
        assert args.format == "markdown"

    def test_parser_accepts_json_format(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json", "--format", "json"])
        assert args.format == "json"

    def test_parser_accepts_output_option(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json", "--output", "out.txt"])
        assert args.output == "out.txt"

    def test_parser_default_output_is_none(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json"])
        assert args.output is None

    def test_parser_accepts_title_option(self, parser):
        args = parser.parse_args(["snap1.json", "snap2.json", "--title", "My Diff"])
        assert args.title == "My Diff"


class TestRun:
    def test_run_with_valid_snapshots_exits_zero(
        self, snapshot_v1_path, snapshot_v2_path, capsys
    ):
        with pytest.raises(SystemExit) as exc_info:
            run([snapshot_v1_path, snapshot_v2_path])
        assert exc_info.value.code == 0

    def test_run_outputs_text_to_stdout(
        self, snapshot_v1_path, snapshot_v2_path, capsys
    ):
        with pytest.raises(SystemExit):
            run([snapshot_v1_path, snapshot_v2_path])
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_run_with_markdown_format(
        self, snapshot_v1_path, snapshot_v2_path, capsys
    ):
        with pytest.raises(SystemExit):
            run([snapshot_v1_path, snapshot_v2_path, "--format", "markdown"])
        captured = capsys.readouterr()
        assert "#" in captured.out or len(captured.out) > 0

    def test_run_with_missing_file_exits_nonzero(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            run(["nonexistent_v1.json", "nonexistent_v2.json"])
        assert exc_info.value.code != 0

    def test_run_writes_output_to_file(
        self, snapshot_v1_path, snapshot_v2_path, tmp_path
    ):
        output_file = str(tmp_path / "output.txt")
        with pytest.raises(SystemExit):
            run([snapshot_v1_path, snapshot_v2_path, "--output", output_file])
        import os
        assert os.path.exists(output_file)
        with open(output_file) as f:
            content = f.read()
        assert len(content) > 0
