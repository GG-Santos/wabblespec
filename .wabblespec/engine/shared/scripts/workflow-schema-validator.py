"""
workflow-schema-validator.py — Validate a WabbleSpec workflow schema YAML file.

Checks:
  1. Required top-level fields present (name, version, phases)
  2. At least one phase
  3. Phase IDs unique
  4. Required phase fields present (id, skill, description)
  5. All required_before IDs reference known phase IDs
  6. No circular dependencies in required_before chains

Usage:
    python workflow-schema-validator.py <path-to-schema.yaml>
    python workflow-schema-validator.py --sample  (validate the built-in sample)

Exit codes:
    0  valid
    1  invalid (prints errors to stderr)
    2  file not found or unreadable
"""

import sys
import os
import json
import argparse

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False

REQUIRED_TOP_LEVEL = ["name", "version", "phases"]
REQUIRED_PHASE_FIELDS = ["id", "skill", "description"]


def find_wabblespec(start=None):
    cwd = start or os.getcwd()
    for _ in range(10):
        ws = os.path.join(cwd, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return None


def load_schema(path):
    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if _YAML:
            return yaml.safe_load(content)
        else:
            print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: could not parse {path}: {e}", file=sys.stderr)
        sys.exit(2)


def has_cycle(phase_id, required_before_map, visiting=None, visited=None):
    if visiting is None:
        visiting = set()
    if visited is None:
        visited = set()
    if phase_id in visited:
        return False
    if phase_id in visiting:
        return True
    visiting.add(phase_id)
    for dep in required_before_map.get(phase_id, []):
        if has_cycle(dep, required_before_map, visiting, visited):
            return True
    visiting.discard(phase_id)
    visited.add(phase_id)
    return False


def validate(schema):
    errors = []
    warnings = []

    # 1. Required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in schema:
            errors.append(f"MISSING_FIELD: required top-level field '{field}' is absent")

    phases = schema.get("phases", [])

    # 2. At least one phase
    if not isinstance(phases, list) or len(phases) == 0:
        errors.append("NO_PHASES: 'phases' must be a non-empty list")
        return errors, warnings

    # 3. Phase IDs unique
    phase_ids = []
    id_seen = set()
    for i, phase in enumerate(phases):
        pid = phase.get("id") if isinstance(phase, dict) else None
        if pid:
            if pid in id_seen:
                errors.append(f"DUPLICATE_PHASE_ID: phase id '{pid}' appears more than once")
            id_seen.add(pid)
            phase_ids.append(pid)

    phase_id_set = set(phase_ids)

    # 4. Required phase fields
    required_before_map = {}
    for phase in phases:
        if not isinstance(phase, dict):
            errors.append(f"INVALID_PHASE: phase entry is not a dict: {phase!r}")
            continue
        for field in REQUIRED_PHASE_FIELDS:
            if field not in phase:
                pid = phase.get("id", "<unknown>")
                errors.append(f"MISSING_PHASE_FIELD: phase '{pid}' missing required field '{field}'")
        pid = phase.get("id")
        required_before_map[pid] = phase.get("required_before", [])

    # 5. required_before references known IDs
    for phase in phases:
        if not isinstance(phase, dict):
            continue
        pid = phase.get("id", "<unknown>")
        for ref in phase.get("required_before", []):
            if ref not in phase_id_set:
                errors.append(f"UNKNOWN_PHASE_REF: phase '{pid}' references unknown phase '{ref}' in required_before")

    # 6. Circular dependency check
    for pid in phase_id_set:
        if has_cycle(pid, required_before_map):
            errors.append(f"CIRCULAR_DEP: phase '{pid}' is part of a circular dependency chain")
            break

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Validate a WabbleSpec workflow schema YAML file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("schema_path", nargs="?", metavar="PATH",
                        help="Path to workflow schema YAML to validate.")
    parser.add_argument("--sample", action="store_true",
                        help="Validate the built-in sample schema.")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON.")
    args = parser.parse_args()

    if args.sample:
        ws = find_wabblespec()
        if not ws:
            print("ERROR: Cannot find .wabblespec/", file=sys.stderr)
            sys.exit(2)
        schema_path = os.path.join(ws, "engine", "shared", "references", "workflow-schema-sample.yaml")
    elif args.schema_path:
        schema_path = args.schema_path
    else:
        parser.print_help()
        sys.exit(1)

    schema = load_schema(schema_path)
    errors, warnings = validate(schema)

    if args.json:
        result = {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "path": schema_path}
        print(json.dumps(result, indent=2))
    else:
        if errors:
            print(f"INVALID: {schema_path}")
            for e in errors:
                print(f"  ERROR: {e}")
            for w in warnings:
                print(f"  WARN:  {w}")
        else:
            name = schema.get("name", "?")
            phase_count = len(schema.get("phases", []))
            print(f"VALID: {schema_path}")
            print(f"  Schema: {name} | {phase_count} phase(s)")
            for w in warnings:
                print(f"  WARN: {w}")

    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
