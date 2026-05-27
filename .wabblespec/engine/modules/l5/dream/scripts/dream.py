#!/usr/bin/env python3
"""
WabbleSpec Dream script.

Reads all drawers, applies EMA decay to confidence scores, writes:
  .wabblespec/state/memory/gap-map.md        -- actionable findings
  .wabblespec/state/memory/staleness-map.md  -- full drawer state table
  .wabblespec/state/memory/dream-log.json    -- run history (Phase 4 validation gate)

EMA formula: new_confidence = old_confidence * 0.9 + base_freshness * 0.1
base_freshness by staleness_state:
  FRESH=1.0, AGING=0.7, STALE=0.3, EXPIRED=0.0,
  NEEDS_REVERIFICATION=0.2, SUPERSEDED=0.0

This script writes no LLM instructions. Every output is deterministic.

Exit 0 = success. Exit 1 = error.

Usage:
  python modules/l5/dream/scripts/dream.py
  python modules/l5/dream/scripts/dream.py --dry-run
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Bootstrap ────────────────────────────────────────────────────────────────
# Minimal primer: find repo root and add to sys.path so _shared is importable.

def _primer() -> None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return


_primer()

try:
    from _shared.memory_backend import get_collection, memory_path
except ImportError:
    get_collection = None
    memory_path = None


# ── EMA config ────────────────────────────────────────────────────────────────

BASE_FRESHNESS: dict[str, float] = {
    "FRESH":                1.0,
    "AGING":                0.7,
    "STALE":                0.3,
    "EXPIRED":              0.0,
    "NEEDS_REVERIFICATION": 0.2,
    "SUPERSEDED":           0.0,
}

GAP_CONFIDENCE_THRESHOLD = 0.5  # drawers below this are actionable

# State display order for staleness-map (worst first)
STATE_ORDER = ["EXPIRED", "SUPERSEDED", "NEEDS_REVERIFICATION", "STALE", "AGING", "FRESH"]


# ── I/O helpers ───────────────────────────────────────────────────────────────

def find_ws_root() -> Path:
    """Return the .wabblespec directory. Uses the canonical sentinel walk."""
    try:
        from _shared.repo_root import find_repo_root
        return find_repo_root(Path(__file__)) / ".wabblespec"
    except Exception:
        # Fallback: walk from cwd (needed if _shared is not yet importable)
        for p in [Path.cwd(), *Path.cwd().parents]:
            if (p / ".wabblespec").is_dir():
                return p / ".wabblespec"
    raise FileNotFoundError(
        "No .wabblespec directory found. Run from inside the WabbleSpec checkout."
    )


def load_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_json(path: Path, data: dict | list) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


# ── EMA ───────────────────────────────────────────────────────────────────────

def apply_ema(old_confidence: float, staleness_state: str) -> float:
    base = BASE_FRESHNESS.get(staleness_state, 0.5)
    return round(old_confidence * 0.9 + base * 0.1, 4)


# ── Gap detection ─────────────────────────────────────────────────────────────

class Finding:
    def __init__(
        self,
        severity: str,      # CRITICAL | HIGH | MEDIUM
        kind: str,          # EXPIRED | LOW_CONFIDENCE | COVERAGE_GAP | NEEDS_REVERIFICATION
        subject: str,       # drawer id or room path
        detail: str,
        action: str,
    ) -> None:
        self.severity = severity
        self.kind = kind
        self.subject = subject
        self.detail = detail
        self.action = action


def detect_gaps(drawers: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    active_ids = {d["id"] for d in drawers if d.get("staleness_state") not in ("SUPERSEDED", "EXPIRED")}

    # Per-drawer findings
    for d in drawers:
        state = d.get("staleness_state", "FRESH")
        conf = d.get("new_confidence", d.get("confidence", 1.0))
        drawer_id = d.get("id", "unknown")
        topic = d.get("topic", drawer_id)
        wing = d.get("wing", "unknown")
        room = d.get("room", "unknown")
        superseded_by = d.get("superseded_by")

        if state == "EXPIRED":
            if superseded_by and superseded_by in active_ids:
                # Superseded and replacement exists — no gap
                continue
            findings.append(Finding(
                severity="CRITICAL",
                kind="EXPIRED",
                subject=drawer_id,
                detail=f"[{wing}/{room}] \"{topic}\" is EXPIRED — confidence {conf:.2f}",
                action=f"Archive to closets/ and write new drawer from verified source. "
                       f"Or mark SUPERSEDED with superseded_by pointing to replacement.",
            ))

        elif state == "NEEDS_REVERIFICATION":
            findings.append(Finding(
                severity="HIGH",
                kind="NEEDS_REVERIFICATION",
                subject=drawer_id,
                detail=f"[{wing}/{room}] \"{topic}\" flagged NEEDS_REVERIFICATION — confidence {conf:.2f}",
                action="Re-read upstream source. Run Memory Transition to FRESH with source confirmation in provenance.",
            ))

        elif conf < GAP_CONFIDENCE_THRESHOLD and state not in ("SUPERSEDED",):
            findings.append(Finding(
                severity="HIGH",
                kind="LOW_CONFIDENCE",
                subject=drawer_id,
                detail=f"[{wing}/{room}] \"{topic}\" confidence {conf:.2f} (state: {state})",
                action="Verify evidence is still accurate. Re-read source before next wave execution that cites this drawer.",
            ))

    # Coverage gap: rooms where no FRESH or AGING drawer exists
    rooms: dict[str, list[dict]] = {}
    for d in drawers:
        key = f"{d.get('wing', 'unknown')}/{d.get('room', 'unknown')}"
        rooms.setdefault(key, []).append(d)

    for room_key, room_drawers in rooms.items():
        active_states = {d.get("staleness_state") for d in room_drawers}
        if active_states and not active_states.intersection({"FRESH", "AGING"}):
            findings.append(Finding(
                severity="MEDIUM",
                kind="COVERAGE_GAP",
                subject=room_key,
                detail=f"Room {room_key} has no FRESH or AGING drawers "
                       f"(states present: {', '.join(sorted(active_states))})",
                action=f"Run MemorySearch to identify what needs documenting in {room_key}. "
                       f"Write at least one new drawer from a verified source.",
            ))

    # Sort: CRITICAL first, then HIGH, then MEDIUM
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
    findings.sort(key=lambda f: order.get(f.severity, 99))
    return findings


# ── Output builders ───────────────────────────────────────────────────────────

def build_staleness_map(drawers: list[dict], run_ts: str) -> str:
    lines: list[str] = [
        "# Staleness Map",
        "",
        f"> Generated: {run_ts}",
        f"> Drawers: {len(drawers)}",
        "",
        "Sorted by state (worst first), then confidence ascending.",
        "",
        "| Drawer ID | Topic | Wing/Room | State | Confidence | Written At |",
        "|---|---|---|---|---|---|",
    ]

    sorted_drawers = sorted(
        drawers,
        key=lambda d: (
            STATE_ORDER.index(d.get("staleness_state", "FRESH"))
            if d.get("staleness_state", "FRESH") in STATE_ORDER else 99,
            d.get("new_confidence", d.get("confidence", 1.0)),
        ),
    )

    for d in sorted_drawers:
        state = d.get("staleness_state", "FRESH")
        conf = d.get("new_confidence", d.get("confidence", 1.0))
        conf_delta = d.get("conf_delta", 0.0)
        delta_str = f" ({conf_delta:+.4f})" if conf_delta != 0.0 else ""
        lines.append(
            f"| {d.get('id', '-')} "
            f"| {d.get('topic', '-')} "
            f"| {d.get('wing', '-')}/{d.get('room', '-')} "
            f"| {state} "
            f"| {conf:.4f}{delta_str} "
            f"| {d.get('written_at', '-')} |"
        )

    # Summary
    state_counts: dict[str, int] = {}
    for d in drawers:
        state_counts[d.get("staleness_state", "FRESH")] = (
            state_counts.get(d.get("staleness_state", "FRESH"), 0) + 1
        )

    lines += [
        "",
        "## Summary",
        "",
    ]
    for state in STATE_ORDER:
        count = state_counts.get(state, 0)
        if count:
            lines.append(f"- {state}: {count}")

    return "\n".join(lines) + "\n"


def build_gap_map(findings: list[Finding], drawers: list[dict], run_ts: str) -> str:
    lines: list[str] = [
        "# Gap Map",
        "",
        f"> Generated: {run_ts}",
        f"> Drawers scanned: {len(drawers)}",
        f"> Findings: {len(findings)}",
        "",
    ]

    if not findings:
        lines += [
            "No actionable findings. All drawers within confidence bounds.",
            "",
            "Next step: run again after more wave executions accumulate receipts.",
        ]
        return "\n".join(lines) + "\n"

    critical = [f for f in findings if f.severity == "CRITICAL"]
    high = [f for f in findings if f.severity == "HIGH"]
    medium = [f for f in findings if f.severity == "MEDIUM"]

    def write_section(severity: str, items: list[Finding]) -> None:
        if not items:
            return
        lines.append(f"## {severity} ({len(items)})")
        lines.append("")
        for i, f in enumerate(items, 1):
            lines.append(f"### {i}. [{f.kind}] {f.subject}")
            lines.append("")
            lines.append(f"**Finding:** {f.detail}")
            lines.append("")
            lines.append(f"**Action:** {f.action}")
            lines.append("")

    write_section("CRITICAL", critical)
    write_section("HIGH", high)
    write_section("MEDIUM", medium)

    lines += [
        "---",
        "",
        "## How to close a finding",
        "",
        "1. Pick highest-severity finding.",
        "2. Follow the Action instruction.",
        "3. After updating the drawer, run `staleness-checker.py` to confirm state.",
        "4. Re-run `dream.py` to verify this finding no longer appears.",
        "5. Record the closure in the drawer's provenance log.",
    ]

    return "\n".join(lines) + "\n"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Dream — EMA decay and gap detection")
    parser.add_argument("--dry-run", action="store_true", help="Compute without writing files")
    parser.add_argument("--background", action="store_true", help="Passed by hook runner; no-op")
    args = parser.parse_args()

    try:
        ws_root = find_ws_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    memory_root = ws_root / "memory"
    wings_root = memory_root / "wings"
    index_path = memory_root / "index.json"
    dream_log_path = memory_root / "dream-log.json"
    gap_map_path = memory_root / "gap-map.md"
    staleness_map_path = memory_root / "staleness-map.md"

    if not wings_root.exists():
        print("No wings directory found — no drawers to process.")
        sys.exit(0)

    # Load index
    index = load_json(index_path)
    if not isinstance(index, dict):
        index = {"drawers": []}

    run_ts = datetime.now(timezone.utc).isoformat()

    # Load all drawer files and apply EMA
    drawer_paths = list(wings_root.rglob("*.json"))
    enriched: list[dict] = []
    ema_updates: list[dict] = []
    errors: list[str] = []

    for drawer_path in drawer_paths:
        drawer = load_json(drawer_path)
        if not isinstance(drawer, dict):
            errors.append(f"parse error: {drawer_path}")
            continue

        state = drawer.get("staleness_state", "FRESH")
        old_conf = float(drawer.get("confidence", 1.0))
        new_conf = apply_ema(old_conf, state)
        delta = round(new_conf - old_conf, 4)

        enriched_drawer = dict(drawer)
        enriched_drawer["new_confidence"] = new_conf
        enriched_drawer["conf_delta"] = delta
        enriched.append(enriched_drawer)

        if delta != 0.0:
            ema_updates.append({
                "drawer_id": drawer.get("id", drawer_path.name),
                "old_confidence": old_conf,
                "new_confidence": new_conf,
                "delta": delta,
                "state": state,
            })

        # Write EMA result back to drawer and index unless dry-run
        if not args.dry_run and delta != 0.0:
            drawer["confidence"] = new_conf
            drawer.setdefault("provenance", []).append({
                "event": "EMA_DECAY",
                "timestamp": run_ts,
                "actor": "dream",
                "from_confidence": old_conf,
                "to_confidence": new_conf,
                "staleness_state": state,
            })
            try:
                save_json(drawer_path, drawer)
            except OSError as exc:
                errors.append(f"write error {drawer_path}: {exc}")
                continue

            for entry in index.get("drawers", []):
                if entry.get("id") == drawer.get("id"):
                    entry["confidence"] = new_conf
                    break

    if not args.dry_run and ema_updates:
        try:
            save_json(index_path, index)
        except OSError as exc:
            errors.append(f"write error {index_path}: {exc}")

    # Sync EMA-updated confidence values back to ChromaDB
    # so MemorySearch scoring stays in sync with dream.py decay.
    chromadb_synced = 0
    if not args.dry_run and ema_updates:
        store_path = memory_path() if memory_path else ""
        chroma_db = ws_root / "memory" / "chroma.sqlite3"
        if store_path and chroma_db.exists() and get_collection is not None:
            try:
                col = get_collection()
                for u in ema_updates:
                    drawer_id = u["drawer_id"]
                    # Look up the ChromaDB doc by wabblespec_drawer_id metadata field
                    r = col.get(where={"wabblespec_drawer_id": drawer_id})
                    ids = r.ids if hasattr(r, "ids") else r.get("ids", [])
                    if ids:
                        col.update(
                            ids=[ids[0]],
                            metadatas=[{"wabblespec_confidence": u["new_confidence"]}],
                        )
                        chromadb_synced += 1
            except Exception as exc:
                errors.append(f"chromadb sync error: {exc}")

    # Detect gaps
    findings = detect_gaps(enriched)

    # Build outputs
    staleness_map_content = build_staleness_map(enriched, run_ts)
    gap_map_content = build_gap_map(findings, enriched, run_ts)

    if not args.dry_run:
        try:
            save_text(staleness_map_path, staleness_map_content)
            save_text(gap_map_path, gap_map_content)
        except OSError as exc:
            print(f"ERROR writing output files: {exc}", file=sys.stderr)
            sys.exit(1)

    # Update dream log
    dream_log = load_json(dream_log_path)
    if not isinstance(dream_log, dict):
        dream_log = {"version": "1.0", "runs": []}

    run_number = len(dream_log["runs"]) + 1
    run_record = {
        "run_id": f"dream-run-{run_number:03d}",
        "timestamp": run_ts,
        "dry_run": args.dry_run,
        "drawers_processed": len(enriched),
        "ema_updates": len(ema_updates),
        "gap_findings": len(findings),
        "findings_by_severity": {
            "CRITICAL": sum(1 for f in findings if f.severity == "CRITICAL"),
            "HIGH": sum(1 for f in findings if f.severity == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f.severity == "MEDIUM"),
        },
        "errors": len(errors),
    }
    dream_log["runs"].append(run_record)

    if not args.dry_run:
        try:
            save_json(dream_log_path, dream_log)
        except OSError as exc:
            errors.append(f"write error {dream_log_path}: {exc}")

    # Report
    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"dream {prefix}complete  (run #{run_number})")
    print(f"  drawers processed : {len(enriched)}")
    print(f"  EMA updates       : {len(ema_updates)}")
    print(f"  ChromaDB synced   : {chromadb_synced}")
    for u in ema_updates:
        print(f"    {u['drawer_id']}: {u['old_confidence']:.4f} -> {u['new_confidence']:.4f} "
              f"({u['delta']:+.4f})  [{u['state']}]")
    print(f"  gap findings      : {len(findings)}")
    for f in findings:
        print(f"    [{f.severity}] {f.kind} — {f.subject}")
    if not args.dry_run:
        print(f"  gap-map.md        : {gap_map_path}")
        print(f"  staleness-map.md  : {staleness_map_path}")
        print(f"  dream-log.json    : {dream_log_path}")
    if errors:
        print(f"  errors: {len(errors)}", file=sys.stderr)
        for e in errors:
            print(f"    {e}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
