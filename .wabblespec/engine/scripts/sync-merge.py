#!/usr/bin/env python3
"""sync-merge.py — Deterministic conflict resolver for .wabblespec/ files.

Called by sync-pull.py when git rebase leaves conflict markers in a
.wabblespec/ file. Resolves conflicts without LLM calls.

Usage:
    python scripts/sync-merge.py <conflicted-file-path>

Resolution rules by file type:
  session/*     → always take OURS  (machine-specific session state)
  *.json        → union all keys; duplicate keys: take entry with later
                  timestamp field; if no timestamp, THEIRS wins
  *.md (log)    → append THEIRS after OURS with sync divider; deduplicate
                  identical lines  (log/observations files)
  *.md (other)  → take THEIRS  (remote is authoritative for docs)
  unknown       → write both sides with NEEDS_REVERIFICATION marker

After resolving, runs `git add <file>` so rebase --continue can proceed.

Exit codes:
  0  resolved and staged
  1  could not resolve (caller should abort the rebase)
"""
from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path


# ── Files treated as append-style logs (OURS + THEIRS both kept) ──────────────
# Match by suffix of the relative .wabblespec/ path
LOG_STYLE_NAMES = {
    "dream-log.json",
    "instinct-observations.md",
    "gap-map.md",
    "sync.log",
}

# ── Conflict marker parsing ────────────────────────────────────────────────────

MARKER_OURS_RE   = re.compile(r"^<<<<<<< (.+)$")
MARKER_SPLIT_RE  = re.compile(r"^=======$")
MARKER_THEIRS_RE = re.compile(r"^>>>>>>> (.+)$")


def _parse_conflict(text: str) -> tuple[str, str] | None:
    """
    Parse a file containing exactly one conflict block.
    Returns (ours, theirs) or None if no conflict markers found.
    Handles multi-block files by treating everything in OURS sections as ours
    and THEIRS sections as theirs.
    """
    ours_parts: list[str] = []
    theirs_parts: list[str] = []
    outside: list[str] = []
    state = "outside"  # "outside" | "ours" | "theirs"

    for line in text.splitlines(keepends=True):
        if MARKER_OURS_RE.match(line):
            state = "ours"
            continue
        if MARKER_SPLIT_RE.match(line.rstrip("\n")):
            state = "theirs"
            continue
        if MARKER_THEIRS_RE.match(line):
            state = "outside"
            continue

        if state == "ours":
            ours_parts.append(line)
        elif state == "theirs":
            theirs_parts.append(line)
        else:
            outside.append(line)

    # If no markers found, no conflict
    if not ours_parts and not theirs_parts:
        return None

    # Outside lines are common — prepend to both
    common = "".join(outside)
    ours_text   = common + "".join(ours_parts)
    theirs_text = common + "".join(theirs_parts)
    return ours_text, theirs_text


# ── JSON merge ─────────────────────────────────────────────────────────────────

def _ts_key(obj: object) -> str:
    """Extract the best timestamp string from a dict for comparison."""
    if not isinstance(obj, dict):
        return ""
    for key in ("timestamp", "completed_at", "started_at", "updated_at", "created_at", "exported_at"):
        val = obj.get(key, "")
        if isinstance(val, str) and val:
            return val
    return ""


def _merge_json_values(ours_val: object, theirs_val: object) -> object:
    """Merge two values for the same key. Latest timestamp wins for dicts."""
    if isinstance(ours_val, dict) and isinstance(theirs_val, dict):
        ours_ts = _ts_key(ours_val)
        theirs_ts = _ts_key(theirs_val)
        if theirs_ts > ours_ts:
            return theirs_val
        return ours_val

    if isinstance(ours_val, list) and isinstance(theirs_val, list):
        # Union: keep all unique entries (by JSON string identity)
        seen = set()
        merged: list = []
        for item in ours_val + theirs_val:
            key = json.dumps(item, sort_keys=True)
            if key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    # Scalar: THEIRS wins (remote is "incoming" in a pull)
    return theirs_val


def _merge_json_objects(ours: object, theirs: object) -> object:
    """Recursively union two JSON objects."""
    if isinstance(ours, dict) and isinstance(theirs, dict):
        result = dict(ours)
        for k, v in theirs.items():
            if k in result:
                result[k] = _merge_json_values(result[k], v)
            else:
                result[k] = v
        return result

    if isinstance(ours, list) and isinstance(theirs, list):
        return _merge_json_values(ours, theirs)

    # Scalar root — THEIRS wins
    return theirs


def resolve_json(ours_text: str, theirs_text: str) -> str:
    try:
        ours_obj   = json.loads(ours_text)
        theirs_obj = json.loads(theirs_text)
    except json.JSONDecodeError:
        # Can't parse — fall back to THEIRS
        return theirs_text

    merged = _merge_json_objects(ours_obj, theirs_obj)
    return json.dumps(merged, indent=2, ensure_ascii=False) + "\n"


# ── Markdown log merge ─────────────────────────────────────────────────────────

def resolve_md_log(ours_text: str, theirs_text: str) -> str:
    """Append THEIRS after OURS. Deduplicate identical lines."""
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    divider = f"\n<!-- sync-merge: {ts} -->\n"

    combined = ours_text.rstrip("\n") + divider + theirs_text.lstrip("\n")

    # Deduplicate identical non-empty lines while preserving order
    seen: set[str] = set()
    result_lines: list[str] = []
    for line in combined.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if stripped and stripped in seen:
            continue
        seen.add(stripped)
        result_lines.append(line)

    return "".join(result_lines)


# ── NEEDS_REVERIFICATION fallback ─────────────────────────────────────────────

def resolve_fallback(ours_text: str, theirs_text: str, file_path: Path) -> str:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"<!-- NEEDS_REVERIFICATION: sync-merge could not auto-resolve {file_path.name} at {ts} -->\n"
        f"<!-- OURS: -->\n"
        + ours_text
        + f"\n<!-- THEIRS: -->\n"
        + theirs_text
    )


# ── Git staging ────────────────────────────────────────────────────────────────

def _git_add(file_path: Path, root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "add", str(file_path)],
            cwd=root,
            capture_output=True,
            timeout=10,
        )
        return result.returncode == 0
    except Exception:  # noqa: BLE001
        return False


# ── Repo root ──────────────────────────────────────────────────────────────────

def _repo_root(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if (parent / ".wabblespec").exists():
            return parent
    return None


# ── Main ───────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: sync-merge.py <conflicted-file-path>", file=sys.stderr)
        return 1

    file_path = Path(argv[1]).resolve()
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        return 1

    root = _repo_root(file_path)
    if root is None:
        print("Cannot find WabbleSpec repo root", file=sys.stderr)
        return 1

    raw = file_path.read_text(encoding="utf-8", errors="replace")

    # Check for conflict markers
    parsed = _parse_conflict(raw)
    if parsed is None:
        # No conflict markers — just stage as-is
        _git_add(file_path, root)
        return 0

    ours_text, theirs_text = parsed

    # Determine relative path within .wabblespec/ for routing
    try:
        rel = file_path.relative_to(root / ".wabblespec")
    except ValueError:
        rel = file_path  # Not under .wabblespec — use fallback

    rel_str = str(rel).replace("\\", "/")
    file_name = file_path.name

    # Route by rule
    if rel_str.startswith("session/"):
        # Always take OURS for session state (machine-specific)
        resolved = ours_text

    elif file_path.suffix == ".json":
        if file_name in LOG_STYLE_NAMES:
            # JSON log files: try JSON merge first
            resolved = resolve_json(ours_text, theirs_text)
        else:
            resolved = resolve_json(ours_text, theirs_text)

    elif file_path.suffix == ".md":
        if file_name in LOG_STYLE_NAMES:
            resolved = resolve_md_log(ours_text, theirs_text)
        else:
            # Docs: THEIRS wins (remote is authoritative)
            resolved = theirs_text

    else:
        resolved = resolve_fallback(ours_text, theirs_text, file_path)

    file_path.write_text(resolved, encoding="utf-8")

    staged = _git_add(file_path, root)
    if not staged:
        print(f"Warning: could not git add {file_path}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
