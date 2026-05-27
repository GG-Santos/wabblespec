#!/usr/bin/env python3
"""
WabbleSpec Shift — compatibility-checker.py

Takes --change-class <class> --consumers <comma-list-of-module-ids>.
Reads framework.yaml to find actual dependencies.
Returns affected module list based on who depends on the changed module.

Usage:
  python modules/l1/shift/scripts/compatibility-checker.py --change-class BREAKING --consumers executor,verifier
  python modules/l1/shift/scripts/compatibility-checker.py --change-class ADDITIVE --module guard
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def find_ws_root() -> Path:
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p / ".wabblespec/wabblespec.yaml").exists():
            return p
    raise FileNotFoundError("No framework.yaml found from cwd")


def load_framework(root: Path) -> dict:
    fw_path = root / ".wabblespec/wabblespec.yaml"
    text = fw_path.read_text(encoding="utf-8")
    if HAS_YAML:
        return yaml.safe_load(text)
    # Minimal YAML parse for module id + depends_on only
    modules = []
    current: dict = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current:
                modules.append(current)
            current = {"id": stripped.split(":", 1)[1].strip(), "depends_on": []}
        elif stripped.startswith("depends_on:") and current:
            deps_raw = stripped.split(":", 1)[1].strip()
            if deps_raw.startswith("["):
                deps_raw = deps_raw.strip("[]")
                current["depends_on"] = [d.strip() for d in deps_raw.split(",") if d.strip()]
    if current:
        modules.append(current)
    return {"modules": modules}


def build_reverse_deps(modules: list[dict]) -> dict[str, list[str]]:
    """Map module_id -> list of module_ids that depend on it."""
    reverse: dict[str, list[str]] = {}
    for mod in modules:
        mod_id = mod.get("id", "")
        for dep in mod.get("depends_on", []):
            reverse.setdefault(dep, []).append(mod_id)
    return reverse


IMPACT_BY_CLASS = {
    "BREAKING": "UPDATE_REQUIRED",
    "DEPRECATION": "MIGRATION_REQUIRED",
    "ADDITIVE": "NONE",
    "COSMETIC": "NONE",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Shift compatibility-checker")
    parser.add_argument("--change-class", required=True,
                        choices=["BREAKING", "DEPRECATION", "ADDITIVE", "COSMETIC"],
                        help="Classification of the change")
    parser.add_argument("--consumers", default="",
                        help="Comma-separated list of module IDs that consume the changed module")
    parser.add_argument("--module", default="",
                        help="Changed module ID — auto-resolve consumers from framework.yaml depends_on")
    args = parser.parse_args()

    try:
        root = find_ws_root()
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        framework = load_framework(root)
    except Exception as e:
        print(f"ERROR: Could not load framework.yaml: {e}", file=sys.stderr)
        sys.exit(1)

    modules = framework.get("modules", [])
    reverse_deps = build_reverse_deps(modules)

    # Resolve consumer list
    if args.module:
        resolved_consumers = reverse_deps.get(args.module, [])
    elif args.consumers:
        resolved_consumers = [c.strip() for c in args.consumers.split(",") if c.strip()]
    else:
        resolved_consumers = []

    impact = IMPACT_BY_CLASS.get(args.change_class, "NONE")
    affected = []

    for consumer_id in resolved_consumers:
        mod = next((m for m in modules if m.get("id") == consumer_id), None)
        affected.append({
            "module_id": consumer_id,
            "affected": impact != "NONE",
            "action_required": impact,
            "layer": mod.get("layer", "unknown") if mod else "unknown",
        })

    result = {
        "change_class": args.change_class,
        "changed_module": args.module or "(consumer list provided directly)",
        "consumers_checked": affected,
        "downstream_consumers_affected": sum(1 for a in affected if a["affected"]),
        "loop_back_required": args.change_class == "BREAKING" and any(a["affected"] for a in affected),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
