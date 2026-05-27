#!/usr/bin/env python3
"""
WabbleSpec staleness-checker.

Reads all drawers in .wabblespec/memory/wings/.
Counts execution receipts written after each drawer's written_at.
Applies staleness transitions per rules/staleness-thresholds.md.
Writes transitions back to drawer files and index.json.

Exit 0 = success. Exit 1 = error. Prints summary to stdout.

Usage:
  python modules/l5/memory/scripts/staleness-checker.py
  python modules/l5/memory/scripts/staleness-checker.py --dry-run
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    for p in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents, Path.cwd(), *Path.cwd().parents]:
        if (p / ".wabblespec").is_dir():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            break
    from _shared.memory_backend import get_knowledge_graph
    _HAS_KG = True
except ImportError:
    _HAS_KG = False


THRESHOLDS = {
    "FRESH_TO_AGING": 5,
    "AGING_TO_STALE": 10,
    "STALE_TO_EXPIRED": 20,
}

VALID_TRANSITIONS: dict[str, list[str]] = {
    "FRESH":                ["AGING", "STALE", "NEEDS_REVERIFICATION", "SUPERSEDED"],
    "AGING":                ["STALE", "NEEDS_REVERIFICATION", "SUPERSEDED"],
    "STALE":                ["EXPIRED", "FRESH", "NEEDS_REVERIFICATION"],
    "EXPIRED":              ["FRESH"],
    "NEEDS_REVERIFICATION": ["FRESH", "EXPIRED"],
    "SUPERSEDED":           [],
}

SKIP_STATES = {"SUPERSEDED", "EXPIRED"}


def find_ws_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        candidate = p / ".wabblespec"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("No .wabblespec directory found from cwd")


def load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_json(path: Path, data: dict | list) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_ts(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def count_receipts_since(receipts_dir: Path, since_ts: str) -> int:
    since = parse_ts(since_ts)
    if since is None:
        return 0
    count = 0
    for p in receipts_dir.glob("*.json"):
        r = load_json(p)
        if isinstance(r, dict):
            rt = parse_ts(r.get("timestamp"))
            if rt and rt > since:
                count += 1
    return count


def compute_target_state(
    current: str, receipt_count: int, expires_at: str | None
) -> str | None:
    now = datetime.now(timezone.utc)
    exp = parse_ts(expires_at)
    if exp and now >= exp:
        return "EXPIRED"

    if current == "FRESH" and receipt_count >= THRESHOLDS["FRESH_TO_AGING"]:
        return "AGING"
    if current == "AGING" and receipt_count >= THRESHOLDS["AGING_TO_STALE"]:
        return "STALE"
    if current == "STALE" and receipt_count >= THRESHOLDS["STALE_TO_EXPIRED"]:
        return "EXPIRED"
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec staleness checker")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    args = parser.parse_args()

    try:
        ws_root = find_ws_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    receipts_dir = ws_root / "receipts"
    memory_root = ws_root / "memory"
    wings_root = memory_root / "wings"
    index_path = memory_root / "index.json"

    if not wings_root.exists():
        print("No wings directory found — no drawers to check.")
        sys.exit(0)

    index = load_json(index_path)
    if not isinstance(index, dict):
        index = {"drawers": []}

    drawer_paths = list(wings_root.rglob("*.json"))
    transitions: list[dict] = []
    errors: list[str] = []
    checked = 0

    for drawer_path in drawer_paths:
        drawer = load_json(drawer_path)
        if not isinstance(drawer, dict):
            errors.append(f"parse error: {drawer_path}")
            continue

        checked += 1
        current = drawer.get("staleness_state", "FRESH")
        if current in SKIP_STATES:
            continue

        written_at = drawer.get("written_at", "")
        expires_at = drawer.get("expires_at")
        receipt_count = count_receipts_since(receipts_dir, written_at)
        target = compute_target_state(current, receipt_count, expires_at)

        if not target:
            continue

        permitted = target in VALID_TRANSITIONS.get(current, [])
        record = {
            "drawer_id": drawer.get("id", drawer_path.name),
            "path": str(drawer_path.relative_to(ws_root)),
            "from": current,
            "to": target,
            "receipt_count": receipt_count,
            "permitted": permitted,
            "applied": False,
        }

        if not args.dry_run and permitted:
            drawer["staleness_state"] = target
            drawer.setdefault("provenance", []).append({
                "event": "TRANSITION",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "staleness-checker",
                "from_state": current,
                "to_state": target,
                "note": "Automatic threshold-based transition",
            })
            save_json(drawer_path, drawer)
            for entry in index.get("drawers", []):
                if entry.get("id") == drawer.get("id"):
                    entry["staleness_state"] = target
                    break
            record["applied"] = True

        transitions.append(record)

    if not args.dry_run and transitions:
        save_json(index_path, index)

    # KG invalidation for EXPIRED / SUPERSEDED transitions
    if not args.dry_run and _HAS_KG:
        kg_path = ws_root / "memory" / "knowledge_graph.sqlite3"
        if kg_path.exists():
            now_iso = datetime.now(timezone.utc).isoformat()
            kg = get_knowledge_graph()
            for t in transitions:
                if t["applied"] and t["to"] in ("EXPIRED", "SUPERSEDED"):
                    try:
                        kg.invalidate(
                            subject=t["drawer_id"],
                            predicate="is_active",
                            obj="true",
                            ended=now_iso,
                        )
                    except Exception:
                        pass
            kg.close()

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"staleness-checker {prefix}complete")
    print(f"  drawers checked  : {checked}")
    print(f"  transitions found: {len(transitions)}")
    for t in transitions:
        if args.dry_run:
            status = "WOULD APPLY" if t["permitted"] else "INVALID TRANSITION"
        else:
            status = "APPLIED" if t["applied"] else "INVALID TRANSITION (skipped)"
        print(f"  {t['drawer_id']}: {t['from']} -> {t['to']} ({t['receipt_count']} receipts) [{status}]")
    if errors:
        print(f"  errors: {len(errors)}")
        for e in errors:
            print(f"    {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
