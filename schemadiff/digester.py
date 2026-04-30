"""Digester: produces a stable fingerprint/hash for schema snapshots and diff lists."""

import hashlib
import json
from typing import List

from schemadiff.core import TableDiff, ChangeType
from schemadiff.snapshot import SchemaSnapshot


def _snapshot_to_stable_dict(snapshot: SchemaSnapshot) -> dict:
    """Convert a snapshot to a deterministic dict suitable for hashing."""
    tables = {}
    for name in sorted(snapshot.table_names()):
        table = snapshot.get_table(name)
        columns = {}
        for col_name in sorted(table.get("columns", {}).keys()):
            columns[col_name] = table["columns"][col_name]
        tables[name] = {"columns": columns}
    return {"tables": tables}


def digest_snapshot(snapshot: SchemaSnapshot, algorithm: str = "sha256") -> str:
    """Return a hex digest fingerprint of a schema snapshot."""
    stable = _snapshot_to_stable_dict(snapshot)
    raw = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    h = hashlib.new(algorithm)
    h.update(raw.encode("utf-8"))
    return h.hexdigest()


def _diff_to_stable_dict(diff: TableDiff) -> dict:
    """Convert a TableDiff to a deterministic dict."""
    col_diffs = []
    for cd in sorted(diff.column_diffs, key=lambda c: c.column_name):
        col_diffs.append({
            "column": cd.column_name,
            "change_type": cd.change_type.value,
            "old": cd.old_definition,
            "new": cd.new_definition,
        })
    return {
        "table": diff.table_name,
        "change_type": diff.change_type.value,
        "column_diffs": col_diffs,
    }


def digest_diffs(diffs: List[TableDiff], algorithm: str = "sha256") -> str:
    """Return a hex digest fingerprint of a list of TableDiff objects."""
    stable = [_diff_to_stable_dict(d) for d in sorted(diffs, key=lambda d: d.table_name)]
    raw = json.dumps(stable, sort_keys=True, separators=(",", ":"))
    h = hashlib.new(algorithm)
    h.update(raw.encode("utf-8"))
    return h.hexdigest()


def digests_match(a: str, b: str) -> bool:
    """Compare two digest strings in constant time."""
    return hmac_compare(a, b)


def hmac_compare(a: str, b: str) -> bool:
    import hmac as _hmac
    return _hmac.compare_digest(a.encode(), b.encode())
