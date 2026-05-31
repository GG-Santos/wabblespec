"""
drawer-writer.py — Schema-enforced writer for WabbleSpec memory drawers.

Replaces Claude reasoning about which fields a drawer JSON requires, constructing the
JSON, and issuing a Write tool call. Validates against .wabblespec/engine/shared/schemas/drawer.schema.json
field set. Supports create, update, validate, show, list, and validate-all operations.

Usage:
    # Create — ID auto-derived from topic if --id omitted:
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --topic "WabbleSpec layer architecture overview" \\
        --wing architecture \\
        --room layer-architecture \\
        --confidence 0.9 \\
        --source ".wabblespec/engine/shared/references/invariants.md" \\
        --source-module memory \\
        --evidence "L0 handles session intake. L1 covers spec and planning..."
        # writes: layer-architecture-overview-20260531.json

    # Create with explicit ID:
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --id arch-layer-overview-20260526 \\
        --topic "WabbleSpec layer architecture overview" \\
        --wing architecture \\
        --room layer-architecture \\
        --confidence 0.9 \\
        --source ".wabblespec/engine/shared/references/invariants.md" \\
        --source-module memory \\
        --evidence "L0 handles session intake. L1 covers spec and planning..."

    # Create with evidence from file:
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --topic "Layer architecture overview" \\
        --wing architecture --room layer-architecture \\
        --confidence 0.9 --source "invariants.md" --source-module memory \\
        --evidence-file /tmp/evidence.txt

    # Specify exact output path:
    python .wabblespec/engine/shared/scripts/drawer-writer.py ... \\
        --out .wabblespec/state/memory/wings/architecture/rooms/layer-architecture/drawers/arch-layer-overview-20260526.json

    # Dry run — print JSON without writing:
    python .wabblespec/engine/shared/scripts/drawer-writer.py ... --dry-run

    # Update fields on an existing drawer (adds an UPDATED provenance event):
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --update .wabblespec/state/memory/wings/architecture/rooms/layer-architecture/drawers/arch-layer-overview-20260526.json \\
        --confidence 0.95 \\
        --staleness-state FRESH \\
        --note "Re-verified 2026-05-26"

    # Mark a drawer superseded:
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --update path/to/old-drawer.json \\
        --staleness-state SUPERSEDED \\
        --superseded-by new-drawer-20260526 \\
        --note "Replaced by new-drawer-20260526"

    # Validate an existing drawer:
    python .wabblespec/engine/shared/scripts/drawer-writer.py --validate path/to/drawer.json

    # Bulk validate — all drawers, or a specific wing:
    python .wabblespec/engine/shared/scripts/drawer-writer.py --validate-all
    python .wabblespec/engine/shared/scripts/drawer-writer.py --validate-all architecture

    # Show a drawer (human-readable summary):
    python .wabblespec/engine/shared/scripts/drawer-writer.py --show path/to/drawer.json

    # List wings / rooms / drawers:
    python .wabblespec/engine/shared/scripts/drawer-writer.py --list
    python .wabblespec/engine/shared/scripts/drawer-writer.py --list architecture
    python .wabblespec/engine/shared/scripts/drawer-writer.py --list architecture/layer-architecture

    # Bulk staleness transition — all drawers in a wing or room:
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --bulk-update architecture \\
        --staleness-state NEEDS_REVERIFICATION \\
        --note "Post-portability-migration sweep"

    # Bulk update with filters:
    python .wabblespec/engine/shared/scripts/drawer-writer.py \\
        --bulk-update architecture/memory \\
        --staleness-state STALE \\
        --current-state AGING \\
        --older-than 2026-01-01 \\
        --dry-run

Valid wings: architecture, implementation, decisions, operations, requirements, infrastructure, research, references, quality
Valid staleness states: FRESH, AGING, STALE, EXPIRED, NEEDS_REVERIFICATION, SUPERSEDED

Output path derivation (when --out is omitted):
    .wabblespec/state/memory/wings/{wing}/rooms/{room}/drawers/{id}.json

Exit codes:
    0  success
    1  validation failure or bad arguments
    2  file not writable / directory missing
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_WINGS = [
    "architecture", "implementation", "decisions", "operations",
    "requirements", "infrastructure", "research", "references", "quality",
]

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


def today_utc():
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def topic_to_slug(topic):
    slug = topic.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    if len(slug) > 40:
        truncated = slug[:40]
        last_hyphen = truncated.rfind('-')
        slug = truncated[:last_hyphen] if last_hyphen > 0 else truncated
    return slug


def derive_id(topic):
    return f"{topic_to_slug(topic)}-{today_utc()}"


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


def find_state_memory(ws):
    return os.path.join(ws, "state", "memory")


def derive_output_path(ws, wing, room, drawer_id):
    return os.path.join(
        find_state_memory(ws), "wings", wing, "rooms", room, "drawers",
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


def resolve_evidence(args):
    """Return evidence string from --evidence or --evidence-file."""
    if args.evidence_file:
        try:
            with open(args.evidence_file, encoding="utf-8") as f:
                return f.read().strip()
        except OSError as e:
            print(f"ERROR: Cannot read --evidence-file {args.evidence_file}: {e}", file=sys.stderr)
            sys.exit(1)
    return args.evidence


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_drawer(data, path=None):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

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

def build_drawer(args, evidence):
    ts = now_utc()
    drawer_id = args.id or derive_id(args.topic)

    drawer = {
        "id": drawer_id,
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
        "evidence": evidence,
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
    evidence = resolve_evidence(args)

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

    if evidence:
        data["evidence"] = evidence
        changed.append("evidence updated")

    if args.source:
        data["source"] = args.source
        changed.append(f"source={args.source}")

    if not changed and not args.note:
        print("WARNING: No fields to update. Pass at least one update flag.")
        sys.exit(1)

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
    missing = []
    for field in ("topic", "wing", "room", "source", "source_module"):
        if not getattr(args, field.replace("-", "_"), None):
            missing.append(f"--{field}")
    if args.confidence is None:
        missing.append("--confidence")
    evidence = resolve_evidence(args)
    if not evidence:
        missing.append("--evidence or --evidence-file")
    if missing:
        print(f"ERROR: Missing required arguments for create: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if args.wing not in VALID_WINGS:
        print(f"ERROR: --wing must be one of {VALID_WINGS}", file=sys.stderr)
        sys.exit(1)

    drawer = build_drawer(args, evidence)

    errors = validate_drawer(drawer)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    if args.out:
        out_path = args.out
    else:
        ws = find_wabblespec()
        if ws is None:
            print("ERROR: Cannot find .wabblespec/. Use --out to specify explicit path.", file=sys.stderr)
            sys.exit(2)
        out_path = derive_output_path(ws, args.wing, args.room, drawer["id"])

    if not args.id:
        print(f"Auto-derived ID: {drawer['id']}")

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


def cmd_validate_all(args):
    ws = find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/.", file=sys.stderr)
        sys.exit(2)

    mem_root = find_state_memory(ws)
    wings_root = os.path.join(mem_root, "wings")

    # Determine search root
    wing_filter = args.validate_all  # '' means all wings, 'architecture' means one wing
    if wing_filter:
        search_root = os.path.join(wings_root, wing_filter)
        if not os.path.isdir(search_root):
            print(f"ERROR: Wing not found: {search_root}", file=sys.stderr)
            sys.exit(1)
    else:
        search_root = wings_root

    drawer_files = []
    for dirpath, _, filenames in os.walk(search_root):
        if os.path.basename(dirpath) == "drawers":
            for fn in filenames:
                if fn.endswith(".json"):
                    drawer_files.append(os.path.join(dirpath, fn))

    if not drawer_files:
        print("No drawer files found.")
        return

    drawer_files.sort()
    passed = 0
    failed = 0
    fail_paths = []

    for path in drawer_files:
        try:
            data = json.loads(open(path, encoding="utf-8").read())
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR {path}: {e}")
            failed += 1
            fail_paths.append(path)
            continue
        errors = validate_drawer(data, path=path)
        if errors:
            print(f"FAIL  {path}")
            for e in errors:
                print(f"       {e}")
            failed += 1
            fail_paths.append(path)
        else:
            print(f"PASS  {path}")
            passed += 1

    print(f"\n{passed + failed} drawers checked — {passed} PASS, {failed} FAIL")
    if failed:
        sys.exit(1)


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


def cmd_list(args):
    ws = find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/.", file=sys.stderr)
        sys.exit(2)

    mem_root = find_state_memory(ws)
    wings_root = os.path.join(mem_root, "wings")

    # Parse list arg: '' → list wings; 'wing' → list rooms; 'wing/room' → list drawers
    list_arg = args.list or ''
    parts = [p for p in list_arg.split('/') if p]

    if len(parts) == 0:
        # List all wings
        if not os.path.isdir(wings_root):
            print("No wings found.")
            return
        wings = sorted(d for d in os.listdir(wings_root)
                       if os.path.isdir(os.path.join(wings_root, d)))
        if not wings:
            print("No wings found.")
            return
        print(f"Wings ({len(wings)}):")
        for w in wings:
            rooms_dir = os.path.join(wings_root, w, "rooms")
            room_count = 0
            drawer_count = 0
            if os.path.isdir(rooms_dir):
                for r in os.listdir(rooms_dir):
                    rpath = os.path.join(rooms_dir, r)
                    if os.path.isdir(rpath):
                        room_count += 1
                        dpath = os.path.join(rpath, "drawers")
                        if os.path.isdir(dpath):
                            drawer_count += sum(1 for f in os.listdir(dpath) if f.endswith(".json"))
            print(f"  {w}  ({room_count} rooms, {drawer_count} drawers)")

    elif len(parts) == 1:
        # List rooms in wing
        wing = parts[0]
        rooms_dir = os.path.join(wings_root, wing, "rooms")
        if not os.path.isdir(rooms_dir):
            print(f"Wing not found or has no rooms: {wing}")
            sys.exit(1)
        rooms = sorted(d for d in os.listdir(rooms_dir)
                       if os.path.isdir(os.path.join(rooms_dir, d)))
        if not rooms:
            print(f"No rooms in wing '{wing}'.")
            return
        print(f"{wing}  ({len(rooms)} rooms):")
        for r in rooms:
            dpath = os.path.join(rooms_dir, r, "drawers")
            count = 0
            if os.path.isdir(dpath):
                count = sum(1 for f in os.listdir(dpath) if f.endswith(".json"))
            print(f"  {r}  ({count} drawers)")

    else:
        # List drawers in wing/room
        wing, room = parts[0], parts[1]
        drawers_dir = os.path.join(wings_root, wing, "rooms", room, "drawers")
        if not os.path.isdir(drawers_dir):
            print(f"Room not found: {wing}/{room}")
            sys.exit(1)
        files = sorted(f for f in os.listdir(drawers_dir) if f.endswith(".json"))
        if not files:
            print(f"No drawers in {wing}/{room}.")
            return
        print(f"{wing}/{room}  ({len(files)} drawers):")
        for fn in files:
            path = os.path.join(drawers_dir, fn)
            try:
                data = json.loads(open(path, encoding="utf-8").read())
                staleness = data.get("staleness_state", "?")
                confidence = data.get("confidence", "?")
                topic = data.get("topic", "")
                print(f"  {fn[:-5]:<55}  {staleness:<22}  conf:{confidence}  {topic[:60]}")
            except Exception:
                print(f"  {fn[:-5]}  (unreadable)")


# ---------------------------------------------------------------------------
# Bulk update
# ---------------------------------------------------------------------------

def cmd_bulk_update(args):
    if not args.staleness_state:
        print("ERROR: --bulk-update requires --staleness-state", file=sys.stderr)
        sys.exit(1)

    ws = find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/.", file=sys.stderr)
        sys.exit(2)

    mem_root = find_state_memory(ws)
    wings_root = os.path.join(mem_root, "wings")

    # Parse scope: 'architecture' or 'architecture/room'
    scope = args.bulk_update or ''
    parts = [p for p in scope.split('/') if p]

    if len(parts) == 0:
        search_root = wings_root
    elif len(parts) == 1:
        search_root = os.path.join(wings_root, parts[0])
    else:
        search_root = os.path.join(wings_root, parts[0], "rooms", parts[1])

    if not os.path.isdir(search_root):
        print(f"ERROR: Path not found: {search_root}", file=sys.stderr)
        sys.exit(1)

    # Collect candidate drawers
    drawer_files = []
    for dirpath, _, filenames in os.walk(search_root):
        if os.path.basename(dirpath) == "drawers":
            for fn in filenames:
                if fn.endswith(".json"):
                    drawer_files.append(os.path.join(dirpath, fn))
    drawer_files.sort()

    if not drawer_files:
        print("No drawer files found in scope.")
        return

    # Parse --older-than filter
    older_than_ts = None
    if args.older_than:
        try:
            from datetime import date
            d = date.fromisoformat(args.older_than)
            older_than_ts = d.strftime("%Y-%m-%d")
        except ValueError:
            print(f"ERROR: --older-than must be YYYY-MM-DD, got: {args.older_than!r}", file=sys.stderr)
            sys.exit(1)

    updated = 0
    skipped = 0
    failed = 0

    for path in drawer_files:
        try:
            data = json.loads(open(path, encoding="utf-8").read())
        except Exception as e:
            print(f"SKIP (unreadable)  {path}: {e}")
            failed += 1
            continue

        # Filter by current staleness state
        current_state = data.get("staleness_state", "")
        if args.current_state and current_state != args.current_state:
            skipped += 1
            continue

        # Filter by written_at date
        if older_than_ts:
            written_at = data.get("written_at", "")
            if written_at and written_at[:10] >= older_than_ts:
                skipped += 1
                continue

        # Skip if already in target state
        if current_state == args.staleness_state:
            skipped += 1
            continue

        if args.dry_run:
            print(f"WOULD UPDATE  {path}")
            print(f"  {current_state} -> {args.staleness_state}")
            updated += 1
            continue

        # Apply update using the existing update_drawer logic
        ts = now_utc()
        old_state = current_state
        data["staleness_state"] = args.staleness_state
        if args.staleness_state == "FRESH":
            data["last_verified"] = ts

        prov_entry = {
            "event": "TRANSITION" if args.staleness_state != "SUPERSEDED" else "SUPERSEDED",
            "timestamp": ts,
            "actor": args.actor or "memory",
            "from_state": old_state,
            "to_state": args.staleness_state,
            "note": args.note or f"Bulk update: {old_state} -> {args.staleness_state}",
        }
        if not isinstance(data.get("provenance"), list):
            data["provenance"] = []
        data["provenance"].append(prov_entry)

        errors = validate_drawer(data, path=path)
        if errors:
            print(f"SKIP (validation fail)  {path}")
            for e in errors:
                print(f"  {e}")
            failed += 1
            continue

        write_json(path, data)
        print(f"  {old_state} -> {args.staleness_state}")
        updated += 1

    action = "Would update" if args.dry_run else "Updated"
    print(f"\n{action} {updated}, skipped {skipped}, failed {failed} (of {len(drawer_files)} total)")
    if failed:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Schema-enforced writer for WabbleSpec memory drawers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Operations (manually enforced as mutually exclusive below)
    parser.add_argument("--id", metavar="ID",
                        help="Explicit drawer ID for create (auto-derived from --topic if omitted).")
    parser.add_argument("--update", metavar="PATH",
                        help="Update an existing drawer at PATH.")
    parser.add_argument("--validate", metavar="PATH",
                        help="Validate an existing drawer at PATH.")
    parser.add_argument("--validate-all", metavar="WING", nargs="?", const="", dest="validate_all",
                        help="Validate all drawers, or all in WING if specified.")
    parser.add_argument("--show", metavar="PATH",
                        help="Show human-readable summary of an existing drawer.")
    parser.add_argument("--list", metavar="WING[/ROOM]", nargs="?", const="",
                        help="List wings (no arg), rooms in WING, or drawers in WING/ROOM.")
    parser.add_argument("--bulk-update", metavar="WING[/ROOM]", nargs="?", const="", dest="bulk_update",
                        help="Transition all matching drawers to --staleness-state. "
                             "Scope: empty=all, WING, or WING/ROOM.")

    # Create-time fields
    parser.add_argument("--topic", metavar="TEXT")
    parser.add_argument("--wing", metavar="WING", choices=VALID_WINGS)
    parser.add_argument("--room", metavar="ROOM")
    parser.add_argument("--source", metavar="PATH_OR_STRING",
                        help="Source path or reference string.")
    parser.add_argument("--source-module", metavar="MODULE_ID", dest="source_module")
    parser.add_argument("--evidence", metavar="TEXT",
                        help="Evidence content string.")
    parser.add_argument("--evidence-file", metavar="PATH", dest="evidence_file",
                        help="Read evidence from a file instead of --evidence.")
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

    # Bulk-update filters
    parser.add_argument("--current-state", metavar="STATE", dest="current_state",
                        choices=VALID_STALENESS,
                        help="Bulk update only drawers currently in this staleness state.")
    parser.add_argument("--older-than", metavar="YYYY-MM-DD", dest="older_than",
                        help="Bulk update only drawers written before this date.")

    # Output / mode
    parser.add_argument("--out", metavar="PATH",
                        help="Explicit output path (create mode; auto-derived if omitted).")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    # Detect which operation is active
    ops = [x for x in ("update", "validate", "show") if getattr(args, x)]
    if args.validate_all is not None:
        ops.append("validate_all")
    if args.list is not None:
        ops.append("list")
    if args.bulk_update is not None:
        ops.append("bulk_update")

    if len(ops) > 1:
        print(f"ERROR: Conflicting operations: {ops}. Use only one at a time.", file=sys.stderr)
        sys.exit(1)

    if args.validate:
        cmd_validate(args)
    elif args.validate_all is not None:
        cmd_validate_all(args)
    elif args.show:
        cmd_show(args)
    elif args.update:
        cmd_update(args)
    elif args.list is not None:
        cmd_list(args)
    elif args.bulk_update is not None:
        cmd_bulk_update(args)
    else:
        # Create mode: requires --topic (--id is optional)
        if not args.topic:
            parser.print_help()
            print("\nERROR: create mode requires at least --topic.", file=sys.stderr)
            sys.exit(1)
        cmd_create(args)

    sys.exit(0)


if __name__ == "__main__":
    main()
