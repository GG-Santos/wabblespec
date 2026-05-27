#!/usr/bin/env python3
"""
WabbleSpec MemoryMine — deep pattern mining across the memory store.

Runs offline only — never during active execution.
PID-locked to prevent concurrent runs.
Schema-version-aware — flags drawers with mismatched version as NEEDS_REBUILD.

Produces four analysis files in .wabblespec/state/memory/mine/:
  gap-map.md
  mine-clusters.md
  pattern-summary.md
  staleness-map.md
  mine-receipt-{timestamp}.json

Usage:
  python modules/l5/memory-mine/scripts/memory-mine.py
  python modules/l5/memory-mine/scripts/memory-mine.py --dry-run
  python modules/l5/memory-mine/scripts/memory-mine.py --min-drawers 0  # override gate for testing

Exit 0 = success. Exit 1 = error or gate not met.
"""

import argparse
import atexit
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

for p in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents, Path.cwd(), *Path.cwd().parents]:
    if (p / ".wabblespec").is_dir():
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
        break

from _shared.memory_backend import get_collection, memory_path

# Must match modules/l5/memory/rules/schema-version.md
CURRENT_SCHEMA_VERSION = 1

# Minimum drawer count before analysis is meaningful
MIN_DRAWERS_DEFAULT = 50

# Stale lock timeout in hours
LOCK_TIMEOUT_HOURS = 24

STALENESS_RANK = {
    "FRESH": 5,
    "AGING": 4,
    "STALE": 3,
    "NEEDS_REVERIFICATION": 2,
    "NEEDS_REBUILD": 1,
    "EXPIRED": 0,
    "SUPERSEDED": -1,
}


# ---------------------------------------------------------------------------
# Environment and path setup
# ---------------------------------------------------------------------------

def find_memory_path() -> Path:
    env_path = memory_path()
    if env_path:
        return Path(env_path)
    raise EnvironmentError(
        "WABBLESPEC_MEMORY_PATH not set and no .wabblespec directory found. "
        "Import _shared.memory_backend or run scripts/memory-bootstrap.py first."
    )


def find_wabblespec_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / ".wabblespec").is_dir():
            return p / ".wabblespec"
    raise FileNotFoundError("No .wabblespec directory found.")


# ---------------------------------------------------------------------------
# PID lock
# ---------------------------------------------------------------------------

_LOCK_FILE: Optional[Path] = None


def acquire_lock(palace_path: Path) -> None:
    global _LOCK_FILE
    lock = palace_path / ".mine.pid"
    _LOCK_FILE = lock

    if lock.exists():
        try:
            data = json.loads(lock.read_text())
            pid = int(data.get("pid", 0))
            started = datetime.fromisoformat(data.get("started_at", "1970-01-01T00:00:00+00:00"))
            age_hours = (datetime.now(timezone.utc) - started).total_seconds() / 3600
            if age_hours < LOCK_TIMEOUT_HOURS:
                try:
                    os.kill(pid, 0)  # check process exists
                    print(json.dumps({"error": f"MemoryMine already running (PID {pid}). Abort."}))
                    sys.exit(1)
                except (ProcessLookupError, PermissionError):
                    pass  # process dead — stale lock, proceed
            # Stale lock — remove and proceed
        except (json.JSONDecodeError, ValueError, OSError):
            pass
        lock.unlink(missing_ok=True)

    lock.write_text(json.dumps({
        "pid": os.getpid(),
        "started_at": datetime.now(timezone.utc).isoformat()
    }))
    atexit.register(lambda: lock.unlink(missing_ok=True))


# ---------------------------------------------------------------------------
# Drawer loading via WabbleSpec Memory
# ---------------------------------------------------------------------------

def _normalize_drawer(doc_id: str, meta: dict, doc_text: str) -> dict:
    """Convert a ChromaDB (id, metadata, document) row to the drawer shape
    expected by downstream analyses."""
    return {
        "id": meta.get("wabblespec_drawer_id", doc_id),
        "content": doc_text,
        "document": doc_text,
        "metadata": meta,
        # Convenience aliases used by the analyses
        "wing": meta.get("wing", ""),
        "room": meta.get("room", ""),
        "topic": meta.get("wabblespec_topic", meta.get("room", "")),
        "staleness_state": meta.get("wabblespec_staleness_state", "FRESH"),
        "confidence": float(meta.get("wabblespec_confidence", 1.0)),
        "superseded_by": meta.get("wabblespec_superseded_by"),
        "expires_at": meta.get("wabblespec_expires_at"),
    }


def load_all_drawers(palace_path: Path) -> list[dict]:
    col = get_collection()
    total = col.count()
    if total == 0:
        return []

    # Fetch in batches to avoid memory issues with large collections
    batch = 2000
    drawers: list[dict] = []
    offset = 0
    while offset < total:
        r = col.get(limit=batch, offset=offset)
        ids = r.ids if hasattr(r, "ids") else r.get("ids", [])
        metas = r.metadatas if hasattr(r, "metadatas") else r.get("metadatas", [])
        docs = r.documents if hasattr(r, "documents") else r.get("documents", [])
        for i, doc_id in enumerate(ids):
            meta = metas[i] if i < len(metas) else {}
            doc_text = docs[i] if i < len(docs) else ""
            drawers.append(_normalize_drawer(doc_id, meta, doc_text))
        offset += len(ids)
        if len(ids) < batch:
            break

    return drawers


# ---------------------------------------------------------------------------
# Schema version check
# ---------------------------------------------------------------------------

def classify_drawers(drawers: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return (valid, needs_rebuild) based on wabblespec_schema_version metadata."""
    valid, needs_rebuild = [], []
    for d in drawers:
        # Metadata may be flat (normalized) or nested — handle both
        meta = d.get("metadata", d)
        ver = meta.get("wabblespec_schema_version", 0)
        try:
            ver = int(ver)
        except (TypeError, ValueError):
            ver = 0
        if ver < CURRENT_SCHEMA_VERSION:
            needs_rebuild.append(d)
        else:
            valid.append(d)
    return valid, needs_rebuild


# ---------------------------------------------------------------------------
# Analysis 1: Gap detection
# ---------------------------------------------------------------------------

def detect_gaps(valid_drawers: list[dict], all_receipts_path: Path) -> list[dict]:
    """
    Gap types:
      REFERENCED_BUT_ABSENT — topic cited by 3+ drawers, no authoritative drawer
      LOW_CONFIDENCE_ANCHOR — topic has drawer but confidence < 0.5, high citation count
      RECEIPT_ONLY          — appears in receipts, never written to memory
    """
    gaps = []
    topic_citations: dict[str, int] = defaultdict(int)
    topic_confidence: dict[str, float] = {}
    known_topics: set[str] = set()

    for d in valid_drawers:
        meta = d.get("metadata", {})
        content = d.get("content", d.get("document", ""))
        topic = meta.get("topic", meta.get("room", ""))
        confidence = float(meta.get("wabblespec_confidence", meta.get("confidence", 0.5)))

        if topic:
            known_topics.add(topic.lower())
            topic_confidence[topic.lower()] = confidence

        # Count cross-references in content
        for other in valid_drawers:
            other_topic = other.get("metadata", {}).get("topic", "").lower()
            if other_topic and other_topic != topic.lower() and other_topic in content.lower():
                topic_citations[other_topic] += 1

    # REFERENCED_BUT_ABSENT
    for cited_topic, count in topic_citations.items():
        if count >= 3 and cited_topic not in known_topics:
            gaps.append({
                "type": "REFERENCED_BUT_ABSENT",
                "topic": cited_topic,
                "citation_count": count,
                "recommendation": f"Create a drawer for '{cited_topic}' — referenced {count}x but no authoritative drawer exists."
            })

    # LOW_CONFIDENCE_ANCHOR
    for topic, confidence in topic_confidence.items():
        if confidence < 0.5 and topic_citations.get(topic, 0) >= 3:
            gaps.append({
                "type": "LOW_CONFIDENCE_ANCHOR",
                "topic": topic,
                "confidence": confidence,
                "citation_count": topic_citations.get(topic, 0),
                "recommendation": f"Drawer for '{topic}' has confidence {confidence:.2f} but is cited {topic_citations.get(topic, 0)}x. Re-verify and update."
            })

    # RECEIPT_ONLY — topics in receipt files not in memory
    if all_receipts_path.exists():
        receipt_topics: set[str] = set()
        for rp in all_receipts_path.glob("*.json"):
            try:
                r = json.loads(rp.read_text())
                if isinstance(r, dict):
                    for field in ["topic", "module", "evidence"]:
                        val = r.get(field, "")
                        if isinstance(val, str) and len(val) > 3:
                            receipt_topics.add(val.lower())
                        elif isinstance(val, list):
                            for v in val:
                                if isinstance(v, str) and len(v) > 3:
                                    receipt_topics.add(v.lower())
            except (json.JSONDecodeError, OSError):
                continue

        for rt in receipt_topics:
            if rt not in known_topics and len(rt) > 5:
                gaps.append({
                    "type": "RECEIPT_ONLY",
                    "topic": rt,
                    "recommendation": f"'{rt}' appears in receipts but has no memory drawer. Consider writing evidence drawer."
                })

    return gaps


# ---------------------------------------------------------------------------
# Analysis 2: Cluster detection
# ---------------------------------------------------------------------------

def detect_clusters(valid_drawers: list[dict]) -> list[dict]:
    """
    Cluster: 3+ drawers sharing same wing + overlapping topic keywords.
    """
    wing_groups: dict[str, list[dict]] = defaultdict(list)
    for d in valid_drawers:
        meta = d.get("metadata", {})
        wing = meta.get("wing", "unknown")
        wing_groups[wing].append(d)

    clusters = []
    for wing, group in wing_groups.items():
        if len(group) < 3:
            continue

        # Simple keyword overlap clustering
        processed: set[str] = set()
        for i, d in enumerate(group):
            if d.get("id") in processed:
                continue
            topic_i = d.get("metadata", {}).get("topic", "").lower()
            words_i = set(topic_i.split())
            cluster_members = [d]
            processed.add(d.get("id", ""))

            for j, other in enumerate(group):
                if i == j or other.get("id") in processed:
                    continue
                topic_j = other.get("metadata", {}).get("topic", "").lower()
                words_j = set(topic_j.split())
                overlap = words_i & words_j
                if len(overlap) >= 1 and len(words_i) > 0:
                    cluster_members.append(other)
                    processed.add(other.get("id", ""))

            if len(cluster_members) >= 3:
                # Find anchor: highest confidence + freshest
                anchor = max(
                    cluster_members,
                    key=lambda x: (
                        float(x.get("metadata", {}).get("wabblespec_confidence", 0.5)),
                        STALENESS_RANK.get(x.get("metadata", {}).get("wabblespec_staleness_state", "STALE"), 0)
                    )
                )
                topic_words = set()
                for m in cluster_members:
                    topic_words.update(m.get("metadata", {}).get("topic", "").lower().split())
                coherence = "HIGH" if len(cluster_members) >= 5 else ("MEDIUM" if len(cluster_members) >= 3 else "LOW")
                recommendation = "CONSOLIDATE" if coherence == "HIGH" else ("KEEP" if coherence == "MEDIUM" else "EXPAND")

                clusters.append({
                    "name": f"{wing}/{'+'.join(list(topic_words)[:3])}",
                    "wing": wing,
                    "anchor_drawer_id": anchor.get("id", ""),
                    "anchor_topic": anchor.get("metadata", {}).get("topic", ""),
                    "member_ids": [m.get("id", "") for m in cluster_members],
                    "member_count": len(cluster_members),
                    "coherence": coherence,
                    "recommendation": recommendation
                })

    return clusters


# ---------------------------------------------------------------------------
# Analysis 3: Pattern extraction
# ---------------------------------------------------------------------------

def extract_patterns(valid_drawers: list[dict]) -> list[dict]:
    """
    Find recurring structural patterns in drawer content.
    """
    patterns = []
    content_phrases: dict[str, list[str]] = defaultdict(list)

    # Collect recurring phrases across drawers
    SIGNAL_PHRASES = [
        "decided to", "decided not to", "because", "tradeoff", "constraint",
        "requirement", "always", "never", "must", "must not", "failed because",
        "works when", "breaks when", "error:", "exception:", "workaround:"
    ]

    for d in valid_drawers:
        content = d.get("content", d.get("document", "")).lower()
        drawer_id = d.get("id", "")
        for phrase in SIGNAL_PHRASES:
            if phrase in content:
                content_phrases[phrase].append(drawer_id)

    # Patterns: phrase appearing in 3+ drawers
    for phrase, drawer_ids in content_phrases.items():
        if len(drawer_ids) >= 3:
            if phrase in ("decided to", "decided not to", "tradeoff"):
                ptype = "DECISION_RATIONALE"
                recommendation = "Consider creating a policy drawer consolidating decision rationale."
            elif phrase in ("always", "never", "must", "must not", "constraint", "requirement"):
                ptype = "RECURRING_CONSTRAINT"
                recommendation = "Consider creating a constraints index drawer."
            elif phrase in ("failed because", "breaks when", "error:", "exception:", "workaround:"):
                ptype = "FAILURE_MODE"
                recommendation = "Consider creating a failure-mode library drawer."
            else:
                ptype = "RECURRING_SIGNAL"
                recommendation = "Recurring signal — review for consolidation opportunity."

            patterns.append({
                "pattern": phrase,
                "type": ptype,
                "evidence_drawer_ids": list(set(drawer_ids)),
                "recurrence": len(set(drawer_ids)),
                "recommendation": recommendation
            })

    return patterns


# ---------------------------------------------------------------------------
# Analysis 4: Staleness map
# ---------------------------------------------------------------------------

def build_staleness_map(all_drawers: list[dict], needs_rebuild: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    state_counts: dict[str, int] = defaultdict(int)
    wing_stale: dict[str, int] = defaultdict(int)
    approaching: list[dict] = []
    schema_versions: dict[int, int] = defaultdict(int)

    for d in all_drawers:
        meta = d.get("metadata", {})
        state = meta.get("wabblespec_staleness_state", "UNKNOWN")
        state_counts[state] += 1
        wing = meta.get("wing", "unknown")

        if state in ("STALE", "EXPIRED", "NEEDS_REVERIFICATION"):
            wing_stale[wing] += 1

        # Schema version breakdown
        ver = int(meta.get("wabblespec_schema_version", 0))
        schema_versions[ver] += 1

        # Approaching staleness (expires_at within 7 days)
        expires_at = meta.get("wabblespec_expires_at")
        if expires_at and state == "FRESH":
            try:
                exp_dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                days_left = (exp_dt - now).days
                if 0 < days_left <= 7:
                    approaching.append({
                        "drawer_id": d.get("id", ""),
                        "topic": meta.get("topic", ""),
                        "expires_in_days": days_left
                    })
            except ValueError:
                pass

    # Add NEEDS_REBUILD
    state_counts["NEEDS_REBUILD"] = len(needs_rebuild)
    for d in needs_rebuild:
        wing_stale[d.get("metadata", {}).get("wing", "unknown")] += 1

    # Top stale wings
    top_stale_wings = sorted(wing_stale.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_drawers": len(all_drawers),
        "state_distribution": dict(state_counts),
        "approaching_staleness": approaching,
        "top_stale_wings": [{"wing": w, "stale_count": c} for w, c in top_stale_wings],
        "schema_version_distribution": {str(k): v for k, v in schema_versions.items()},
        "needs_rebuild_count": len(needs_rebuild)
    }


# ---------------------------------------------------------------------------
# Analysis 5: Deduplication
# ---------------------------------------------------------------------------

def detect_dedup_candidates(palace_path: Path, valid_drawers: list[dict]) -> list[dict]:
    """For each drawer, query ChromaDB for near-duplicates (similarity > 0.95).

    Returns list of candidate pairs for manual review.
    Only checks curated drawers (non-wing_sessions, non-synthetic).
    """
    col = get_collection()
    candidates = []
    seen_pairs: set[frozenset] = set()

    # Only check curated drawers (wing_sessions volume is too large and lower quality)
    curated = [
        d for d in valid_drawers
        if d.get("wing", "") not in ("wing_sessions",)
        and not d.get("id", "").startswith("drawer_wing_sessions")
        and "__synth_" not in d.get("id", "")
    ]

    for d in curated:
        drawer_id = d.get("id", "")
        content = d.get("content", "")[:200].strip()
        if not content:
            continue

        try:
            qr = col.query(query_texts=[content], n_results=4)
            ids = qr.ids[0] if qr.ids else []
            metas = qr.metadatas[0] if qr.metadatas else []
            distances = qr.distances[0] if qr.distances else []
        except Exception:
            continue

        for i, hit_id in enumerate(ids):
            if i >= len(distances):
                break
            hit_meta = metas[i] if i < len(metas) else {}
            hit_drawer_id = hit_meta.get("wabblespec_drawer_id", hit_id)

            # Skip self
            if hit_drawer_id == drawer_id:
                continue
            # Skip synthetic docs
            if "__synth_" in hit_id:
                continue

            similarity = max(0.0, 1.0 - distances[i])
            if similarity < 0.95:
                continue

            pair = frozenset([drawer_id, hit_drawer_id])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

            candidates.append({
                "drawer_a": drawer_id,
                "drawer_b": hit_drawer_id,
                "similarity": round(similarity, 4),
                "recommendation": "Review for consolidation — similarity >= 0.95",
            })

    return candidates


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_gap_map(mine_dir: Path, gaps: list[dict], ts: str) -> None:
    lines = [
        f"# Gap Map — {ts}",
        "",
        f"Total gaps found: {len(gaps)}",
        "",
    ]
    for gap_type in ["REFERENCED_BUT_ABSENT", "LOW_CONFIDENCE_ANCHOR", "RECEIPT_ONLY", "NEEDS_REBUILD"]:
        typed = [g for g in gaps if g.get("type") == gap_type]
        if typed:
            lines.append(f"## {gap_type} ({len(typed)})")
            lines.append("")
            for g in typed:
                lines.append(f"- **{g.get('topic', '')}**")
                if "citation_count" in g:
                    lines.append(f"  - Citations: {g['citation_count']}")
                if "confidence" in g:
                    lines.append(f"  - Confidence: {g['confidence']:.2f}")
                lines.append(f"  - {g.get('recommendation', '')}")
                lines.append("")
    if not gaps:
        lines.append("No gaps found. Memory store appears coherent.")
    mine_dir.joinpath("gap-map.md").write_text("\n".join(lines), encoding="utf-8")


def write_clusters(mine_dir: Path, clusters: list[dict], ts: str) -> None:
    lines = [
        f"# Mine Clusters — {ts}",
        "",
        f"Total clusters found: {len(clusters)}",
        "",
    ]
    for c in clusters:
        lines += [
            f"## Cluster: {c['name']}",
            f"- Wing: {c['wing']}",
            f"- Anchor drawer: {c['anchor_drawer_id']} ({c['anchor_topic']})",
            f"- Members: {', '.join(c['member_ids'])} ({c['member_count']} total)",
            f"- Coherence: {c['coherence']}",
            f"- Recommendation: {c['recommendation']}",
            "",
        ]
    if not clusters:
        lines.append("No clusters detected. Minimum 3 drawers per wing required for cluster analysis.")
    mine_dir.joinpath("mine-clusters.md").write_text("\n".join(lines), encoding="utf-8")


def write_patterns(mine_dir: Path, patterns: list[dict], ts: str) -> None:
    lines = [
        f"# Pattern Summary — {ts}",
        "",
        f"Total patterns found: {len(patterns)}",
        "",
    ]
    for p in patterns:
        lines += [
            f"## Pattern: {p['pattern']}",
            f"- Type: {p['type']}",
            f"- Evidence drawers: {', '.join(p['evidence_drawer_ids'])}",
            f"- Recurrence: {p['recurrence']}",
            f"- Recommendation: {p['recommendation']}",
            "",
        ]
    if not patterns:
        lines.append("No recurring patterns detected.")
    mine_dir.joinpath("pattern-summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_staleness_map(mine_dir: Path, smap: dict, ts: str) -> None:
    lines = [
        f"# Staleness Map — {ts}",
        "",
        f"Total drawers: {smap['total_drawers']}",
        "",
        "## State Distribution",
        "",
    ]
    for state, count in sorted(smap["state_distribution"].items()):
        lines.append(f"| {state} | {count} |")

    lines += [
        "",
        "## Schema Version Distribution",
        "",
    ]
    for ver, count in smap["schema_version_distribution"].items():
        marker = " (current)" if int(ver) == CURRENT_SCHEMA_VERSION else " (**NEEDS_REBUILD**)" if int(ver) < CURRENT_SCHEMA_VERSION else ""
        lines.append(f"| v{ver}{marker} | {count} |")

    if smap["approaching_staleness"]:
        lines += ["", "## Approaching Staleness (within 7 days)", ""]
        for a in smap["approaching_staleness"]:
            lines.append(f"- {a['drawer_id']} ({a['topic']}) — expires in {a['expires_in_days']} days")

    if smap["top_stale_wings"]:
        lines += ["", "## Top Stale Wings", ""]
        for w in smap["top_stale_wings"]:
            lines.append(f"- {w['wing']}: {w['stale_count']} stale/expired drawers")

    mine_dir.joinpath("staleness-map.md").write_text("\n".join(lines), encoding="utf-8")


def write_dedup_candidates(mine_dir: Path, candidates: list[dict], ts: str) -> None:
    lines = [
        f"# Dedup Candidates — {ts}",
        "",
        f"Near-duplicate pairs (similarity >= 0.95): {len(candidates)}",
        "",
    ]
    if candidates:
        lines += [
            "| Drawer A | Drawer B | Similarity | Action |",
            "|---|---|---|---|",
        ]
        for c in sorted(candidates, key=lambda x: -x["similarity"]):
            lines.append(
                f"| {c['drawer_a']} | {c['drawer_b']} "
                f"| {c['similarity']:.4f} | {c['recommendation']} |"
            )
    else:
        lines.append("No near-duplicate pairs found.")
    mine_dir.joinpath("dedup-candidates.md").write_text("\n".join(lines), encoding="utf-8")


def write_receipt(receipts_dir: Path, ts: str, stats: dict) -> Path:
    receipt_path = receipts_dir / f"mine-receipt-{ts.replace(':', '-').replace('+', '')}.json"
    receipt_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return receipt_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec MemoryMine")
    parser.add_argument("--dry-run", action="store_true", help="Print what would run without writing output files")
    parser.add_argument("--min-drawers", type=int, default=MIN_DRAWERS_DEFAULT,
                        help=f"Minimum drawer count gate (default {MIN_DRAWERS_DEFAULT})")
    args = parser.parse_args()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")

    try:
        palace_path = find_memory_path()
        ws_root = find_wabblespec_root()
    except (EnvironmentError, FileNotFoundError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    # PID lock
    acquire_lock(palace_path)

    # Load drawers
    all_drawers = load_all_drawers(palace_path)
    total = len(all_drawers)

    # Gate: minimum drawer count
    if total < args.min_drawers:
        print(json.dumps({
            "status": "GATE_NOT_MET",
            "message": f"Drawer count {total} < minimum {args.min_drawers}. Run after more drawers are written.",
            "drawers_found": total,
            "min_required": args.min_drawers
        }))
        sys.exit(1)

    # Schema classification
    valid_drawers, needs_rebuild = classify_drawers(all_drawers)

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "total_drawers": total,
            "valid_drawers": len(valid_drawers),
            "needs_rebuild": len(needs_rebuild),
            "schema_version_current": CURRENT_SCHEMA_VERSION,
            "would_write_to": str(ws_root / "memory" / "mine")
        }, indent=2))
        sys.exit(0)

    # Run analyses
    receipts_dir = ws_root / "state" / "receipts"
    gaps = detect_gaps(valid_drawers, receipts_dir)
    clusters = detect_clusters(valid_drawers)
    patterns = extract_patterns(valid_drawers)
    smap = build_staleness_map(all_drawers, needs_rebuild)
    dedup_candidates = detect_dedup_candidates(palace_path, valid_drawers)

    # Write output files
    mine_dir = palace_path / "mine"
    mine_dir.mkdir(parents=True, exist_ok=True)

    write_gap_map(mine_dir, gaps, ts)
    write_clusters(mine_dir, clusters, ts)
    write_patterns(mine_dir, patterns, ts)
    write_staleness_map(mine_dir, smap, ts)
    write_dedup_candidates(mine_dir, dedup_candidates, ts)

    # Write receipt
    stats = {
        "module": "memory-mine",
        "layer": "L5",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "schema_version_current": CURRENT_SCHEMA_VERSION,
        "drawers_analyzed": len(valid_drawers),
        "drawers_skipped_schema_mismatch": len(needs_rebuild),
        "gaps_found": len(gaps),
        "clusters_found": len(clusters),
        "patterns_found": len(patterns),
        "dedup_candidates_found": len(dedup_candidates),
        "staleness_critical": smap["state_distribution"].get("EXPIRED", 0)
            + smap["state_distribution"].get("NEEDS_REVERIFICATION", 0)
            + smap["needs_rebuild_count"],
        "output_dir": str(mine_dir),
        "dry_run": False
    }
    receipt_path = write_receipt(receipts_dir, ts, stats)

    print(json.dumps({
        "status": "COMPLETE",
        "drawers_analyzed": len(valid_drawers),
        "drawers_skipped": len(needs_rebuild),
        "gaps_found": len(gaps),
        "clusters_found": len(clusters),
        "patterns_found": len(patterns),
        "dedup_candidates": len(dedup_candidates),
        "output_dir": str(mine_dir),
        "receipt": str(receipt_path)
    }, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
