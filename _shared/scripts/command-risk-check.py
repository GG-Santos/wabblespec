"""
command-risk-check.py — Classify shell commands against the WabbleSpec command risk policy.

Replaces Claude reading _shared/references/command-risk-policy.md (~2,225 tokens) on every
Guard invocation. The full policy is embedded as a classification table. The file is never
read; this script is the authoritative runtime implementation of the policy.

Usage:
    # Classify one or more commands (human-readable):
    python _shared/scripts/command-risk-check.py \\
        --commands "git add -A" "git push --force" "npm run build"

    # JSON output (for guard-check.py or CI):
    python _shared/scripts/command-risk-check.py \\
        --commands "git push --force" "curl http://api.example.com" \\
        --json

    # Read commands from a wave plan file (extracts bash_command fields):
    python _shared/scripts/command-risk-check.py \\
        --from-wave-plan .wabblespec/plans/wave-current.md

    # Stdin mode (one command per line):
    echo "git push --force" | python _shared/scripts/command-risk-check.py --stdin

Policy rules embedded from _shared/references/command-risk-policy.md:
    SAFE   Read-only, dry-run, or temp-scoped. No annotation required.
    WARN   Potentially destructive. Requires rationale annotation in wave plan step.
    BLOCK  Irreversible or high blast-radius. Aborts wave; requires human attestation.

SAFE exception rule: A SAFE match terminates classification for that command even if a
BLOCK or WARN pattern also matches. SAFE patterns are evaluated first.

Exit codes:
    0  All commands are SAFE or WARN — wave may proceed
    1  At least one command is BLOCK — wave must be aborted
    2  Parse error or missing input
"""

import sys
import os
import re
import json
import argparse

# ---------------------------------------------------------------------------
# Classification rules
# Each entry: (pattern_fn, verdict, safer_alternative_or_None)
# pattern_fn receives the full command string (lower-cased, stripped).
# Rules are evaluated in order: first match wins within each tier bucket.
# SAFE bucket is evaluated first (per policy SAFE exception rule).
# ---------------------------------------------------------------------------

def _cmd(s):
    """Normalize command string for matching."""
    return s.lower().strip()


def _has(cmd, *substrings):
    return any(s in cmd for s in substrings)


def _starts(cmd, *prefixes):
    return any(cmd.startswith(p) for p in prefixes)


def _re(cmd, pattern):
    return bool(re.search(pattern, cmd))


# ---------------------------------------------------------------------------
# SAFE rules — evaluated first; a SAFE match wins immediately.
# ---------------------------------------------------------------------------

SAFE_RULES = [
    # --- Git: safe reads and non-destructive ops ---
    (lambda c: _re(c, r"^git\s+log\b"),                          "Read-only git log"),
    (lambda c: _re(c, r"^git\s+status\b"),                       "Read-only git status"),
    (lambda c: _re(c, r"^git\s+diff\b"),                         "Read-only git diff"),
    (lambda c: _re(c, r"^git\s+show\b"),                         "Read-only git show"),
    (lambda c: _re(c, r"^git\s+fetch\b"),                        "Remote read; no local ref change"),
    (lambda c: _re(c, r"^git\s+branch\s+-m\b"),                  "Rename only; no deletion"),
    (lambda c: _re(c, r"^git\s+checkout\s+-b\b"),                "Branch creation; no work destruction"),
    (lambda c: _re(c, r"^git\s+checkout\s+--orphan\b"),          "Orphan branch; no work destruction"),
    (lambda c: _re(c, r"^git\s+restore\s+(-S\b|--staged\b)"),   "Index only; working tree unchanged"),
    (lambda c: _re(c, r"^git\s+clean\s+.*(-n\b|--dry-run\b)"),  "Preview only; no deletion"),
    (lambda c: _re(c, r"^git\s+stash\s+list\b"),                 "Read-only stash list"),
    # git push without --force or --force-with-lease is safe
    (lambda c: _re(c, r"^git\s+push\b") and
               not _has(c, "--force", "-f", "--force-with-lease"), "Normal publish"),
    # git add/commit (no --amend) are safe
    (lambda c: _re(c, r"^git\s+add\b"),                          "Staging files"),
    (lambda c: _re(c, r"^git\s+commit\b") and "--amend" not in c, "Standard commit"),
    (lambda c: _re(c, r"^git\s+(pull|merge|tag|stash\s+pop|stash\s+apply|stash\s+show)\b"),
                                                                  "Non-destructive git op"),
    (lambda c: _re(c, r"^git\s+(init|clone|remote|config|describe|rev-parse|shortlog|blame|bisect)\b"),
                                                                  "Non-destructive git op"),

    # --- Filesystem: read-only ---
    (lambda c: _re(c, r"^(ls|dir|find|cat|head|tail|wc|stat|file|du|df|tree)\b"),
                                                                  "Read-only filesystem"),
    (lambda c: _re(c, r"^mkdir\b"),                               "Additive only"),
    (lambda c: _re(c, r"^cp\b") and not _has(c, "-r ", "-R "),   "Single-file copy; low blast radius"),
    # rm targeting temp paths is safe
    (lambda c: _re(c, r"^rm\b") and _has(c, "/tmp/", "$tmpdir/", ".wabblespec/tmp/", "\\tmp\\"),
                                                                  "Scoped to temp path"),
    (lambda c: _re(c, r"^rm\s+.*-ri?\b"),                        "Interactive mode; user confirms"),

    # --- Database: read-only ---
    (lambda c: _re(c, r"^\s*(select|explain|show|describe)\b"),   "Read-only SQL"),
    (lambda c: _has(c, "--dry-run", "--pretend") and
               _has(c, "migrate", "migration", "alembic", "flyway"), "Migration preview"),

    # --- Process/Network: safe checks ---
    (lambda c: _re(c, r"^kill\s+-0\b"),                           "Existence check; no signal sent"),
    (lambda c: _has(c, "--dry-run") or _has(c, "--spider"),       "Dry-run; no side effects"),
    (lambda c: _re(c, r"^(ping|nslookup|dig|host|traceroute)\b"), "Read-only network check"),
    (lambda c: _re(c, r"^curl\b") and _has(c, "localhost", "127.0.0.1", "::1"),
                                                                  "Localhost curl; no external state"),

    # --- Build: safe runners ---
    (lambda c: _re(c, r"^npm\s+ci\b"),                            "Clean install; reproducible"),
    (lambda c: _re(c, r"^(python|python3|node|pytest|jest|cargo\s+test|go\s+test)\b") and
               not _has(c, "rm", "delete", "drop", "truncate"),   "Test/build runner"),
    (lambda c: _re(c, r"^(echo|printf|pwd|whoami|env|which|type|date|uname)\b"),
                                                                  "Introspection only"),
]


# ---------------------------------------------------------------------------
# BLOCK rules — checked after SAFE; these abort the wave.
# ---------------------------------------------------------------------------

BLOCK_RULES = [
    # --- Git: irreversible ---
    (lambda c: _re(c, r"^git\s+push\b") and _re(c, r"(--force\b|-f\b)") and
               "--force-with-lease" not in c,
     "Use --force-with-lease to check concurrent pushes"),
    (lambda c: _re(c, r"^git\s+reset\s+--hard\b"),
     "Use git stash or git reset --soft to preserve work"),
    (lambda c: _re(c, r"^git\s+(checkout|restore)\b") and
               _re(c, r"\s--\s") and "--staged" not in c and "-S" not in c,
     "Use git stash to save changes first"),
    (lambda c: _re(c, r"^git\s+clean\b") and _has(c, "-fd", "-fx", "-fdx") and
               "--dry-run" not in c and "-n" not in c,
     "Run git clean --dry-run first to preview"),
    (lambda c: _re(c, r"^git\s+branch\s+-D\b"),
     "Use git branch -d (with merge check) or verify work is preserved"),
    (lambda c: _re(c, r"^git\s+(filter-branch|filter-repo)\b"),
     "Requires out-of-band human approval; not a wave operation"),

    # --- Filesystem: high blast radius ---
    (lambda c: _re(c, r"^rm\b") and _has(c, "-rf", "-fr") and
               _has(c, " /", " ~", "$home", " ."),
     "Never rm -rf project root or home; scope to a specific subdirectory"),
    (lambda c: _re(c, r"^(shred|wipe|srm)\b"),
     "Secure deletion is unrecoverable; not a valid wave operation"),

    # --- Database: data loss ---
    (lambda c: _re(c, r"\bdrop\s+(table|database|schema|index)\b"),
     "Verify backup exists; use two-phase migration: deprecate first, drop later"),
    (lambda c: _re(c, r"\bdelete\s+from\b") and "where" not in c,
     "Add a WHERE clause; use TRUNCATE only with explicit attestation"),
    (lambda c: _re(c, r"\btruncate\s+(table\s+)?\w+"),
     "Require explicit attestation outside the wave"),
    (lambda c: _re(c, r"\balter\s+table\b") and _re(c, r"\bdrop\s+column\b"),
     "Use two-phase migration: mark deprecated, then drop in a later wave"),

    # --- Process: unscoped kill ---
    (lambda c: _re(c, r"^kill\s+-9\b") or _re(c, r"^kill\s+-sigkill\b"),
     "Use SIGTERM first and wait for graceful exit"),
    (lambda c: _re(c, r"^killall\b"),
     "Use pkill with -n (newest) or PID-targeted kill"),
    (lambda c: _re(c, r"^curl\b") and _re(c, r"(login|auth|token|oauth|session)"),
     "Require human review before any auth endpoint call in wave"),
]


# ---------------------------------------------------------------------------
# WARN rules — checked after SAFE and BLOCK; everything else defaults WARN.
# ---------------------------------------------------------------------------

WARN_RULES = [
    # --- Git ---
    (lambda c: _re(c, r"^git\s+push\b") and "--force-with-lease" in c,
     "State which branch and why force is needed"),
    (lambda c: _re(c, r"^git\s+stash\s+(drop|clear)\b"),
     "Confirm stash content is already applied or not needed"),
    (lambda c: _re(c, r"^git\s+branch\s+-d\b"),
     "Confirm branch is merged or work is preserved"),
    (lambda c: _re(c, r"^git\s+clean\s+-f\b") and not _has(c, "-d", "-fd"),
     "Confirm files are generated/temporary"),
    (lambda c: _re(c, r"^git\s+rebase\b") and "--abort" not in c,
     "Confirm no upstream consumers"),
    (lambda c: _re(c, r"^git\s+commit\b") and "--amend" in c,
     "Confirm commit not yet pushed"),

    # --- Filesystem ---
    (lambda c: _re(c, r"^rm\b") and not _has(c, "-r", "-R") and not _has(c, "-rf", "-fr"),
     "Confirm file is generated or expendable"),
    (lambda c: _re(c, r"^rm\b") and _re(c, r"(-r\b|-R\b)") and
               not _has(c, "/tmp/", "$tmpdir/", ".wabblespec/tmp/"),
     "Confirm path is a generated output directory"),
    (lambda c: _re(c, r"^mv\b"),
     "Confirm destination and rollback path"),
    (lambda c: _re(c, r"^(cp\s+.*-r\b|cp\s+.*-R\b)"),
     "Confirm scope; large recursive copies have blast radius"),
    (lambda c: _re(c, r"^chmod\b"),
     "Confirm scope and reversibility"),
    (lambda c: _re(c, r"^truncate\b") or (">" in c and _re(c, r"\s>\s+\S+")),
     "Confirm file is not a source artifact"),

    # --- Database: additive DDL ---
    (lambda c: _re(c, r"\balter\s+table\b") and _re(c, r"\badd\s+(column\b|constraint\b)"),
     "Confirm migration is reversible (has down migration)"),
    (lambda c: _re(c, r"\bcreate\s+(table|index)\b"),
     "Confirm down migration exists"),
    (lambda c: _re(c, r"\binsert\s+into\b"),
     "Confirm idempotent (no duplicate risk)"),
    (lambda c: _re(c, r"\bupdate\b") and "where" in c,
     "Confirm scope of affected rows"),

    # --- Network ---
    (lambda c: _re(c, r"^curl\b") and not _has(c, "localhost", "127.0.0.1", "::1"),
     "Confirm endpoint, payload, and idempotency"),
    (lambda c: _re(c, r"^wget\b"),
     "Confirm source and intent"),

    # --- Process ---
    (lambda c: _re(c, r"^kill\b"),
     "Confirm process identity and restart plan"),
    (lambda c: _re(c, r"^pkill\b"),
     "Confirm pattern scope"),

    # --- Package managers ---
    (lambda c: _re(c, r"^(npm|pip|pip3|yarn|pnpm)\s+(install|add)\b"),
     "Confirm package names are correct and pinned"),
    (lambda c: _re(c, r"^(npx|uvx|pipx)\b"),
     "External download; confirm package and source"),
]


# ---------------------------------------------------------------------------
# Classify a single command string
# Returns: {"command": str, "verdict": str, "reason": str, "safer_alternative": str|None}
# ---------------------------------------------------------------------------

def classify(command):
    c = _cmd(command)

    # Check for shell variables / unresolved wildcards in non-read positions
    # If the command would otherwise be WARN or BLOCK, escalate to BLOCK
    has_unresolved = _re(c, r"\$[a-z_][a-z0-9_]*") and not _re(c, r"^(echo|printf|env)\b")

    # 1. SAFE first
    for fn, reason in SAFE_RULES:
        try:
            if fn(c):
                return {
                    "command": command,
                    "verdict": "SAFE",
                    "reason": reason,
                    "safer_alternative": None,
                    "annotation_required": False,
                }
        except Exception:
            continue

    # 2. BLOCK
    for fn, safer in BLOCK_RULES:
        try:
            if fn(c):
                return {
                    "command": command,
                    "verdict": "BLOCK",
                    "reason": "Irreversible or high blast-radius operation",
                    "safer_alternative": safer,
                    "annotation_required": True,
                }
        except Exception:
            continue

    # 3. WARN
    for fn, annotation in WARN_RULES:
        try:
            if fn(c):
                verdict = "BLOCK" if has_unresolved else "WARN"
                return {
                    "command": command,
                    "verdict": verdict,
                    "reason": annotation,
                    "safer_alternative": "Resolve variables before running" if has_unresolved else None,
                    "annotation_required": True,
                }
        except Exception:
            continue

    # 4. Default — unrecognized command → WARN with uncertain note
    return {
        "command": command,
        "verdict": "WARN",
        "reason": "Unrecognized command pattern — classification uncertain",
        "safer_alternative": None,
        "annotation_required": True,
    }


def overall_verdict(results):
    verdicts = {r["verdict"] for r in results}
    if "BLOCK" in verdicts:
        return "BLOCK"
    if "WARN" in verdicts:
        return "WARN"
    return "SAFE"


# ---------------------------------------------------------------------------
# Wave-plan extraction — scans for lines like:
#   bash_command: git add -A
#   `git push --force`
#   $ npm run build
# ---------------------------------------------------------------------------

WAVE_PLAN_PATTERNS = [
    re.compile(r"^bash_command:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^`(.+)`\s*$"),
    re.compile(r"^\$\s+(.+)$"),
    re.compile(r"^\s{4,}(git|npm|pip|python|python3|rm|mv|cp|curl|wget|kill|node|npx)\b(.*)$"),
]


def extract_from_wave_plan(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"ERROR: Cannot read wave plan {path}: {e}", file=sys.stderr)
        sys.exit(2)

    commands = []
    for line in lines:
        stripped = line.rstrip()
        for pat in WAVE_PLAN_PATTERNS:
            m = pat.match(stripped)
            if m:
                cmd = m.group(1).strip()
                if cmd:
                    commands.append(cmd)
                break
    return commands


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

VERDICT_WIDTH = 5  # SAFE / WARN / BLOCK


def print_results(results):
    for r in results:
        verdict = r["verdict"]
        cmd_display = r["command"][:60]
        alt = f"  -- {r['safer_alternative']}" if r["safer_alternative"] else ""
        reason_display = f"  ({r['reason']})" if r["verdict"] != "SAFE" else ""
        print(f"  {verdict:<5}  {cmd_display}{reason_display}{alt}")
    print()
    ov = overall_verdict(results)
    print(f"Overall: {ov}")
    if ov == "BLOCK":
        print("  Wave must be aborted. Resolve BLOCK commands before proceeding.")
    elif ov == "WARN":
        print("  Wave may proceed. Add rationale annotations for WARN commands.")


def print_json(results):
    blocking = [r for r in results if r["verdict"] == "BLOCK"]
    warnings = [r for r in results if r["verdict"] == "WARN"]
    out = {
        "overall": overall_verdict(results),
        "commands": results,
        "blocking_count": len(blocking),
        "warning_count": len(warnings),
    }
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Classify shell commands against the WabbleSpec command risk policy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--commands", nargs="+", metavar="CMD",
                       help="One or more shell commands to classify.")
    group.add_argument("--from-wave-plan", metavar="PATH",
                       help="Extract commands from a wave plan markdown file.")
    group.add_argument("--stdin", action="store_true",
                       help="Read commands from stdin, one per line.")
    parser.add_argument("--json", action="store_true", dest="emit_json",
                        help="Emit JSON output instead of human-readable.")

    args = parser.parse_args()

    # Collect commands
    if args.commands:
        commands = args.commands
    elif args.from_wave_plan:
        commands = extract_from_wave_plan(args.from_wave_plan)
        if not commands:
            print(f"No commands found in {args.from_wave_plan}")
            sys.exit(0)
    else:  # stdin
        commands = [line.rstrip("\n") for line in sys.stdin if line.strip()]

    if not commands:
        print("No commands to classify.", file=sys.stderr)
        sys.exit(2)

    results = [classify(cmd) for cmd in commands]

    if args.emit_json:
        print_json(results)
    else:
        print_results(results)

    ov = overall_verdict(results)
    sys.exit(0 if ov in ("SAFE", "WARN") else 1)


if __name__ == "__main__":
    main()
