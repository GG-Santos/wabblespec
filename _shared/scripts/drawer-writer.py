"""
drawer-writer.py — Schema-enforced writer for WabbleSpec memory drawers.

Replaces Claude reasoning about which fields a drawer JSON requires, constructing the
JSON, and issuing a Write tool call. Validates against _shared/schemas/drawer.schema.json
field set. Supports create, update, and validate operations.

Usage:
    # Create a new drawer (auto-determines output path from --out or wing/room/id):
    python _shared/scripts/drawer-writer.py \\
        --id arch-layer-overview-20260526 \\
        --topic "WabbleSpec layer architecture overview" \\
        --wing architecture \\
        --room layer-architecture \\
        --confidence 0.9 \\
        --source "_shared/references/invariants.md" \\
        --source-module memory \\
        --evidence "L0 handles session intake. L1 covers spec and planning..." \\
        --note "Session seed-run-20260526aa"

    # Specify exact output path:
    python _shared/scripts/drawer-writer.py ... \\
        --out .wabblespec/memory/wings/architecture/rooms/layer-architecture/drawers/arch-layer-overview-20260526.json

    # Dry run — print JSON without writing:
    python _shared/scripts/drawer-writer.py ... --dry-run

    # Update fields on an existing drawer (adds an UPDATED provenance event):
    python _shared/scripts/drawer-writer.py \\
        --update .wabblespec/memory/wings/architecture/rooms/layer-architecture/drawers/arch-layer-overview-20260526.json \\
        --confidence 0.95 \\
        --staleness-state FRESH \\
        --note "Re-verified 2026-05-26"

    # Mark a drawer superseded:
    python _shared/scripts/drawer-writer.py \\
        --update path/to/old-drawer.json \\
        --staleness-state SUPERSEDED \\
        --superseded-by new-drawer-20260526 \\
        --note "Replaced by new-drawer-20260526"

    # Validate an existing drawer against schema field requirements:
    python _shared/scripts/drawer-writer.py --validate path/to/drawer.json

    # Show a drawer (human-readable summary):
    python _shared/scripts/drawer-writer.py --show path/to/drawer.json

Valid wings: architecture, implementation, decisions, operations
Valid staleness states: FRESH, AGING, STALE, EXPIRED, NEEDS_REVERIFICATION, SUPERSEDED

Output path derivation (when --out is omitted):
    .wabblespec/memory/wings/{wing}/rooms/{room}/drawers/{id}.json

Exit codes:
    0  success
    1  validation failure or bad arguments
    2  file not writable / directory missing
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_WINGS = ["architecture", "implementation", "decisions", "operations"]

VALID_STALENESS = [
    "FRESH", "AGING", "STALE", "EXPIRED", "NEEDS_REVERIFICATION", "SUPERSEDED"
]

REQUIRED_FIELDS = [
    "id", "topic", "wing", "room", "staleness_state",
    "written_at", "source", "source_module", "confidence", "evidence", "provenance"
]


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_wabblespec(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        ws = os.path.join(candidate, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def derive_output_path(ws, wing, room, drawer_id):
    return os.path.join(
        ws, "memory", "wings", wing, "rooms", room, "drawers",
        f"{drawer_id}.json"
    )


def write_json(path, data, dry_run=False):
    text = json.dumps(data, indent=2) + "\n"
    if dry_run:
        print(f"--- [DRY RUN] {path} ---")
        print(text)
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        print(f"ERROR: Cannot write {path}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Wrote {path}")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_drawer(data, path=None):
    errors = []
    loc = path or "drawer"

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Field type/enum checks
    ss = data.get("staleness_state")
    if ss and ss not in VALID_STALENESS:
        errors.append(f"staleness_state '{ss}' not in {VALID_STALENESS}")

    wing = data.get("wing")
    if wing and wing not in VALID_WINGS:
        errors.append(f"wing '{wing}' not in {VALID_WINGS}")

    conf = data.get("confidence")
    if conf is not None:
        if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
            errors.append(f"confidence must be 0.0–1.0, got: {conf}")

    if data.get("staleness_state") == "SUPERSEDED" and not data.get("superseded_by"):
        errors.append("staleness_state=SUPERSEDED requires superseded_by to be set")

    prov = data.get("provenance")
    if prov is not None:
        if not isinstance(prov, list):
            errors.append("provenance must be an array")
        else:
            for i, evt in enumerate(prov):
                for rf in ("event", "timestamp", "actor"):
                    if rf not in evt:
                        errors.append(f"provenance[{i}] missing required field: {rf}")

    return errors


# ---------------------------------------------------------------------------
# Build drawer dict
# ---------------------------------------------------------------------------

def build_drawer(args):
    ts = now_utc()

    drawer = {
        "id": args.id,
        "topic": args.topic,
        "wing": args.wing,
        "room": args.room,
        "staleness_state": args.staleness_state or "FRESH",
        "written_at": ts,
        "last_verified": ts,
        "expires_at": None,
        "source": args.source,
        "source_module": args.source_module,
        "confidence": args.confidence,
        "evidence": args.evidence,
        "superseded_by": None,
        "contradicts": None,
        "provenance": [
            {
                "event": "WRITTEN",
                "timestamp": ts,
                "actor": args.source_module,
                "note": args.note or "",
            }
        ],
    }

    return drawer


# ---------------------------------------------------------------------------
# Update drawer
# ---------------------------------------------------------------------------

def update_drawer(data, args):
    ts = now_utc()
    changed = []

    if args.confidence is not None:
        data["confidence"] = args.confidence
        changed.append(f"confidence={args.confidence}")

    if args.staleness_state:
        old_state = data.get("staleness_state")
        data["staleness_state"] = args.staleness_state
        changed.append(f"staleness_state: {old_state} -> {args.staleness_state}")

        if args.staleness_state == "FRESH":
            data["last_verified"] = ts

    if args.superseded_by:
        data["superseded_by"] = args.superseded_by
        changed.append(f"superseded_by={args.superseded_by}")

    if args.contradicts:
        data["contradicts"] = args.contradicts
        changed.append(f"contradicts={args.contradicts}")

    if args.evidence:
        data["evidence"] = args.evidence
        changed.append("evidence updated")

    if args.source:
        data["source"] = args.source
        changed.append(f"source={args.source}")

    if not changed and not args.note:
        print("WARNING: No fields to update. Pass at least one update flag.")
        sys.exit(1)

    # Determine provenance event type
    if args.staleness_state == "SUPERSEDED":
        event_type = "SUPERSEDED"
    elif args.staleness_state:
        event_type = "TRANSITION"
    else:
        event_type = "UPDATED"

    prov_entry = {
        "event": event_type,
        "timestamp": ts,
        "actor": args.actor or "memory",
        "note": args.note or (", ".join(changed)),
    }
    if event_type == "TRANSITION" and args.staleness_state:
        old_state = data.get("staleness_state")
        if old_state:
            prov_entry["from_state"] = old_state
        prov_entry["to_state"] = args.staleness_state

    if not isinstance(data.get("provenance"), list):
        data["provenance"] = []
    data["provenance"].append(prov_entry)

    return data, changed


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_create(args):
    # Validate required create-time args
    missing = []
    for field in ("id", "topic", "wing", "room", "source", "source_module", "evidence"):
        if not getattr(args, field.replace("-", "_"), None):
            missing.append(f"--{field}")
    if args.confidence is None:
        missing.append("--confidence")
    if missing:
        print(f"ERROR: Missing required arguments for create: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if args.wing not in VALID_WINGS:
        print(f"ERROR: --wing must be one of {VALID_WINGS}", file=sys.stderr)
        sys.exit(1)

    drawer = build_drawer(args)

    errors = validate_drawer(drawer)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    # Determine output path
    if args.out:
        out_path = args.out
    else:
        ws = find_wabblespec()
        if ws is None:
            print("ERROR: Cannot find .wabblespec/. Use --out to specify explicit path.", file=sys.stderr)
            sys.exit(2)
        out_path = derive_output_path(ws, args.wing, args.room, args.id)

    write_json(out_path, drawer, dry_run=args.dry_run)


def cmd_update(args):
    data = load_json(args.update)
    data, changed = update_drawer(data, args)

    errors = validate_drawer(data, path=args.update)
    if errors:
        print("Validation errors after update:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    write_json(args.update, data, dry_run=args.dry_run)
    if not args.dry_run:
        print(f"Updated fields: {', '.join(changed) if changed else '(note only)'}")


def cmd_validate(args):
    data = load_json(args.validate)
    errors = validate_drawer(data, path=args.validate)
    if errors:
        print(f"FAIL  {args.validate}")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"PASS  {args.validate}")
        print(f"  id: {data.get('id')}, wing: {data.get('wing')}, "
              f"staleness: {data.get('staleness_state')}, confidence: {data.get('confidence')}")


def cmd_show(args):
    data = load_json(args.show)
    print(f"id:             {data.get('id')}")
    print(f"topic:          {data.get('topic')}")
    print(f"wing/room:      {data.get('wing')} / {data.get('room')}")
    print(f"staleness:      {data.get('staleness_state')}")
    print(f"confidence:     {data.get('confidence')}")
    print(f"written_at:     {data.get('written_at')}")
    print(f"last_verified:  {data.get('last_verified')}")
    print(f"source:         {data.get('source')}")
    print(f"source_module:  {data.get('source_module')}")
    sup = data.get("superseded_by")
    if sup:
        print(f"superseded_by:  {sup}")
    prov = data.get("provenance", [])
    print(f"provenance:     {len(prov)} event(s)")
    for evt in prov:
        print(f"  {evt.get('timestamp')}  {evt.get('event')}  {evt.get('note', '')}")
    print()
    evidence = data.get("evidence", "")
    print(f"evidence ({len(evidence)} chars):")
    print(f"  {evidence[:200]}{'...' if len(evidence) > 200 else ''}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Schema-enforced writer for WabbleSpec memory drawers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Operation selectors (mutually exclusive)
    op = parser.add_mutually_exclusive_group(required=True)
    op.add_argument("--id", metavar="ID",
                    help="Create a new drawer with this ID.")
    op.add_argument("--update", metavar="PATH",
                    help="Update an existing drawer at PATH.")
    op.add_argument("--validate", metavar="PATH",
                    help="Validate an existing drawer at PATH.")
    op.add_argument("--show", metavar="PATH",
                    help="Show human-readable summary of an existing drawer.")

    # Create-time fields
    parser.add_argument("--topic", metavar="TEXT")
    parser.add_argument("--wing", metavar="WING", choices=VALID_WINGS)
    parser.add_argument("--room", metavar="ROOM")
    parser.add_argument("--source", metavar="PATH_OR_STRING",
                        help="Source path or reference string.")
    parser.add_argument("--source-module", metavar="MODULE_ID", dest="source_module")
    parser.add_argument("--evidence", metavar="TEXT",
                        help="Evidence content string.")
    parser.add_argument("--confidence", type=float, metavar="0.0-1.0")
    parser.add_argument("--staleness-state", metavar="STATE", dest="staleness_state",
                        choices=VALID_STALENESS,
                        help="Staleness state (default: FRESH for new drawers).")

    # Update-specific fields
    parser.add_argument("--superseded-by", metavar="DRAWER_ID", dest="superseded_by")
    parser.add_argument("--contradicts", metavar="DRAWER_ID")
    parser.add_argument("--actor", metavar="MODULE_ID",
                        help="Module recording the update (default: memory).")
    parser.add_argument("--note", metavar="TEXT",
                        help="Provenance note for the event.")

    # Output / mode
    parser.add_argument("--out", metavar="PATH",
                        help="Explicit output path (create mode; auto-derived if omitted).")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.validate:
        cmd_validate(args)
    elif args.show:
        cmd_show(args)
    elif args.update:
        cmd_update(args)
    else:
        cmd_create(args)

    sys.exit(0)


if __name__ == "__main__":
    main()
