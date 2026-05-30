"""
error-event-writer.py — Schema-enforced writer for WabbleSpec error events.

Enforces the error-event.schema.json type enum and auto-derives routing.action
and recoverable from the error type. Modules call this instead of constructing
error JSON ad-hoc.

Usage:
    # SOFT error (auto: recoverable=true, routing=retry):
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --type SOFT \\
        --module verifier \\
        --message "Acceptance criterion V-03 not met; retrying"

    # HARD error (auto: recoverable=false, routing=halt):
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --type HARD \\
        --module executor \\
        --message "Wave plan file missing; cannot continue" \\
        --out .wabblespec/state/session/errors/hard-20260531T120000Z.json

    # DEPENDENCY error (auto: routing=pause, target=upstream_module):
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --type DEPENDENCY \\
        --module executor \\
        --message "Guard has not run for this wave" \\
        --upstream-module guard

    # STALENESS_VIOLATION (auto: routing=quarantine, target=artifact):
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --type STALENESS_VIOLATION \\
        --module guard \\
        --message "Evidence drawer is EXPIRED" \\
        --artifact ".wabblespec/state/memory/wings/architecture/rooms/hooks/drawers/hook-architecture-detail-20260525.json" \\
        --staleness-state EXPIRED

    # SPEC_VIOLATION (auto: routing=loop_back):
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --type SPEC_VIOLATION \\
        --module verifier \\
        --message "Output does not satisfy AC-02" \\
        --artifact ".wabblespec/state/plans/task-card.md"

    # CONTEXT_EXHAUSTION (auto: recoverable=true, routing=compress):
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --type CONTEXT_EXHAUSTION \\
        --module executor \\
        --message "Context limit approaching; compressing"

    # Dry run — print JSON without writing:
    python .wabblespec/engine/shared/scripts/error-event-writer.py ... --dry-run

    # Validate an existing error event:
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --validate path/to/error.json

    # Show human-readable summary:
    python .wabblespec/engine/shared/scripts/error-event-writer.py \\
        --show path/to/error.json

Error type routing table (from error-event.schema.json $comment):
    SOFT              → recoverable=true,  action=retry
    HARD              → recoverable=false, action=halt
    DEPENDENCY        → recoverable=false, action=pause,    target=upstream_module
    CONTEXT_EXHAUSTION→ recoverable=true,  action=compress
    SPEC_VIOLATION    → recoverable=false, action=loop_back
    STALENESS_VIOLATION→recoverable=false, action=quarantine, target=artifact

Output:
    If --out is specified, writes JSON to that file.
    Otherwise prints JSON to stdout (error events are often ephemeral / piped).

Exit codes:
    0  success
    1  validation failure or bad arguments
    2  file not writable
"""

from __future__ import annotations

import sys
import os
import json
import argparse
from datetime import datetime, timezone

VALID_TYPES = [
    "SOFT", "HARD", "DEPENDENCY", "CONTEXT_EXHAUSTION",
    "SPEC_VIOLATION", "STALENESS_VIOLATION",
]

VALID_STALENESS = [
    "FRESH", "AGING", "STALE", "EXPIRED", "NEEDS_REVERIFICATION", "SUPERSEDED",
]

REQUIRED_FIELDS = ["type", "module", "message", "timestamp", "recoverable"]

# Routing table: type → (action, recoverable, needs_target)
_ROUTING = {
    "SOFT":               ("retry",      True,  None),
    "HARD":               ("halt",       False, None),
    "DEPENDENCY":         ("pause",      False, "upstream_module"),
    "CONTEXT_EXHAUSTION": ("compress",   True,  None),
    "SPEC_VIOLATION":     ("loop_back",  False, "artifact"),
    "STALENESS_VIOLATION":("quarantine", False, "artifact"),
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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
    print(f"Wrote {path}", file=sys.stderr)


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

def validate_event(data, path=None):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    t = data.get("type")
    if t and t not in VALID_TYPES:
        errors.append(f"type '{t}' not in {VALID_TYPES}")

    if data.get("staleness_state") and data["staleness_state"] not in VALID_STALENESS:
        errors.append(f"staleness_state '{data['staleness_state']}' not in {VALID_STALENESS}")

    # Cross-field checks
    if t == "DEPENDENCY" and not data.get("upstream_module"):
        errors.append("type=DEPENDENCY requires upstream_module")
    if t == "STALENESS_VIOLATION" and not data.get("artifact"):
        errors.append("type=STALENESS_VIOLATION requires artifact")
    if t == "STALENESS_VIOLATION" and not data.get("staleness_state"):
        errors.append("type=STALENESS_VIOLATION requires staleness_state")

    return errors


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def derive_routing(error_type, upstream_module=None, artifact=None):
    action, recoverable, target_field = _ROUTING[error_type]
    routing = {"action": action}
    if target_field == "upstream_module" and upstream_module:
        routing["target"] = upstream_module
    elif target_field == "artifact" and artifact:
        routing["target"] = artifact
    return routing, recoverable


def build_event(args):
    routing, recoverable = derive_routing(
        args.type,
        upstream_module=args.upstream_module,
        artifact=args.artifact,
    )

    event = {
        "type": args.type,
        "module": args.module,
        "message": args.message,
        "timestamp": now_utc(),
        "recoverable": recoverable,
        "routing": routing,
    }

    if args.upstream_module:
        event["upstream_module"] = args.upstream_module
    if args.artifact:
        event["artifact"] = args.artifact
    if args.staleness_state:
        event["staleness_state"] = args.staleness_state

    return event


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_create(args):
    missing = []
    for field in ("type", "module", "message"):
        if not getattr(args, field, None):
            missing.append(f"--{field}")
    if missing:
        print(f"ERROR: Missing required arguments: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    if args.type not in VALID_TYPES:
        print(f"ERROR: --type must be one of {VALID_TYPES}", file=sys.stderr)
        sys.exit(1)

    # Guard cross-field requirements before building
    if args.type == "DEPENDENCY" and not args.upstream_module:
        print("ERROR: --type DEPENDENCY requires --upstream-module", file=sys.stderr)
        sys.exit(1)
    if args.type == "STALENESS_VIOLATION":
        if not args.artifact:
            print("ERROR: --type STALENESS_VIOLATION requires --artifact", file=sys.stderr)
            sys.exit(1)
        if not args.staleness_state:
            print("ERROR: --type STALENESS_VIOLATION requires --staleness-state", file=sys.stderr)
            sys.exit(1)

    event = build_event(args)

    errors = validate_event(event)
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    text = json.dumps(event, indent=2) + "\n"

    if args.dry_run:
        out_label = args.out or "stdout"
        print(f"--- [DRY RUN] {out_label} ---")
        print(text)
        return

    if args.out:
        write_json(args.out, event)
    else:
        print(text)


def cmd_validate(args):
    data = load_json(args.validate)
    errors = validate_event(data, path=args.validate)
    if errors:
        print(f"FAIL  {args.validate}")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"PASS  {args.validate}")
        print(f"  type: {data.get('type')}, module: {data.get('module')}, "
              f"recoverable: {data.get('recoverable')}, "
              f"routing: {data.get('routing', {}).get('action')}")


def cmd_show(args):
    data = load_json(args.show)
    print(f"type:            {data.get('type')}")
    print(f"module:          {data.get('module')}")
    print(f"message:         {data.get('message')}")
    print(f"timestamp:       {data.get('timestamp')}")
    print(f"recoverable:     {data.get('recoverable')}")
    routing = data.get("routing") or {}
    print(f"routing.action:  {routing.get('action')}")
    if routing.get("target"):
        print(f"routing.target:  {routing.get('target')}")
    if data.get("upstream_module"):
        print(f"upstream_module: {data.get('upstream_module')}")
    if data.get("artifact"):
        print(f"artifact:        {data.get('artifact')}")
    if data.get("staleness_state"):
        print(f"staleness_state: {data.get('staleness_state')}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Schema-enforced writer for WabbleSpec error events.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Operations
    parser.add_argument("--validate", metavar="PATH",
                        help="Validate an existing error event JSON.")
    parser.add_argument("--show", metavar="PATH",
                        help="Show human-readable summary of an existing error event.")

    # Create-time fields
    parser.add_argument("--type", metavar="TYPE", choices=VALID_TYPES,
                        help=f"Error type. One of: {', '.join(VALID_TYPES)}")
    parser.add_argument("--module", metavar="MODULE_ID",
                        help="Module that emitted the error.")
    parser.add_argument("--message", metavar="TEXT",
                        help="Human-readable error description.")
    parser.add_argument("--upstream-module", metavar="MODULE_ID", dest="upstream_module",
                        help="Required for DEPENDENCY: which upstream module failed.")
    parser.add_argument("--artifact", metavar="PATH_OR_ID",
                        help="Required for SPEC_VIOLATION / STALENESS_VIOLATION: offending artifact.")
    parser.add_argument("--staleness-state", metavar="STATE", dest="staleness_state",
                        choices=VALID_STALENESS,
                        help="Required for STALENESS_VIOLATION: staleness state of the artifact.")

    # Output / mode
    parser.add_argument("--out", metavar="PATH",
                        help="Write to this file. If omitted, prints to stdout.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written without writing.")

    args = parser.parse_args()

    ops = [x for x in ("validate", "show") if getattr(args, x)]
    if len(ops) > 1:
        print(f"ERROR: Conflicting operations: {ops}. Use only one.", file=sys.stderr)
        sys.exit(1)

    if args.validate:
        cmd_validate(args)
    elif args.show:
        cmd_show(args)
    else:
        if not args.type:
            parser.print_help()
            print("\nERROR: create mode requires at least --type, --module, --message.", file=sys.stderr)
            sys.exit(1)
        cmd_create(args)

    sys.exit(0)


if __name__ == "__main__":
    main()
