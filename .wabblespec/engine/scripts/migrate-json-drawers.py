"""
migrate-json-drawers.py

One-time migration: reads all JSON drawers from
.wabblespec/memory/wings/{wing}/rooms/{room}/drawers/{id}.json
and upserts them into ChromaDB with WabbleSpec metadata fields preserved.

Also creates synthetic preference-pattern pointer documents for drawers
in the decisions wing to bridge vocabulary gaps during semantic search.

Run once after the WabbleSpec Memory store is initialized:
    python scripts/migrate-json-drawers.py

Safe to re-run: upsert is idempotent.
"""

import json
import re
import sys
from pathlib import Path


# Minimal primer: find repo root and add to sys.path so _shared is importable.
def _primer() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".wabblespec").exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return parent
    raise RuntimeError(f"Cannot find WabbleSpec repo root above {here}")


_primer()


def _require_backend():
    """Import the memory backend, with a clear error if not installed."""
    try:
        from _shared.memory_backend import get_collection, memory_path  # noqa: PLC0415
        return get_collection, memory_path
    except ModuleNotFoundError as exc:
        print(
            f"ERROR: WabbleSpec Memory backend not available ({exc}).\n"
            "Install with: python -m pip install -e packages/memory",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc


# ── Preference patterns for decisions wing ─────────────────────────────────
# Architectural-decision vocabulary that bridges query/drawer vocabulary gaps.
_DECISION_PATTERNS = [
    re.compile(r"decided\s+(?:that|to|over)\s+(.{10,80})", re.I),
    re.compile(r"chosen\s+because\s+(.{10,80})", re.I),
    re.compile(r"the\s+rationale\s+(?:was|is)\s+(.{10,80})", re.I),
    re.compile(r"the\s+alternative\s+was\s+(.{10,80})", re.I),
    re.compile(r"invariant:\s*(.{5,80})", re.I),
    re.compile(r"gate:\s*(.{5,80})", re.I),
    re.compile(r"blocked\s+by\s+(.{5,80})", re.I),
    re.compile(r"cascade\s+triggers\s+(.{5,80})", re.I),
    re.compile(r"\bBREAKING\b.{0,60}", re.I),
    re.compile(r"\bADDITIVE\b.{0,60}", re.I),
    re.compile(r"SUPERSEDED\s+by\s+(.{5,80})", re.I),
    re.compile(r"depends_on\s+(.{5,60})", re.I),
]


def _extract_decision_phrases(text: str) -> list[str]:
    phrases = []
    for pattern in _DECISION_PATTERNS:
        for match in pattern.findall(text):
            phrase = match.strip().rstrip(".,;")
            if phrase:
                phrases.append(phrase)
    return phrases[:8]  # cap at 8 phrases per drawer


def migrate():
    get_collection, memory_path = _require_backend()

    memory_root = Path(memory_path())
    wings_root = memory_root / "wings"

    if not wings_root.exists():
        print(f"ERROR: wings directory not found at {wings_root}")
        sys.exit(1)

    col = get_collection()

    # Collect all drawer JSON files
    drawer_files = sorted(wings_root.rglob("drawers/*.json"))
    print(f"Found {len(drawer_files)} drawer files to migrate.")

    migrated = 0
    skipped = 0
    synthetic_added = 0

    for drawer_file in drawer_files:
        with open(drawer_file, "r", encoding="utf-8") as f:
            try:
                d = json.load(f)
            except json.JSONDecodeError as e:
                print(f"  SKIP (JSON error): {drawer_file.name} -- {e}")
                skipped += 1
                continue

        drawer_id = d.get("id")
        evidence = d.get("evidence", "")
        if not drawer_id or not evidence:
            print(f"  SKIP (missing id or evidence): {drawer_file.name}")
            skipped += 1
            continue

        # Build ChromaDB metadata. All WabbleSpec fields prefixed wabblespec_.
        metadata = {
            "wing": d.get("wing", ""),
            "room": d.get("room", ""),
            "date": (d.get("written_at") or "")[:10],
            "source_file": d.get("source", str(drawer_file.relative_to(memory_root))),
            "filed_at": d.get("written_at", ""),
            "wabblespec_staleness_state": d.get("staleness_state", "FRESH"),
            "wabblespec_confidence": float(d.get("confidence", 1.0)),
            "wabblespec_expires_at": d.get("expires_at") or "",
            "wabblespec_source_module": d.get("source_module", ""),
            "wabblespec_schema_version": 1,
            "wabblespec_superseded_by": d.get("superseded_by") or "",
            "wabblespec_topic": d.get("topic", ""),
            "wabblespec_drawer_id": drawer_id,
        }

        # Upsert main drawer document
        col.upsert(
            ids=[drawer_id],
            documents=[evidence],
            metadatas=[metadata],
        )
        migrated += 1
        print(f"  OK: {drawer_id} ({metadata['wing']}/{metadata['room']})")

        # Synthetic preference-pattern documents for decisions wing
        if d.get("wing") == "decisions":
            phrases = _extract_decision_phrases(evidence)
            if phrases:
                synth_id = f"{drawer_id}__synth_decision"
                synth_doc = "WabbleSpec decision: " + "; ".join(phrases)
                synth_meta = {**metadata, "wabblespec_synthetic": "decision_pattern"}
                col.upsert(
                    ids=[synth_id],
                    documents=[synth_doc],
                    metadatas=[synth_meta],
                )
                synthetic_added += 1
                print(f"    + synthetic: {len(phrases)} decision phrase(s)")

    print(
        f"\nMigration complete: {migrated} drawers upserted, "
        f"{synthetic_added} synthetic docs added, {skipped} skipped."
    )
    print(f"Total ChromaDB documents: {col.count()}")


if __name__ == "__main__":
    migrate()
