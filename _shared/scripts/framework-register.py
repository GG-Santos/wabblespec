"""
framework-register.py — Read/patch framework.yaml without loading it into Claude's context.

Replaces the 52KB / ~13K-token framework.yaml read-reason-rewrite cycle that
occurs every time a module is added, validated, or updated.

All writes are atomic (temp-file + os.replace). YAML comments are NOT preserved
(PyYAML does not support round-trip comment preservation). Sections not touched
are rewritten verbatim from the parsed structure — field order within each module
entry follows the canonical order defined in this script.

Usage:
    # Register a new module (fails if id already exists):
    python _shared/scripts/framework-register.py register \\
        --id my-module \\
        --layer L5 \\
        --path modules/l5/my-module/ \\
        --tier 3 \\
        --tags memory,analysis \\
        --depends-on memory,provenance \\
        --description "Optional — not stored in framework.yaml but logged"

    # Update specific fields on an existing module:
    python _shared/scripts/framework-register.py set \\
        --id my-module \\
        --quality-floor-passed true \\
        --last-validated 2026-05-26 \\
        --build-status built

    # Bulk-update last_validated for all modules that pass quality-floor today:
    python _shared/scripts/framework-register.py touch-validated \\
        --ids recipe specify decompose guard \\
        --date 2026-05-26

    # Show one module entry as JSON:
    python _shared/scripts/framework-register.py show --id my-module

    # List all module IDs (with optional layer filter):
    python _shared/scripts/framework-register.py list --layer L5

    # Add a consumer to a shared artifact:
    python _shared/scripts/framework-register.py add-consumer \\
        --path _shared/schemas/receipt.base.schema.json \\
        --consumer my-module

Exit codes:
    0  success
    1  logical error (duplicate id, module not found, bad args)
    2  file not found or parse error
"""

import sys
import os
import json
import argparse
from datetime import date

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ---------------------------------------------------------------------------
# Canonical module field order for serialization
# ---------------------------------------------------------------------------

MODULE_FIELD_ORDER = [
    "id", "path", "type", "layer", "tags",
    "produces_schemas", "consumes_schemas", "depends_on",
    "last_validated", "quality_floor_passed", "build_status",
    "tier", "activators", "anti_activators", "file_path_patterns",
    "build_targets", "phases", "stages", "authority",
    "verification_mode", "receipt_required", "collapse_eligible",
    "commands", "promoted_from", "promoted_at",
]


def ordered_module(m):
    """Return module dict with canonical field ordering for stable diffs."""
    result = {}
    for key in MODULE_FIELD_ORDER:
        if key in m:
            result[key] = m[key]
    # Append any unknown fields at the end
    for key in m:
        if key not in result:
            result[key] = m[key]
    return result


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def find_framework(start_dir=None):
    if start_dir is None:
        start_dir = os.getcwd()
    candidate = start_dir
    for _ in range(10):
        path = os.path.join(candidate, "framework.yaml")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def load_framework(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or "modules" not in data:
            print(f"ERROR: {path} does not look like a valid framework.yaml", file=sys.stderr)
            sys.exit(2)
        return data
    except (OSError, yaml.YAMLError) as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)


def save_framework(path, data, dry_run=False):
    text = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    if dry_run:
        print(f"--- DRY RUN: would write {os.path.basename(path)} ({len(text)} bytes) ---")
        return
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def find_module(data, module_id):
    for m in data.get("modules", []):
        if m.get("id") == module_id:
            return m
    return None


def find_shared_artifact(data, artifact_path):
    """Find a shared artifact entry across schemas/references/infrastructure/templates."""
    shared = data.get("shared", {})
    for section_name, section in shared.items():
        if not isinstance(section, list):
            continue
        for item in section:
            if isinstance(item, dict) and item.get("path") == artifact_path:
                return section_name, item
    return None, None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_register(args, data, fw_path):
    if find_module(data, args.id):
        print(f"ERROR: Module '{args.id}' already exists. Use 'set' to update it.", file=sys.stderr)
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    depends = [d.strip() for d in args.depends_on.split(",")] if args.depends_on else []

    entry = ordered_module({
        "id": args.id,
        "path": args.path or f"modules/{args.layer.lower()}/{args.id}/",
        "type": "skill",
        "layer": args.layer,
        "tags": tags,
        "produces_schemas": [],
        "consumes_schemas": [],
        "depends_on": depends,
        "last_validated": "",
        "quality_floor_passed": False,
        "build_status": args.build_status or "deferred",
    })

    data["modules"].append(entry)
    save_framework(fw_path, data, dry_run=args.dry_run)

    print(f"Registered module '{args.id}' in framework.yaml")
    if args.description:
        print(f"  description (not stored): {args.description}")
    print(f"  layer: {args.layer}, path: {entry['path']}, build_status: {entry['build_status']}")
    if not args.dry_run:
        print(f"  Total modules now: {len(data['modules'])}")


def cmd_set(args, data, fw_path):
    m = find_module(data, args.id)
    if m is None:
        print(f"ERROR: Module '{args.id}' not found. Use 'register' to add it.", file=sys.stderr)
        sys.exit(1)

    changed = []

    if args.quality_floor_passed is not None:
        val = args.quality_floor_passed.lower() in ("true", "1", "yes")
        m["quality_floor_passed"] = val
        changed.append(f"quality_floor_passed={val}")

    if args.last_validated:
        m["last_validated"] = args.last_validated
        changed.append(f"last_validated={args.last_validated}")

    if args.build_status:
        m["build_status"] = args.build_status
        changed.append(f"build_status={args.build_status}")

    if args.tags:
        m["tags"] = [t.strip() for t in args.tags.split(",")]
        changed.append(f"tags={m['tags']}")

    if args.depends_on:
        m["depends_on"] = [d.strip() for d in args.depends_on.split(",")]
        changed.append(f"depends_on={m['depends_on']}")

    if args.path:
        m["path"] = args.path
        changed.append(f"path={args.path}")

    if args.layer:
        m["layer"] = args.layer
        changed.append(f"layer={args.layer}")

    if not changed:
        print("WARNING: No fields to update. Pass at least one of: "
              "--quality-floor-passed --last-validated --build-status "
              "--tags --depends-on --path --layer")
        sys.exit(1)

    save_framework(fw_path, data, dry_run=args.dry_run)
    print(f"Updated '{args.id}': {', '.join(changed)}")


def cmd_touch_validated(args, data, fw_path):
    today = args.date or date.today().isoformat()
    ids = [i.strip() for i in args.ids.split(",")]
    updated = []
    missing = []

    for mid in ids:
        m = find_module(data, mid)
        if m is None:
            missing.append(mid)
        else:
            m["last_validated"] = today
            updated.append(mid)

    if missing:
        print(f"WARNING: Modules not found (skipped): {missing}")

    if updated:
        save_framework(fw_path, data, dry_run=args.dry_run)
        print(f"Set last_validated={today} for {len(updated)} modules: {updated}")
    else:
        print("No modules updated.")
        sys.exit(1)


def cmd_show(args, data, fw_path):
    m = find_module(data, args.id)
    if m is None:
        print(f"ERROR: Module '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(m, indent=2))


def cmd_list(args, data, fw_path):
    modules = data.get("modules", [])
    if args.layer:
        modules = [m for m in modules if m.get("layer") == args.layer.upper()]
    if args.build_status:
        modules = [m for m in modules if m.get("build_status") == args.build_status]

    for m in modules:
        qf = "QF:PASS" if m.get("quality_floor_passed") else "QF:FAIL"
        bs = m.get("build_status", "?")
        print(f"  {m.get('id'):<30} {m.get('layer'):<5} {qf}  {bs}")
    print(f"\nTotal: {len(modules)}")


def cmd_add_consumer(args, data, fw_path):
    section_name, artifact = find_shared_artifact(data, args.path)
    if artifact is None:
        print(f"ERROR: Shared artifact '{args.path}' not found in framework.yaml shared section.",
              file=sys.stderr)
        sys.exit(1)

    consumers = artifact.get("consumers", [])
    if args.consumer in consumers:
        print(f"'{args.consumer}' is already a consumer of '{args.path}'")
        sys.exit(0)

    consumers.append(args.consumer)
    artifact["consumers"] = sorted(consumers)
    save_framework(fw_path, data, dry_run=args.dry_run)
    print(f"Added '{args.consumer}' to consumers of '{args.path}' (section: {section_name})")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Patch framework.yaml without reading it into Claude's context.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--framework", metavar="PATH", help="Explicit path to framework.yaml.")

    sub = parser.add_subparsers(dest="command", required=True)

    # register
    p_reg = sub.add_parser("register", help="Add a new module entry.")
    p_reg.add_argument("--id", required=True)
    p_reg.add_argument("--layer", required=True, choices=["L0","L1","L2","L3","L4","L5","L6","L7","L8"])
    p_reg.add_argument("--path", metavar="PATH")
    p_reg.add_argument("--tier", type=int, default=3, choices=[1,2,3,4,5])
    p_reg.add_argument("--tags", metavar="a,b,c")
    p_reg.add_argument("--depends-on", metavar="a,b,c")
    p_reg.add_argument("--build-status", default="deferred",
                       choices=["built","deferred","experimental","deprecated"])
    p_reg.add_argument("--description", metavar="TEXT", help="Logged only, not stored in YAML.")
    p_reg.add_argument("--dry-run", action="store_true")

    # set
    p_set = sub.add_parser("set", help="Update fields on an existing module.")
    p_set.add_argument("--id", required=True)
    p_set.add_argument("--quality-floor-passed", metavar="true|false")
    p_set.add_argument("--last-validated", metavar="YYYY-MM-DD")
    p_set.add_argument("--build-status", choices=["built","deferred","experimental","deprecated"])
    p_set.add_argument("--tags", metavar="a,b,c")
    p_set.add_argument("--depends-on", metavar="a,b,c")
    p_set.add_argument("--dry-run", action="store_true")
    p_set.add_argument("--path", metavar="PATH")
    p_set.add_argument("--layer", choices=["L0","L1","L2","L3","L4","L5","L6","L7","L8"])

    # touch-validated
    p_tv = sub.add_parser("touch-validated", help="Bulk-set last_validated date.")
    p_tv.add_argument("--ids", required=True, metavar="id1,id2,...")
    p_tv.add_argument("--date", metavar="YYYY-MM-DD", help="Default: today.")
    p_tv.add_argument("--dry-run", action="store_true")

    # show
    p_sh = sub.add_parser("show", help="Print one module entry as JSON.")
    p_sh.add_argument("--id", required=True)

    # list
    p_ls = sub.add_parser("list", help="List module IDs with status.")
    p_ls.add_argument("--layer", metavar="L5")
    p_ls.add_argument("--build-status", metavar="built|deferred")

    # add-consumer
    p_ac = sub.add_parser("add-consumer", help="Add a module as consumer of a shared artifact.")
    p_ac.add_argument("--path", required=True, metavar="ARTIFACT_PATH")
    p_ac.add_argument("--consumer", required=True, metavar="MODULE_ID")
    p_ac.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    # Ensure dry_run attribute exists for all subcommands
    if not hasattr(args, "dry_run"):
        args.dry_run = False

    # Locate framework.yaml
    fw_path = args.framework or find_framework()
    if fw_path is None:
        print("ERROR: Cannot find framework.yaml. Run from inside the repo.", file=sys.stderr)
        sys.exit(2)

    data = load_framework(fw_path)

    dispatch = {
        "register": cmd_register,
        "set": cmd_set,
        "touch-validated": cmd_touch_validated,
        "show": cmd_show,
        "list": cmd_list,
        "add-consumer": cmd_add_consumer,
    }
    dispatch[args.command](args, data, fw_path)
    sys.exit(0)


if __name__ == "__main__":
    main()
