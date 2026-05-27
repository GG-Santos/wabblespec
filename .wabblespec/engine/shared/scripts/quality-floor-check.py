"""
WabbleSpec quality floor checker.

Runs quick_validate (8 checks) and lint_prompts (6 checks) on every module
declared in framework.yaml. Rules defined in .wabblespec/engine/shared/references/quality-floor-gates.md.

Exit codes:
  0 = all modules pass both gates
  1 = one or more modules fail
  2 = input error (file not found, parse error)

Usage:
  python quality-floor-check.py
  python quality-floor-check.py --verbose
  python quality-floor-check.py --module recipe
  python quality-floor-check.py --update-yaml
  python quality-floor-check.py --write
  python quality-floor-check.py --framework path/to/.wabblespec/wabblespec.yaml
"""

import sys
import json
import os
import re
import argparse

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ─── Loaders ─────────────────────────────────────────────────────────────────

def load_framework(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse {path}: {e}", file=sys.stderr)
        sys.exit(2)


def load_rules(rules_path):
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        return None, str(e)


def load_skill(skill_path):
    try:
        with open(skill_path, "r", encoding="utf-8-sig") as f:
            return f.read(), None
    except OSError as e:
        return None, str(e)


# ─── Gate 1: quick_validate ───────────────────────────────────────────────────

REQUIRED_RULE_FIELDS = [
    "module", "layer", "tier", "activators",
    "authority", "verification_mode", "receipt_required",
]


def quick_validate(module_dir, rules_data, rules_error):
    checks = {}

    skill_path = os.path.join(module_dir, "SKILL.md")
    rules_path = os.path.join(module_dir, "skill-rules.json")

    checks["SKILL_EXISTS"] = os.path.isfile(skill_path)
    checks["RULES_EXISTS"] = os.path.isfile(rules_path)

    if rules_error:
        checks["RULES_PARSE"] = False
    else:
        checks["RULES_PARSE"] = rules_data is not None

    if rules_data:
        checks["REQUIRED_FIELDS"] = all(f in rules_data for f in REQUIRED_RULE_FIELDS)

        auth = rules_data.get("authority", {})
        owns = auth.get("owns") if isinstance(auth, dict) else None
        checks["AUTHORITY_OWNS"] = isinstance(owns, list) and len(owns) > 0

        reads = auth.get("reads") if isinstance(auth, dict) else None
        checks["AUTHORITY_READS"] = isinstance(reads, list)

        checks["RECEIPT_BOOL"] = isinstance(rules_data.get("receipt_required"), bool)

        activators = rules_data.get("activators", [])
        loading_gate = rules_data.get("loading_gate", "")
        commands = rules_data.get("commands", [])
        checks["ACTIVATORS_VALID"] = (
            (isinstance(activators, list) and len(activators) > 0)
            or loading_gate == "phase"
            or (isinstance(commands, list) and len(commands) > 0)
        )
    else:
        for key in ("REQUIRED_FIELDS", "AUTHORITY_OWNS", "AUTHORITY_READS",
                    "RECEIPT_BOOL", "ACTIVATORS_VALID"):
            checks[key] = False

    passed = all(checks.values())
    return passed, checks


# ─── Gate 2: lint_prompts ─────────────────────────────────────────────────────

OUTPUT_SIGNALS = [
    "## Output contract",
    "## Outputs",
    "receipt**",
    "**receipt",
]


def lint_prompts(module_dir):
    checks = {}

    skill_path = os.path.join(module_dir, "SKILL.md")
    if not os.path.isfile(skill_path):
        return False, {k: False for k in (
            "FRONTMATTER", "DESCRIPTION_LEN", "SECTION_WHAT",
            "SECTION_WHEN", "SECTION_OUTPUT", "MIN_LENGTH"
        )}

    content, err = load_skill(skill_path)
    if err or content is None:
        return False, {k: False for k in (
            "FRONTMATTER", "DESCRIPTION_LEN", "SECTION_WHAT",
            "SECTION_WHEN", "SECTION_OUTPUT", "MIN_LENGTH"
        )}

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    fm_body = fm_match.group(1) if fm_match else ""
    checks["FRONTMATTER"] = bool(fm_match) and "name:" in fm_body and "description:" in fm_body

    desc_match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
    checks["DESCRIPTION_LEN"] = bool(desc_match) and len(desc_match.group(1).strip()) >= 20

    body = content[fm_match.end():].strip() if fm_match else content.strip()

    checks["SECTION_WHAT"] = "## What this skill does" in content
    checks["SECTION_WHEN"] = "## When to use" in content
    checks["SECTION_OUTPUT"] = any(sig in content for sig in OUTPUT_SIGNALS)
    checks["MIN_LENGTH"] = len(body) >= 200

    return all(checks.values()), checks


# ─── Adversarial warning ──────────────────────────────────────────────────────

def adversarial_warning(module_dir, rules_data, adversarial_tags):
    if not rules_data:
        return None
    tags = rules_data.get("tags", [])
    if not isinstance(tags, list):
        return None
    if not any(t in adversarial_tags for t in tags):
        return None

    skill_path = os.path.join(module_dir, "SKILL.md")
    content, _ = load_skill(skill_path)
    if content is None:
        return False
    return "adversarial" in content.lower()


# ─── framework.yaml patcher ───────────────────────────────────────────────────

def patch_framework_yaml(framework_path, passing_ids):
    with open(framework_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_id = None
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        id_match = re.match(r"^\s+- id:\s+(\S+)", line)
        if id_match:
            current_id = id_match.group(1)
        if current_id in passing_ids and re.match(r"^\s+quality_floor_passed:\s+\S+", line):
            indent = len(line) - len(line.lstrip())
            line = " " * indent + "quality_floor_passed: true\n"
        out.append(line)
        i += 1

    with open(framework_path, "w", encoding="utf-8") as f:
        f.writelines(out)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WabbleSpec quality floor gate checker"
    )
    parser.add_argument("--framework", default=".wabblespec/wabblespec.yaml",
                        help="Path to framework.yaml (default: framework.yaml)")
    parser.add_argument("--module", metavar="ID",
                        help="Check a single module by ID")
    parser.add_argument("--verbose", action="store_true",
                        help="Print all check results, not just failures")
    parser.add_argument("--update-yaml", action="store_true",
                        help="Print passing module IDs for human review")
    parser.add_argument("--write", action="store_true",
                        help="Patch framework.yaml quality_floor_passed (opt-in)")
    args = parser.parse_args()

    framework_path = args.framework
    framework_dir = os.path.dirname(os.path.abspath(framework_path))
    data = load_framework(framework_path)

    qf = data.get("quality_floor", {})
    adversarial_tags = set(qf.get("adversarial_required_for_tags", []))

    modules = data.get("modules", [])
    if args.module:
        modules = [m for m in modules if m.get("id") == args.module]
        if not modules:
            print(f"ERROR: module '{args.module}' not found in framework.yaml", file=sys.stderr)
            sys.exit(2)

    results = []

    # Skip modules on non-standard layers (e.g. layer: shared) — they are
    # reference collections, not skill modules, and have no SKILL.md structure.
    standard_layer = re.compile(r"^L\d+$", re.IGNORECASE)
    modules = [m for m in modules if standard_layer.match(str(m.get("layer", "")))]

    for entry in modules:
        mid = entry.get("id", "<unknown>")
        rel_path = entry.get("path", "")
        module_dir = os.path.join(framework_dir, rel_path.replace("/", os.sep))

        rules_path = os.path.join(module_dir, "skill-rules.json")
        if os.path.isfile(rules_path):
            rules_data, rules_error = load_rules(rules_path)
        else:
            rules_data, rules_error = None, None

        qv_pass, qv_checks = quick_validate(module_dir, rules_data, rules_error)
        lp_pass, lp_checks = lint_prompts(module_dir)
        adv = adversarial_warning(module_dir, rules_data, adversarial_tags)

        overall = qv_pass and lp_pass
        results.append({
            "id": mid,
            "pass": overall,
            "quick_validate": {"pass": qv_pass, "checks": qv_checks},
            "lint_prompts": {"pass": lp_pass, "checks": lp_checks},
            "adversarial_warning": adv,
        })

    if args.update_yaml:
        passing = [r["id"] for r in results if r["pass"]]
        print(f"# Passing module IDs ({len(passing)}/{len(results)})")
        for mid in passing:
            print(f"  {mid}")
        return

    # ── Standard report ──
    total = len(results)
    passing = sum(1 for r in results if r["pass"])
    fail_qv = sum(1 for r in results if not r["quick_validate"]["pass"])
    fail_lp = sum(1 for r in results if not r["lint_prompts"]["pass"])
    warnings = sum(1 for r in results if r["adversarial_warning"] is False)

    print(f"WabbleSpec quality floor check")
    print(f"  Modules checked:          {total}")
    print(f"  Passing both gates:       {passing}")
    print(f"  Failing quick_validate:   {fail_qv}")
    print(f"  Failing lint_prompts:     {fail_lp}")
    print(f"  Adversarial warnings:     {warnings}")
    print()

    any_failure = False
    for r in results:
        mid = r["id"]
        verdict = "PASS" if r["pass"] else "FAIL"

        show = args.verbose or not r["pass"] or r["adversarial_warning"] is False
        if not show:
            continue

        print(f"  [{verdict}] {mid}")

        if args.verbose or not r["quick_validate"]["pass"]:
            for check, result in r["quick_validate"]["checks"].items():
                if args.verbose or not result:
                    mark = "+" if result else "-"
                    print(f"           quick_validate.{check}: {mark}")

        if args.verbose or not r["lint_prompts"]["pass"]:
            for check, result in r["lint_prompts"]["checks"].items():
                if args.verbose or not result:
                    mark = "+" if result else "-"
                    print(f"           lint_prompts.{check}: {mark}")

        if r["adversarial_warning"] is False:
            print(f"           [WARN] adversarial_required tag present but 'adversarial' not in SKILL.md")

        if not r["pass"]:
            any_failure = True

    if not any_failure and not args.verbose:
        print("  All modules PASS")

    if args.write:
        passing_ids = {r["id"] for r in results if r["pass"]}
        patch_framework_yaml(framework_path, passing_ids)
        print(f"\n--write: patched quality_floor_passed for {len(passing_ids)} modules in {framework_path}")

    sys.exit(1 if any_failure else 0)


if __name__ == "__main__":
    main()
