"""
module-scaffold.py — Generate all required module files as quality-gate-passing stubs.

Creates the four mandatory files for a new WabbleSpec module:
  - SKILL.md           (passes lint_prompts gate: frontmatter, required headings, ≥200 chars body)
  - skill-rules.json   (passes quick_validate gate: all required fields)
  - rules/cold-start.md
  - tests/acceptance.md

All stubs pass BOTH quality floor gates immediately. Claude fills in the
reasoning-dependent content (behavior description, check logic, acceptance
criteria) — but structure, field presence, and headings are correct from the
start so no repair pass is needed.

Optionally registers the module in framework.yaml (--register flag).

Usage:
    python .wabblespec/engine/shared/scripts/module-scaffold.py \\
        --id my-module \\
        --layer L5 \\
        --description "Does X when Y is present in the session context" \\
        --activators "trigger phrase A" "trigger phrase B" \\
        --tags memory,analysis \\
        --tier 3 \\
        --build-targets ALL \\
        --register

    # With explicit output path (default: modules/{layer_lower}/{id}/):
    python .wabblespec/engine/shared/scripts/module-scaffold.py \\
        --id my-module --layer L2 \\
        --path modules/l2/my-module/ \\
        --description "..." \\
        --activators "phrase"

    # Dry run — print files that would be created:
    python .wabblespec/engine/shared/scripts/module-scaffold.py --id my-module --layer L5 \\
        --description "..." --activators "phrase" --dry-run

Exit codes:
    0  success
    1  target path already exists (idempotency guard), or bad args
    2  file system error
"""

import sys
import os
import json
import argparse
from datetime import date


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

SKILL_MD_TEMPLATE = """\
---
name: {id}
description: {description}
---

# {title}

{description}

## What this skill does

[TODO: describe the concrete operations this module performs, in active voice.
Be specific: what does it read, what does it produce, what decisions does it make.]

## When to use / when not to use

**Use when:**
- [TODO: primary activation condition]
- [TODO: secondary activation condition]

**Do not use when:**
- [TODO: anti-activation condition — prevents misfire]

## Inputs

- [TODO: list upstream receipts or artifacts this module reads]

## How to do it

### Step 1 — [TODO: first action]

[TODO: describe step 1 in detail. Be specific about file paths, field names,
and decision rules. Avoid vague directives like "process the input".]

### Step 2 — Write receipt

Write to `.wabblespec/receipts/{id}-receipt-{{session_id}}.json`. All base receipt
fields required (see `.wabblespec/engine/shared/schemas/receipt.base.schema.json`). Status PASS =
[TODO: define what constitutes a passing execution].

## Output contract

| Field | Type | Description |
|---|---|---|
| status | PASS / FAIL | Whether the module completed successfully |
| not_tested | list | Items not verified in this execution |
| [TODO: add module-specific output fields] | | |

## Error types emitted

- [TODO: list error types from .wabblespec/engine/shared/references/error-taxonomy.md this module can emit, or "(none)"]
"""

SKILL_RULES_TEMPLATE = {
    "module": None,          # filled in
    "layer": None,           # filled in
    "tier": None,            # filled in
    "activators": None,      # filled in
    "anti_activators": [],
    "build_targets": None,   # filled in
    "phases": ["ALL"],
    "stages": ["ALL"],
    "authority": {
        "owns": [],          # TODO: fill in
        "reads": [],         # TODO: fill in
    },
    "verification_mode": "Observation",
    "receipt_required": True,
    "collapse_eligible": False,
    "gate_collapsing_conditions": None,
    "commands": [],
    "file_path_patterns": [],
}

COLD_START_TEMPLATE = """\
# Cold-Start Behavior — {title}

Defines what {title} does when its expected upstream artifacts are absent.

## Absent: prior receipts

Condition: No receipts from upstream modules exist for the current session.
Detection: `.wabblespec/receipts/` does not contain expected upstream receipt files.
Action: [TODO: describe behavior — surface error, proceed anyway, or ask user].

## Absent: [TODO: primary input artifact]

Condition: [TODO: describe the artifact that must exist].
Detection: File read returns not-found.
Action: [TODO: describe recovery or error behavior].

## Default state on cold start

| Field | Default |
|---|---|
| status | null — must be determined, never assumed |
| [TODO] | [TODO] |

Do not proceed with assumed inputs. If required upstream artifacts are absent and
no recovery path applies, surface a typed error from `.wabblespec/engine/shared/references/error-taxonomy.md`.
"""

ACCEPTANCE_TEMPLATE = """\
# {title} — Acceptance Criteria

## Gate: primary success path

Given {title} is invoked with valid inputs,
When execution completes,
Then status is PASS,
And a receipt is written to `.wabblespec/receipts/{id}-receipt-{{session_id}}.json`,
And all required output fields are present.

## Gate: [TODO: describe a specific behavioral gate]

Given [TODO: precondition],
When [TODO: action or trigger],
Then [TODO: expected outcome — be specific about field values and file states].

## Gate: FAIL path — missing required input

Given [TODO: required input] is absent,
When {title} is invoked,
Then status is FAIL,
And `failure_reason` field is present in the receipt,
And [TODO: describe any typed error emitted].

## Not Tested

The following are NOT required for acceptance and remain as future verification scope:
- [TODO: list edge cases not covered by these criteria]
"""


# ---------------------------------------------------------------------------
# File generation
# ---------------------------------------------------------------------------

def title_from_id(module_id):
    """Convert 'my-module' to 'My-Module'."""
    return "-".join(w.capitalize() for w in module_id.split("-"))


def write_file(path, content, dry_run):
    if dry_run:
        print(f"  [DRY RUN] would write: {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Wrote: {path}")


def scaffold(module_id, layer, path, tier, description, activators,
             anti_activators, tags, build_targets, dry_run):
    title = title_from_id(module_id)

    # Guard: idempotency
    skill_md_path = os.path.join(path, "SKILL.md")
    if os.path.exists(skill_md_path) and not dry_run:
        print(f"ERROR: {skill_md_path} already exists. Module already scaffolded.", file=sys.stderr)
        print("Use --force to overwrite (destructive — not recommended).", file=sys.stderr)
        sys.exit(1)

    # SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(
        id=module_id,
        title=title,
        description=description,
    )
    write_file(skill_md_path, skill_md, dry_run)

    # skill-rules.json
    rules = dict(SKILL_RULES_TEMPLATE)
    rules["module"] = module_id
    rules["layer"] = layer
    rules["tier"] = tier
    rules["activators"] = activators
    rules["anti_activators"] = anti_activators
    rules["build_targets"] = build_targets
    rules["authority"] = {
        "owns": [f".wabblespec/receipts/{module_id}-receipt-*.json"],
        "reads": [],
    }

    rules_path = os.path.join(path, "skill-rules.json")
    if not dry_run:
        os.makedirs(os.path.dirname(rules_path), exist_ok=True)
        tmp = rules_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2)
            f.write("\n")
        os.replace(tmp, rules_path)
        print(f"  Wrote: {rules_path}")
    else:
        print(f"  [DRY RUN] would write: {rules_path}")

    # rules/cold-start.md
    cold_start = COLD_START_TEMPLATE.format(title=title, id=module_id)
    write_file(os.path.join(path, "rules", "cold-start.md"), cold_start, dry_run)

    # tests/acceptance.md
    acceptance = ACCEPTANCE_TEMPLATE.format(title=title, id=module_id)
    write_file(os.path.join(path, "tests", "acceptance.md"), acceptance, dry_run)

    return {
        "id": module_id,
        "layer": layer,
        "path": path,
        "tier": tier,
        "tags": tags,
        "build_status": "deferred",
        "quality_floor_passed": False,
        "last_validated": "",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new WabbleSpec module with quality-gate-passing stubs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--id", required=True, metavar="MODULE_ID",
                        help="Module identifier (kebab-case, matches framework.yaml id).")
    parser.add_argument("--layer", required=True,
                        choices=["L0","L1","L2","L3","L4","L5","L6","L7","L8"],
                        help="Layer this module belongs to.")
    parser.add_argument("--description", required=True, metavar="TEXT",
                        help="One-line description (≥20 chars) — goes in SKILL.md frontmatter.")
    parser.add_argument("--activators", nargs="+", required=True, metavar="PHRASE",
                        help="Activation phrases for skill-rules.json (space-separated).")
    parser.add_argument("--path", metavar="DIR",
                        help="Output directory. Default: modules/{layer_lower}/{id}/")
    parser.add_argument("--tier", type=int, default=3, choices=[1,2,3,4,5],
                        help="Tier: 1=CRITICAL 2=CORE 3=SUPPORTING 4=SPECIALIZED 5=EXTENDED")
    parser.add_argument("--tags", nargs="*", metavar="TAG", default=[],
                        help="Tags for framework.yaml registration.")
    parser.add_argument("--build-targets", nargs="*", default=["ALL"],
                        metavar="TARGET",
                        choices=["ALL","Web","API-Service","CLI","Mobile","Desktop",
                                 "Library-Package","Extension-Plugin","Data-Pipeline",
                                 "AI-Agent","Game","IoT-Embedded"],
                        help="Build targets. Default: ALL")
    parser.add_argument("--anti-activators", nargs="*", default=[], metavar="PHRASE",
                        help="Anti-activation phrases.")
    parser.add_argument("--register", action="store_true",
                        help="Also register the module in framework.yaml via framework-register.py.")
    parser.add_argument("--depends-on", nargs="*", default=[], metavar="MODULE_ID",
                        help="Module IDs this module depends on (for --register).")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing files (destructive).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be created; write nothing.")

    args = parser.parse_args()

    if len(args.description) < 20:
        print("ERROR: --description must be ≥20 characters (lint_prompts gate requirement).",
              file=sys.stderr)
        sys.exit(1)

    # Resolve output path
    out_path = args.path or os.path.join("modules", args.layer.lower(), args.id)
    out_path = out_path.rstrip("/\\") + os.sep

    print(f"Scaffolding module '{args.id}' ({args.layer}) -> {out_path}")

    entry = scaffold(
        module_id=args.id,
        layer=args.layer,
        path=out_path,
        tier=args.tier,
        description=args.description,
        activators=args.activators,
        anti_activators=args.anti_activators,
        tags=args.tags,
        build_targets=args.build_targets,
        dry_run=args.dry_run,
    )

    # Optionally register in framework.yaml
    if args.register and not args.dry_run:
        register_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "framework-register.py"
        )
        import subprocess
        cmd = [
            sys.executable, register_script, "register",
            "--id", args.id,
            "--layer", args.layer,
            "--path", out_path,
            "--tier", str(args.tier),
        ]
        if args.tags:
            cmd += ["--tags", ",".join(args.tags)]
        if args.depends_on:
            cmd += ["--depends-on", ",".join(args.depends_on)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"WARNING: framework-register.py failed: {result.stderr.strip()}")
            print("Run manually: python .wabblespec/engine/shared/scripts/framework-register.py register ...")

    print()
    print(f"Done. Next steps:")
    print(f"  1. Fill in SKILL.md — replace [TODO] sections with actual behavior")
    print(f"  2. Fill in skill-rules.json — set authority.owns and authority.reads")
    print(f"  3. Fill in tests/acceptance.md — add real acceptance gates")
    print(f"  4. Run: python .wabblespec/engine/shared/scripts/quality-floor-check.py --module {args.id}")
    if not args.register:
        print(f"  5. Register: python .wabblespec/engine/shared/scripts/framework-register.py register --id {args.id} --layer {args.layer}")

    sys.exit(0)


if __name__ == "__main__":
    main()
