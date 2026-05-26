"""
provenance-append.py — Append-only writer for the WabbleSpec provenance ledger.

Replaces Claude constructing provenance ledger entries and patching index.json.
The ledger (ledger.md) is append-only — this script never reads it before writing.
index.json is loaded, updated, and atomically written back.

Writes:
    .wabblespec/memory/provenance/ledger.md  — appended (open 'a', never read)
    .wabblespec/memory/provenance/index.json — load → update → atomic write

Subcommands:
    record        Record a Memory write event (new drawer written)
    cascade       Record a cascade event from a BREAKING spec change
    contradiction Record a contradiction between two drawers
    transition    Record a staleness state transition for a drawer
    delete        Record a deletion event (from Forget module)
    show          Show the index record for a drawer (reads index.json only)

Usage:
    # Record a Memory write event:
    python _shared/scripts/provenance-append.py record \\
        --drawer-id arch-layer-overview-20260526 \\
        --topic "WabbleSpec layer architecture overview" \\
        --source "_shared/references/invariants.md" \\
        --source-type reference \\
        --written-by memory \\
        --confidence 0.9

    # Record a cascade event (BREAKING spec change):
    python _shared/scripts/provenance-append.py cascade \\
        --spec-path modules/l2/executor/SKILL.md \\
        --change-class BREAKING \\
        --affected-drawers "arch-layer-overview-20260526" "executor-wave-protocol-20260525"

    # Record a contradiction:
    python _shared/scripts/provenance-append.py contradiction \\
        --drawer-id arch-layer-overview-20260526 \\
        --contradicts-drawer executor-wave-protocol-20260525 \\
        --description "Layer L2 description conflicts with wave protocol detail"

    # Record staleness transition:
    python _shared/scripts/provenance-append.py transition \\
        --drawer-id arch-layer-overview-20260526 \\
        --from-state FRESH \\
        --to-state AGING \\
        --reason "Activity decay after 30 days"

    # Record a deletion:
    python _shared/scripts/provenance-append.py delete \\
        --drawer-id old-drawer-20260521 \\
        --reason "Superseded by arch-layer-overview-20260526" \\
        --requesting-module forget

    # Show the index record for a drawer:
    python _shared/scripts/provenance-append.py show \\
        --drawer-id arch-layer-overview-20260526

Exit codes:
    0  success
    1  bad arguments or drawer not found in index (for show)
    2  provenance directory not found or not writable
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def find_provenance_dir(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        path = os.path.join(candidate, ".wabblespec", "memory", "provenance")
        if os.path.isdir(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Ledger append (never reads existing content)
# ---------------------------------------------------------------------------

def ledger_append(ledger_path, timestamp, event, drawer_id, actor, detail):
    """Append one row to ledger.md. Opens in append mode — never reads."""
    row = f"| {timestamp} | {event} | {drawer_id} | {actor} | {detail} |\n"
    try:
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(row)
    except OSError as e:
        print(f"ERROR: Cannot append to ledger {ledger_path}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Index CRUD (load → update → atomic write)
# ---------------------------------------------------------------------------

def load_index(index_path):
    if not os.path.isfile(index_path):
        return {"version": "1.0", "records": {}}
    try:
        with open(index_path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read index.json at {index_path}: {e}", file=sys.stderr)
        sys.exit(2)


def save_index(index_path, data):
    text = json.dumps(data, indent=2) + "\n"
    tmp = index_path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, index_path)
    except OSError as e:
        print(f"ERROR: Cannot write index.json at {index_path}: {e}", file=sys.stderr)
        sys.exit(2)


def empty_record(drawer_id, topic, source_path, source_type, written_by, confidence, ts):
    return {
        "drawer_id": drawer_id,
        "topic": topic,
        "source": {
            "path": source_path,
            "type": source_type,
            "trust_level": "HIGH" if float(confidence) >= 0.9 else "MEDIUM",
        },
        "written_by": written_by,
        "written_at": ts,
        "last_updated": ts,
        "confidence": confidence,
        "staleness_state": "FRESH",
        "last_verified": ts,
        "superseded_by": None,
        "source_hash": None,
        "cited_by": [],
        "cascade_events": [],
        "contradiction_with": [],
        "deletion": {
            "deleted": False,
            "deleted_at": None,
            "deleted_by": None,
            "reason": None,
            "archived_to": None,
        },
    }


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_record(args, prov_dir):
    ts = now_utc()
    ledger_path = os.path.join(prov_dir, "ledger.md")
    index_path = os.path.join(prov_dir, "index.json")

    detail = f"source={args.source} confidence={args.confidence}"

    ledger_append(ledger_path, ts, "WRITTEN", args.drawer_id, args.written_by, detail)

    index = load_index(index_path)
    rec = empty_record(
        args.drawer_id,
        args.topic or args.drawer_id,
        args.source,
        args.source_type or "reference",
        args.written_by,
        args.confidence,
        ts,
    )
    index["records"][args.drawer_id] = rec
    save_index(index_path, index)

    print(f"Recorded WRITTEN for {args.drawer_id}")
    print(f"  Ledger: {ledger_path}")
    print(f"  Index:  {index_path}")


def cmd_cascade(args, prov_dir):
    ts = now_utc()
    ledger_path = os.path.join(prov_dir, "ledger.md")
    index_path = os.path.join(prov_dir, "index.json")
    index = load_index(index_path)

    affected = args.affected_drawers or []
    detail = (
        f"change_class={args.change_class} "
        f"hop={args.hop_depth} "
        f"source={args.spec_path} "
        f"affected_drawers={len(affected)}"
    )

    for drawer_id in affected:
        ledger_append(ledger_path, ts, "CASCADE", drawer_id, "provenance", detail)

        # Update each affected drawer's index record
        if drawer_id in index["records"]:
            rec = index["records"][drawer_id]
            rec["last_updated"] = ts
            rec.setdefault("cascade_events", []).append({
                "triggered_at": ts,
                "change_class": args.change_class,
                "source_spec": args.spec_path,
                "hop_depth": args.hop_depth,
                "affected_specs": [],
            })
            # BREAKING cascade transitions FRESH → NEEDS_REVERIFICATION
            if args.change_class == "BREAKING" and rec.get("staleness_state") == "FRESH":
                old = rec["staleness_state"]
                rec["staleness_state"] = "NEEDS_REVERIFICATION"
                transition_detail = (
                    f"FRESH -> NEEDS_REVERIFICATION "
                    f"reason=BREAKING cascade from {os.path.basename(args.spec_path)}"
                )
                ledger_append(
                    ledger_path, ts, "STALENESS_TRANSITION",
                    drawer_id, "provenance", transition_detail
                )

    save_index(index_path, index)
    print(f"Recorded CASCADE ({args.change_class}) for {len(affected)} drawer(s): {affected}")


def cmd_contradiction(args, prov_dir):
    ts = now_utc()
    ledger_path = os.path.join(prov_dir, "ledger.md")
    index_path = os.path.join(prov_dir, "index.json")
    index = load_index(index_path)

    detail = f"contradicts={args.contradicts_drawer} desc={args.description or '(none)'}"
    ledger_append(ledger_path, ts, "CONTRADICTION", args.drawer_id, "provenance", detail)

    for did in (args.drawer_id, args.contradicts_drawer):
        if did in index["records"]:
            rec = index["records"][did]
            rec["last_updated"] = ts
            other = args.contradicts_drawer if did == args.drawer_id else args.drawer_id
            if other not in rec.get("contradiction_with", []):
                rec.setdefault("contradiction_with", []).append(other)

    save_index(index_path, index)
    print(f"Recorded CONTRADICTION: {args.drawer_id} <-> {args.contradicts_drawer}")


def cmd_transition(args, prov_dir):
    ts = now_utc()
    ledger_path = os.path.join(prov_dir, "ledger.md")
    index_path = os.path.join(prov_dir, "index.json")
    index = load_index(index_path)

    detail = f"{args.from_state} -> {args.to_state} reason={args.reason or '(none)'}"
    ledger_append(ledger_path, ts, "STALENESS_TRANSITION", args.drawer_id, "provenance", detail)

    if args.drawer_id in index["records"]:
        rec = index["records"][args.drawer_id]
        rec["staleness_state"] = args.to_state
        rec["last_updated"] = ts
        if args.to_state == "FRESH":
            rec["last_verified"] = ts
        save_index(index_path, index)
        print(f"Recorded STALENESS_TRANSITION for {args.drawer_id}: {args.from_state} -> {args.to_state}")
    else:
        # Ledger entry was written; index record doesn't exist — warn but don't fail
        save_index(index_path, index)
        print(f"WARNING: {args.drawer_id} not in index.json — ledger entry written but index not updated")


def cmd_delete(args, prov_dir):
    ts = now_utc()
    ledger_path = os.path.join(prov_dir, "ledger.md")
    index_path = os.path.join(prov_dir, "index.json")
    index = load_index(index_path)

    detail = f"reason={args.reason or '(none)'} by={args.requesting_module}"
    ledger_append(ledger_path, ts, "DELETED", args.drawer_id, args.requesting_module, detail)

    if args.drawer_id in index["records"]:
        rec = index["records"][args.drawer_id]
        rec["last_updated"] = ts
        rec["deletion"] = {
            "deleted": True,
            "deleted_at": ts,
            "deleted_by": args.requesting_module,
            "reason": args.reason,
            "archived_to": None,
        }
        save_index(index_path, index)

    print(f"Recorded DELETED for {args.drawer_id} (requested by {args.requesting_module})")


def cmd_show(args, prov_dir):
    index_path = os.path.join(prov_dir, "index.json")
    index = load_index(index_path)

    rec = index["records"].get(args.drawer_id)
    if rec is None:
        print(f"No index record found for '{args.drawer_id}'")
        print(f"Known drawers: {list(index['records'].keys())[:10]}")
        sys.exit(1)

    print(json.dumps(rec, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Append-only writer for the WabbleSpec provenance ledger.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--provenance-dir", metavar="PATH",
                        help="Explicit path to provenance directory.")

    sub = parser.add_subparsers(dest="command", required=True)

    # record
    p_rec = sub.add_parser("record", help="Record a new drawer write event.")
    p_rec.add_argument("--drawer-id", required=True, metavar="ID", dest="drawer_id")
    p_rec.add_argument("--topic", metavar="TEXT")
    p_rec.add_argument("--source", required=True, metavar="PATH_OR_STRING")
    p_rec.add_argument("--source-type", default="reference", metavar="TYPE", dest="source_type")
    p_rec.add_argument("--written-by", required=True, metavar="MODULE_ID", dest="written_by")
    p_rec.add_argument("--confidence", type=float, default=1.0, metavar="0.0-1.0")

    # cascade
    p_cas = sub.add_parser("cascade", help="Record a cascade from a spec change.")
    p_cas.add_argument("--spec-path", required=True, metavar="PATH", dest="spec_path")
    p_cas.add_argument("--change-class", required=True,
                       choices=["BREAKING", "ADDITIVE", "COSMETIC"], dest="change_class")
    p_cas.add_argument("--affected-drawers", nargs="+", metavar="DRAWER_ID",
                       dest="affected_drawers")
    p_cas.add_argument("--hop-depth", type=int, default=1, dest="hop_depth")

    # contradiction
    p_con = sub.add_parser("contradiction", help="Record a contradiction between two drawers.")
    p_con.add_argument("--drawer-id", required=True, metavar="ID", dest="drawer_id")
    p_con.add_argument("--contradicts-drawer", required=True, metavar="ID",
                       dest="contradicts_drawer")
    p_con.add_argument("--description", metavar="TEXT")

    # transition
    p_tr = sub.add_parser("transition", help="Record a staleness state transition.")
    p_tr.add_argument("--drawer-id", required=True, metavar="ID", dest="drawer_id")
    p_tr.add_argument("--from-state", required=True, metavar="STATE", dest="from_state")
    p_tr.add_argument("--to-state", required=True, metavar="STATE", dest="to_state")
    p_tr.add_argument("--reason", metavar="TEXT")

    # delete
    p_del = sub.add_parser("delete", help="Record a deletion event.")
    p_del.add_argument("--drawer-id", required=True, metavar="ID", dest="drawer_id")
    p_del.add_argument("--reason", metavar="TEXT")
    p_del.add_argument("--requesting-module", default="forget", metavar="MODULE_ID",
                       dest="requesting_module")

    # show
    p_sh = sub.add_parser("show", help="Show the index record for a drawer.")
    p_sh.add_argument("--drawer-id", required=True, metavar="ID", dest="drawer_id")

    args = parser.parse_args()

    prov_dir = args.provenance_dir or find_provenance_dir()
    if prov_dir is None:
        print("ERROR: Cannot find .wabblespec/memory/provenance/. "
              "Run from inside the repo or use --provenance-dir.", file=sys.stderr)
        sys.exit(2)

    dispatch = {
        "record": cmd_record,
        "cascade": cmd_cascade,
        "contradiction": cmd_contradiction,
        "transition": cmd_transition,
        "delete": cmd_delete,
        "show": cmd_show,
    }
    dispatch[args.command](args, prov_dir)
    sys.exit(0)


if __name__ == "__main__":
    main()
