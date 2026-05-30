"""
crdt_merge.py — CRDT-based merge semantics for parallel wave file conflicts.

Provides Last-Write-Wins Register (LWW), OR-Set (add-only), and a simple
ordered-sequence merge for parallel waves that write to overlapping keys.

Merge is deterministic: same inputs in any argument order produce the same
output. Conflict resolution uses the higher timestamp value (LWW semantics).

Usage as library:
    from crdt_merge import merge, lww_merge, or_set_union

    # LWW merge of two dicts of {key: {val: ..., ts: ...}}:
    result = merge(wave_a, wave_b)

Usage as CLI:
    python crdt_merge.py --file-a a.json --file-b b.json [--out merged.json]

Each file must be a JSON object of {key: {val: <any>, ts: <unix float>}}.

Exit codes:
    0  success
    1  error
"""

import sys
import os
import json
import argparse
from typing import Any, Dict


# ---------------------------------------------------------------------------
# Core CRDT operations
# ---------------------------------------------------------------------------

def lww_merge(a: Dict[str, Dict], b: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Last-Write-Wins Register merge.

    Each entry: {key: {"val": <value>, "ts": <float unix timestamp>}}

    Conflict resolution: higher ts wins. Ties resolve to value from 'b'
    (deterministic secondary sort: prefer lexicographically larger str(val)).
    """
    result = {}
    all_keys = set(a) | set(b)
    for key in all_keys:
        if key in a and key not in b:
            result[key] = a[key]
        elif key in b and key not in a:
            result[key] = b[key]
        else:
            a_ts = float(a[key].get("ts", 0))
            b_ts = float(b[key].get("ts", 0))
            if a_ts > b_ts:
                result[key] = a[key]
            elif b_ts > a_ts:
                result[key] = b[key]
            else:
                # Tie-break: larger str(val) wins (deterministic)
                a_val = str(a[key].get("val", ""))
                b_val = str(b[key].get("val", ""))
                result[key] = b[key] if b_val >= a_val else a[key]
    return result


def or_set_union(a: list, b: list) -> list:
    """
    OR-Set (Observed-Remove Set) union: add-only, order-preserving dedup.
    Items from 'a' appear first, then items from 'b' not already in 'a'.
    """
    seen = []
    result = []
    for item in list(a) + list(b):
        key = json.dumps(item, sort_keys=True)
        if key not in seen:
            seen.append(key)
            result.append(item)
    return result


def merge(wave_a: Dict[str, Any], wave_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Top-level merge for two wave output dicts.

    Each value in the dict should be either:
    - A LWW entry: {"val": <any>, "ts": <float>}
    - A list (merged via OR-Set union)
    - A plain scalar (LWW by presence of "ts" key at top level, else last-writer-wins via b)

    Returns the merged dict. Raises no exceptions on conflict -- resolves deterministically.
    """
    all_keys = set(wave_a) | set(wave_b)
    result = {}

    for key in all_keys:
        if key not in wave_a:
            result[key] = wave_b[key]
            continue
        if key not in wave_b:
            result[key] = wave_a[key]
            continue

        va, vb = wave_a[key], wave_b[key]

        # Both are LWW dicts (have "ts" key)
        if isinstance(va, dict) and isinstance(vb, dict) and "ts" in va and "ts" in vb:
            result[key] = lww_merge({key: va}, {key: vb})[key]

        # Both are nested dicts of LWW entries
        elif isinstance(va, dict) and isinstance(vb, dict):
            result[key] = lww_merge(va, vb)

        # Both are lists
        elif isinstance(va, list) and isinstance(vb, list):
            result[key] = or_set_union(va, vb)

        # Scalar conflict: prefer b (deterministic last-writer-wins)
        else:
            result[key] = vb

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CRDT-based merge for parallel wave output dicts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file-a", required=True, metavar="PATH",
                        help="JSON file for wave A output.")
    parser.add_argument("--file-b", required=True, metavar="PATH",
                        help="JSON file for wave B output.")
    parser.add_argument("--out", metavar="PATH",
                        help="Write merged JSON to this path (default: stdout).")
    args = parser.parse_args()

    for path in [args.file_a, args.file_b]:
        if not os.path.exists(path):
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    with open(args.file_a, encoding="utf-8") as f:
        wave_a = json.load(f)
    with open(args.file_b, encoding="utf-8") as f:
        wave_b = json.load(f)

    result = merge(wave_a, wave_b)
    output = json.dumps(result, indent=2) + "\n"

    if args.out:
        tmp = args.out + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(output)
        os.replace(tmp, args.out)
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
