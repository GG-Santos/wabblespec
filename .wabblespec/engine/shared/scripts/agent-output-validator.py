"""
agent-output-validator.py — Validate JSON output from WabbleSpec subagents.

When a skill runs as a Claude Code subagent, its final message is a JSON
receipt. This script validates that JSON against the expected schema for
the skill type before Executor records it.

Usage:
    # Validate inline JSON:
    python .wabblespec/engine/shared/scripts/agent-output-validator.py \\
        --type verifier \\
        --json '{"module":"verifier","wave":1,"verdict":"PASS",...}'

    # Validate from a file:
    python .wabblespec/engine/shared/scripts/agent-output-validator.py \\
        --type guard \\
        --file .wabblespec/state/receipts/agent-output-guard-wave-1.json

    # Extract JSON from a mixed text+JSON agent response:
    python .wabblespec/engine/shared/scripts/agent-output-validator.py \\
        --type verifier \\
        --extract "...prose... ```json {\"verdict\":\"PASS\",...} ```"

Exit codes:
    0  valid
    1  schema violation (printed to stdout with field details)
    2  parse error (invalid JSON or missing required fields at top level)
"""

import sys
import json
import re
import argparse


# ---------------------------------------------------------------------------
# Minimal required fields per agent type
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    "verifier": {
        "module", "wave", "verification_mode", "verdict", "spec_compliance",
        "checks_run", "checks_passed", "status",
    },
    "guard": {
        "module", "wave_id", "layer_1_schema", "layer_2_scope",
        "layer_3_invariants", "layer_4_authority", "layer_5_command_risk",
        "overall", "status",
    },
    "executor": {
        "module", "wave", "status", "files_written", "delta_class", "summary",
    },
    "recipe": {
        "module", "target", "complexity", "confidence", "detection_method", "status",
    },
    "archive": {
        "module", "version_previous", "version_new", "version_bump_reason",
        "receipts_aggregated", "all_waves_passed", "status",
    },
}

VALID_STATUS = {"PASS", "FAIL", "PARTIAL", "BLOCKED"}
VALID_VERDICT = {"PASS", "FAIL", "BLOCKED"}
VALID_OVERALL = {"PASS", "FAIL", "WARN"}


def extract_json(text):
    """Extract first JSON object or array from mixed text."""
    # Try code fence first: ```json ... ```
    m = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
    if m:
        return m.group(1)
    # Try bare JSON object
    m = re.search(r"(\{[\s\S]*\})", text)
    if m:
        return m.group(1)
    return None


def validate(data, agent_type):
    """
    Validate parsed dict against required fields for agent_type.
    Returns list of error strings (empty = valid).
    """
    errors = []
    required = REQUIRED_FIELDS.get(agent_type, set())
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    if "status" in data and data["status"] not in VALID_STATUS:
        errors.append(f"'status' must be one of {VALID_STATUS}, got '{data['status']}'")

    if "verdict" in data and data["verdict"] not in VALID_VERDICT:
        errors.append(f"'verdict' must be one of {VALID_VERDICT}, got '{data['verdict']}'")

    if "overall" in data and data["overall"] not in VALID_OVERALL:
        errors.append(f"'overall' must be one of {VALID_OVERALL}, got '{data['overall']}'")

    # Verifier: FAIL requires non-null fix_recommendation
    if agent_type == "verifier":
        if data.get("verdict") == "FAIL" and not data.get("fix_recommendation"):
            errors.append(
                "verdict=FAIL requires a non-null, non-empty 'fix_recommendation'."
            )

    # Guard: FAIL requires non-empty violations
    if agent_type == "guard":
        if data.get("overall") == "FAIL" and not data.get("violations"):
            errors.append("overall=FAIL requires at least one entry in 'violations'.")

    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--type", required=True,
                        choices=list(REQUIRED_FIELDS.keys()),
                        help="Agent/skill type to validate against.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", metavar="JSON_STRING",
                       help="Inline JSON string to validate.")
    group.add_argument("--file", metavar="PATH",
                       help="Path to JSON file to validate.")
    group.add_argument("--extract", metavar="TEXT",
                       help="Raw agent response text — extracts first JSON block.")
    args = parser.parse_args()

    # Get raw JSON string
    if args.json:
        raw = args.json
    elif args.file:
        try:
            with open(args.file, encoding="utf-8") as fh:
                raw = fh.read()
        except OSError as e:
            print(f"ERROR: Cannot read {args.file}: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        raw = extract_json(args.extract)
        if raw is None:
            print("ERROR: No JSON block found in --extract text.", file=sys.stderr)
            sys.exit(2)

    # Parse
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"PARSE ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(data, dict):
        print("PARSE ERROR: Expected a JSON object (dict), got array or scalar.",
              file=sys.stderr)
        sys.exit(2)

    # Validate
    errors = validate(data, args.type)
    if errors:
        print(f"INVALID ({args.type}):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"VALID ({args.type}) — status={data.get('status', 'unset')}")


if __name__ == "__main__":
    main()
