"""
wave-plan-writer.py — Write a conforming current-wave-plan.md from CLI arguments.

Eliminates manual Markdown construction for Decompose. Claude provides the
reasoning-dependent content (wave names, checkpoints, verification commands);
this script handles structure, required fields, and Markdown serialization.

Usage:
    python .wabblespec/engine/shared/scripts/wave-plan-writer.py \\
        --session-id phase3-new-scripts-20260528 \\
        --target Library-Package \\
        --complexity Medium \\
        --generated-at 2026-05-28T13:00:00Z \\
        --wave '{"name":"Audit and contract file","inputs":["task-card.md"],"outputs":["script-delegation-contract.md"],"checkpoint":"Contract exists with all 4 scripts","rollback_to":null,"verification_mode":"Audit","verification_command":"python -c \\"print(\\'PASS\\')\\""}' \\
        --wave '{"name":"Rewrite SKILL.md files","inputs":["Wave 1 outputs"],"outputs":["6 SKILL.md files"],"checkpoint":"All skills have script calls","rollback_to":"Wave 1 checkpoint","verification_mode":"Audit","verification_command":"python -c \\"print(\\'PASS\\')\\""}' \\
        --out .wabblespec/state/plans/current-wave-plan.md

    # Via --waves-file (avoids shell quoting issues with complex verification_command):
    python .wabblespec/engine/shared/scripts/wave-plan-writer.py \\
        --session-id my-session \\
        --target Library-Package \\
        --complexity Low \\
        --waves-file /tmp/waves.json \\
        --out .wabblespec/state/plans/current-wave-plan.md

    waves.json format: JSON array of wave objects (same schema as --wave).

    # Dry run:
    python .wabblespec/engine/shared/scripts/wave-plan-writer.py ... --dry-run

Wave JSON fields (all required unless noted):
    name                string — wave label
    inputs              list[string] — input file paths or descriptions
    outputs             list[string] — expected output paths
    checkpoint          string — condition that must be true before next wave
    rollback_to         string|null — "null" or "Wave N checkpoint"
    verification_mode   string — Test|Audit|Observation|Review|Attestation|Measurement|Demonstration
    verification_command string — exact shell command that proves the checkpoint

Exit codes:
    0  success
    1  validation failure
    2  output path not writable
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

VALID_COMPLEXITY = {"Low", "Medium", "High"}
VALID_MODES = {"Test", "Audit", "Observation", "Review", "Attestation",
               "Measurement", "Demonstration"}
WAVE_REQUIRED = ("name", "inputs", "outputs", "checkpoint",
                 "rollback_to", "verification_mode", "verification_command")


def parse_wave(raw, index):
    """Parse a JSON wave spec. Returns dict or raises ValueError."""
    try:
        w = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Wave {index+1}: invalid JSON — {e}")
    missing = [f for f in WAVE_REQUIRED if f not in w]
    if missing:
        raise ValueError(f"Wave {index+1}: missing required fields: {missing}")
    if w["verification_mode"] not in VALID_MODES:
        raise ValueError(
            f"Wave {index+1}: verification_mode '{w['verification_mode']}' not in {VALID_MODES}"
        )
    return w


def render(args, waves):
    lines = [
        "# Wave Plan",
        "",
        f"**task_card:** .wabblespec/state/plans/task-card.md",
        f"**target:** {args.target}",
        f"**complexity:** {args.complexity}",
        f"**collapse_eligible:** {str(args.collapse_eligible).lower()}",
        f"**session_id:** {args.session_id}",
        f"**generated_at:** {args.generated_at}",
        "",
        "## Waves",
        "",
    ]

    prev_label = None
    for i, w in enumerate(waves):
        n = i + 1
        inputs_str = ", ".join(w["inputs"]) if isinstance(w["inputs"], list) else w["inputs"]
        outputs_str = ", ".join(w["outputs"]) if isinstance(w["outputs"], list) else w["outputs"]
        rollback = w["rollback_to"] if w["rollback_to"] and w["rollback_to"] != "null" else "null"

        lines += [
            f"### Wave {n}: {w['name']}",
            "",
            f"**inputs:** [{inputs_str}]",
            f"**outputs:** [{outputs_str}]",
            f"**checkpoint:** {w['checkpoint']}",
            f"**verification_command:** `{w['verification_command']}`",
            f"**rollback_to:** {rollback}",
            f"**verification_mode:** {w['verification_mode']}",
            "",
            "---",
            "",
        ]
        prev_label = w["name"]

    lines += ["## Rollback Map", ""]
    lines.append("| Wave | Rollback target | Trigger condition |")
    lines.append("|---|---|---|")
    for i, w in enumerate(waves):
        n = i + 1
        rollback = w["rollback_to"] if w["rollback_to"] and w["rollback_to"] != "null" else \
            f"null (Wave {n} — no prior checkpoint)"
        lines.append(
            f"| Wave {n} fails | {rollback} | "
            "HARD error or BLOCKED after 3 REVISE cycles |"
        )

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--complexity", required=True, choices=list(VALID_COMPLEXITY))
    parser.add_argument("--collapse-eligible", action="store_true", default=False,
                        dest="collapse_eligible")
    parser.add_argument("--generated-at", default=NOW, dest="generated_at")
    parser.add_argument("--wave", action="append", default=[], metavar="JSON",
                        help="Repeatable. JSON object per wave. "
                             "Mutually exclusive with --waves-file.")
    parser.add_argument("--waves-file", metavar="PATH",
                        help="Path to a JSON file containing an array of wave objects. "
                             "Use instead of --wave to avoid shell quoting issues with "
                             "complex verification_command strings.")
    parser.add_argument("--out", required=True, metavar="PATH")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    errors = []
    if args.wave and args.waves_file:
        errors.append("--wave and --waves-file are mutually exclusive.")
    elif not args.wave and not args.waves_file:
        errors.append("At least one --wave or --waves-file is required.")

    waves = []
    if args.waves_file and not errors:
        try:
            with open(args.waves_file, encoding="utf-8") as fh:
                raw_waves = json.load(fh)
            if not isinstance(raw_waves, list):
                errors.append("--waves-file must contain a JSON array.")
            else:
                for i, w in enumerate(raw_waves):
                    try:
                        waves.append(parse_wave(json.dumps(w), i))
                    except ValueError as e:
                        errors.append(str(e))
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"--waves-file: {e}")
    else:
        for i, raw in enumerate(args.wave):
            try:
                waves.append(parse_wave(raw, i))
            except ValueError as e:
                errors.append(str(e))

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    content = render(args, waves)

    if args.dry_run or args.out == "-":
        print(content, end="")
        return

    try:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"Wrote {args.out}")
    except OSError as e:
        print(f"ERROR: Cannot write to {args.out}: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
