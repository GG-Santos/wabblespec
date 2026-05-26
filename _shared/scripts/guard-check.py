"""
guard-check.py — Automate Guard Layers 4 and 5 without loading framework context.

Replaces Claude reading skill-rules.json (~1–2 KB) and manually resolving glob patterns
for Layer 4 (authority), plus invoking command-risk-check for Layer 5 (command risk).

Saves ~2,500–3,500 tokens per Guard invocation.

Does NOT replace Guard Layers 1–3 (schema, scope, invariants) — those require Claude
reasoning about task context. This script handles only the deterministic pattern-matching
layers.

Subcommands:
    authority   Layer 4: confirm module owns the target files (fnmatch against authority.owns)
    commands    Layer 5: classify shell commands via embedded policy
    wave        Layers 4+5 combined — primary entrypoint for pre-wave check

Usage:
    # Layer 4: does the module own the proposed output files?
    python _shared/scripts/guard-check.py authority \\
        --module executor \\
        --files ".wabblespec/receipts/wave-1-receipt.json" \\
                ".wabblespec/checkpoints/cp1.json"

    # Layer 4 with misactivation check (file_path_patterns vs wave input files):
    python _shared/scripts/guard-check.py authority \\
        --module archive \\
        --files ".wabblespec/receipts/archive-receipt-aa.json" \\
        --wave-files "src/foo.ts" ".wabblespec/plans/task-card.md"

    # Layer 5: classify commands only
    python _shared/scripts/guard-check.py commands \\
        --commands "git add -A" "git push --force"

    # Combined wave check (most common use):
    python _shared/scripts/guard-check.py wave \\
        --module executor \\
        --files ".wabblespec/receipts/execution-receipt.json" \\
        --commands "git add -A" "python _shared/scripts/validate-graph.py" \\
        --json

    # Explicit path to skill-rules.json (auto-discovered if omitted):
    python _shared/scripts/guard-check.py authority \\
        --module guard \\
        --files ".wabblespec/receipts/guard-wave-1-receipt.json" \\
        --rules-file modules/l2/guard/skill-rules.json

Exit codes:
    0  PASS (all layers clear)
    1  FAIL or BLOCK (authority violation or blocked command)
    2  Module not found / skill-rules.json missing / parse error
"""

import sys
import os
import re
import json
import fnmatch
import argparse
import subprocess

# Import command-risk-check from the same scripts directory.
# Falls back to subprocess if import fails (e.g., different working dir).
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_command_risk():
    """Import classify() from command-risk-check.py in the same directory."""
    import importlib.util
    crc_path = os.path.join(_SCRIPT_DIR, "command-risk-check.py")
    if not os.path.isfile(crc_path):
        return None
    spec = importlib.util.spec_from_file_location("command_risk_check", crc_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CRC = _import_command_risk()


# ---------------------------------------------------------------------------
# Module discovery
# ---------------------------------------------------------------------------

def find_repo_root(start=None):
    """Walk up from start looking for framework.yaml or .wabblespec/."""
    candidate = start or os.getcwd()
    for _ in range(12):
        if (os.path.isfile(os.path.join(candidate, "framework.yaml")) or
                os.path.isdir(os.path.join(candidate, ".wabblespec"))):
            return candidate
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def find_rules_file(module_id, repo_root):
    """
    Search for skill-rules.json by module id.
    Tries modules/<layer>/<id>/skill-rules.json for each known layer.
    Returns the first match or None.
    """
    layers = ["l0", "l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8"]
    for layer in layers:
        path = os.path.join(repo_root, "modules", layer, module_id, "skill-rules.json")
        if os.path.isfile(path):
            return path
    # Also try a flat modules/<id>/skill-rules.json
    path = os.path.join(repo_root, "modules", module_id, "skill-rules.json")
    if os.path.isfile(path):
        return path
    return None


def load_rules(rules_file):
    try:
        with open(rules_file, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {rules_file}: {e}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------------
# Layer 4 — Authority check
# ---------------------------------------------------------------------------

def check_authority(rules, proposed_files, wave_files=None):
    """
    Returns a Layer 4 report dict:
    {
        "verdict": "PASS" | "FAIL",
        "owns": [...],           # authority.owns patterns from rules
        "unauthorized_files": [...],   # files not matched by any owns pattern
        "misactivation_risk": bool,    # True if file_path_patterns non-empty and no wave_files match
        "details": str
    }
    """
    owns_patterns = rules.get("authority", {}).get("owns", [])
    file_path_patterns = rules.get("file_path_patterns", [])

    unauthorized = []
    for f in proposed_files:
        # Normalize path separators for matching
        f_normalized = f.replace("\\", "/")
        matched = False
        for pat in owns_patterns:
            pat_normalized = pat.replace("\\", "/")
            if fnmatch.fnmatch(f_normalized, pat_normalized):
                matched = True
                break
        if not matched:
            unauthorized.append(f)

    # Misactivation check: if module has file_path_patterns declared,
    # at least one wave input file should match at least one pattern.
    misactivation_risk = False
    if file_path_patterns and wave_files is not None and len(wave_files) > 0:
        any_match = False
        for wf in wave_files:
            wf_normalized = wf.replace("\\", "/")
            for pat in file_path_patterns:
                pat_normalized = pat.replace("\\", "/")
                if fnmatch.fnmatch(wf_normalized, pat_normalized):
                    any_match = True
                    break
            if any_match:
                break
        misactivation_risk = not any_match

    verdict = "FAIL" if unauthorized else "PASS"
    if misactivation_risk:
        verdict = "FAIL"

    details_parts = []
    if unauthorized:
        details_parts.append(
            f"Module '{rules.get('module')}' does not own: {unauthorized}. "
            f"authority.owns = {owns_patterns}"
        )
    if misactivation_risk:
        details_parts.append(
            f"Misactivation risk: file_path_patterns {file_path_patterns} "
            f"matched none of wave files {wave_files}"
        )

    return {
        "verdict": verdict,
        "owns": owns_patterns,
        "unauthorized_files": unauthorized,
        "misactivation_risk": misactivation_risk,
        "details": "; ".join(details_parts) if details_parts else "All files authorized.",
    }


# ---------------------------------------------------------------------------
# Layer 5 — Command risk
# ---------------------------------------------------------------------------

def check_commands(commands):
    """
    Returns a Layer 5 report dict:
    {
        "verdict": "PASS" | "WARN" | "BLOCK",
        "results": [...],         # per-command classification
        "blocking_commands": [...],
        "warning_commands": [...],
    }
    """
    if not _CRC:
        # Fallback: call as subprocess
        return _check_commands_subprocess(commands)

    results = [_CRC.classify(cmd) for cmd in commands]
    overall = _CRC.overall_verdict(results)

    blocking = [r for r in results if r["verdict"] == "BLOCK"]
    warnings = [r for r in results if r["verdict"] == "WARN"]

    # Normalize verdict for guard output: SAFE/WARN both map to PASS for Layer 5
    # BLOCK maps to BLOCK (hard fail).
    verdict = "BLOCK" if blocking else ("WARN" if warnings else "PASS")

    return {
        "verdict": verdict,
        "results": results,
        "blocking_commands": blocking,
        "warning_commands": warnings,
    }


def _check_commands_subprocess(commands):
    """Fallback: invoke command-risk-check.py as subprocess."""
    crc_path = os.path.join(_SCRIPT_DIR, "command-risk-check.py")
    if not os.path.isfile(crc_path):
        return {
            "verdict": "WARN",
            "results": [],
            "blocking_commands": [],
            "warning_commands": [],
            "error": "command-risk-check.py not found; command classification skipped",
        }

    try:
        proc = subprocess.run(
            [sys.executable, crc_path, "--json", "--commands"] + list(commands),
            capture_output=True, text=True
        )
        data = json.loads(proc.stdout)
        verdict = "BLOCK" if data.get("blocking_count", 0) > 0 else (
            "WARN" if data.get("warning_count", 0) > 0 else "PASS"
        )
        return {
            "verdict": verdict,
            "results": data.get("commands", []),
            "blocking_commands": [r for r in data.get("commands", []) if r["verdict"] == "BLOCK"],
            "warning_commands": [r for r in data.get("commands", []) if r["verdict"] == "WARN"],
        }
    except Exception as e:
        return {
            "verdict": "WARN",
            "results": [],
            "blocking_commands": [],
            "warning_commands": [],
            "error": f"command-risk-check subprocess failed: {e}",
        }


# ---------------------------------------------------------------------------
# Combined wave check
# ---------------------------------------------------------------------------

def check_wave(rules, proposed_files, commands, wave_files=None):
    """
    Run Layers 4+5 together.
    Returns combined report dict.
    """
    l4 = check_authority(rules, proposed_files, wave_files) if proposed_files else {
        "verdict": "PASS",
        "owns": rules.get("authority", {}).get("owns", []),
        "unauthorized_files": [],
        "misactivation_risk": False,
        "details": "No files to check.",
    }

    l5 = check_commands(commands) if commands else {
        "verdict": "PASS",
        "results": [],
        "blocking_commands": [],
        "warning_commands": [],
    }

    # Overall: BLOCK if either layer fails
    if l4["verdict"] == "FAIL" or l5["verdict"] == "BLOCK":
        overall = "FAIL"
    elif l5["verdict"] == "WARN":
        overall = "WARN"
    else:
        overall = "PASS"

    return {
        "module": rules.get("module"),
        "layer_4": l4,
        "layer_5": l5,
        "overall": overall,
    }


# ---------------------------------------------------------------------------
# Human-readable output
# ---------------------------------------------------------------------------

def print_authority_report(report, module_id):
    verdict = report["verdict"]
    print(f"\nLayer 4 (Authority) — module: {module_id}")
    print(f"  Verdict: {verdict}")
    if report["unauthorized_files"]:
        print(f"  Unauthorized files: {report['unauthorized_files']}")
    if report["misactivation_risk"]:
        print("  Misactivation risk: YES — file_path_patterns matched no wave input files")
    if verdict == "PASS":
        print("  All proposed output files are within module authority.")


def print_commands_report(report):
    print("\nLayer 5 (Command Risk)")
    print(f"  Verdict: {report['verdict']}")
    for r in report.get("results", []):
        ann = " [annotation required]" if r.get("annotation_required") else ""
        alt = f"  -- safer: {r['safer_alternative']}" if r.get("safer_alternative") else ""
        print(f"    {r['verdict']:<5}  {r['command'][:60]}{ann}{alt}")
    if report.get("error"):
        print(f"  Warning: {report['error']}")


def print_wave_report(report):
    print(f"\nWave guard check — module: {report['module']}")
    print(f"Overall: {report['overall']}")
    print_authority_report(report["layer_4"], report["module"])
    print_commands_report(report["layer_5"])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Guard Layers 4+5 automation — authority and command risk checks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--rules-file", metavar="PATH",
                        help="Explicit path to skill-rules.json (auto-discovered if omitted).")
    parser.add_argument("--repo-root", metavar="PATH",
                        help="Explicit repo root path (auto-discovered if omitted).")

    sub = parser.add_subparsers(dest="command", required=True)

    # authority
    p_auth = sub.add_parser("authority", help="Layer 4: authority ownership check.")
    p_auth.add_argument("--module", required=True, metavar="MODULE_ID")
    p_auth.add_argument("--files", nargs="+", required=True, metavar="PATH")
    p_auth.add_argument("--wave-files", nargs="*", metavar="PATH",
                        help="Wave input files for misactivation check.")
    p_auth.add_argument("--json", action="store_true", dest="emit_json")

    # commands
    p_cmd = sub.add_parser("commands", help="Layer 5: command risk classification.")
    p_cmd.add_argument("--commands", nargs="+", required=True, metavar="CMD")
    p_cmd.add_argument("--json", action="store_true", dest="emit_json")

    # wave
    p_wave = sub.add_parser("wave", help="Layers 4+5 combined pre-wave check.")
    p_wave.add_argument("--module", required=True, metavar="MODULE_ID")
    p_wave.add_argument("--files", nargs="*", default=[], metavar="PATH",
                        help="Proposed output files (Layer 4).")
    p_wave.add_argument("--wave-files", nargs="*", metavar="PATH",
                        help="Wave input files for misactivation check.")
    p_wave.add_argument("--commands", nargs="*", default=[], metavar="CMD",
                        help="Shell commands to classify (Layer 5).")
    p_wave.add_argument("--json", action="store_true", dest="emit_json")

    args = parser.parse_args()
    if not hasattr(args, "emit_json"):
        args.emit_json = False

    repo_root = args.repo_root or find_repo_root()
    if repo_root is None:
        print("ERROR: Cannot find repo root. Run from inside the project.", file=sys.stderr)
        sys.exit(2)

    # Commands-only subcommand doesn't need a module
    if args.command == "commands":
        report = check_commands(args.commands)
        if args.emit_json:
            print(json.dumps(report, indent=2))
        else:
            print_commands_report(report)
        sys.exit(0 if report["verdict"] != "BLOCK" else 1)

    # Resolve rules file
    rules_file = args.rules_file or find_rules_file(args.module, repo_root)
    if rules_file is None:
        print(f"ERROR: skill-rules.json not found for module '{args.module}'. "
              f"Searched modules/<layer>/{args.module}/skill-rules.json.",
              file=sys.stderr)
        sys.exit(2)
    rules = load_rules(rules_file)

    if args.command == "authority":
        report = check_authority(rules, args.files, getattr(args, "wave_files", None))
        if args.emit_json:
            print(json.dumps(report, indent=2))
        else:
            print_authority_report(report, args.module)
        sys.exit(0 if report["verdict"] == "PASS" else 1)

    elif args.command == "wave":
        report = check_wave(
            rules,
            args.files,
            args.commands,
            getattr(args, "wave_files", None),
        )
        if args.emit_json:
            print(json.dumps(report, indent=2))
        else:
            print_wave_report(report)
        overall = report["overall"]
        sys.exit(0 if overall in ("PASS", "WARN") else 1)


if __name__ == "__main__":
    main()
