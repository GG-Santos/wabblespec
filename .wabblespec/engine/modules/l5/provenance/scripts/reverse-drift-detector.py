#!/usr/bin/env python3
"""
reverse-drift-detector.py

Detects reverse drift: implementation files edited after spec was last updated.
Emits findings in JSON format for receipt integration.

Usage:
    python reverse-drift-detector.py [--wave-plan <path>] [--root <path>]

Exit codes:
    0 — No drift or WARNING-only
    1 — STALENESS_VIOLATION detected
    2 — SPEC_VIOLATION detected
    3 — HARD error (BREAKING spec + reverse drift)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone


SPEC_PATHS = [
    ".wabblespec/plans/task-card.md",
    ".wabblespec/plans/wave-plan.md",
    ".wabblespec/specs",
]

EXEMPT_PATTERNS = [
    "*.generated.*",
    "*.gen.*",
]

HOUR = 3600
DAY = 86400


def find_wabblespec_root(start: Path) -> Path:
    current = start.resolve()
    while current != current.parent:
        if (current / ".wabblespec").exists():
            return current
        current = current.parent
    return start.resolve()


def get_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return 0.0


def get_spec_mtime(root: Path) -> float:
    """Return the most recent mtime of any spec artifact."""
    latest = 0.0
    for spec_rel in SPEC_PATHS:
        spec_path = root / spec_rel
        if spec_path.is_dir():
            for f in spec_path.rglob("*.md"):
                latest = max(latest, get_mtime(f))
        elif spec_path.exists():
            latest = max(latest, get_mtime(spec_path))
    return latest


def is_exempt(path: Path) -> bool:
    name = path.name.lower()
    return any(
        name.endswith(pat.lstrip("*")) or pat.lstrip("*") in name
        for pat in EXEMPT_PATTERNS
    )


def load_wave_plan_targets(wave_plan_path: Path):
    """Extract declared write targets from wave plan. Returns list of paths."""
    if not wave_plan_path.exists():
        return None
    targets = []
    with open(wave_plan_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("- ") and ("project/repo/" in line or "src/" in line):
                # Extract path-like tokens
                for token in line.split():
                    if token.startswith("project/") or token.startswith("src/"):
                        targets.append(token.strip("`").strip())
    return targets if targets else None


def classify_drift(delta_seconds: float, spec_has_breaking: bool) -> str:
    if spec_has_breaking:
        return "HARD"
    if delta_seconds > DAY:
        return "SPEC_VIOLATION"
    if delta_seconds > HOUR:
        return "STALENESS_VIOLATION"
    return "WARNING"


def check_spec_has_breaking(root: Path) -> bool:
    task_card = root / ".wabblespec/plans/task-card.md"
    if not task_card.exists():
        return False
    content = task_card.read_text(encoding="utf-8", errors="replace")
    return "change_class: BREAKING" in content or "delta_class: BREAKING" in content


def scan(root: Path, wave_plan_path: Path | None) -> dict:
    spec_mtime = get_spec_mtime(root)
    if spec_mtime == 0.0:
        return {"status": "NO_SPEC", "findings": [], "exit_code": 0}

    spec_has_breaking = check_spec_has_breaking(root)
    targets = None
    if wave_plan_path:
        targets = load_wave_plan_targets(wave_plan_path)

    repo = root / "project" / "repo"
    if not repo.exists():
        repo = root  # fallback: scan entire root

    findings = []
    worst_severity = None
    severity_order = {"WARNING": 0, "STALENESS_VIOLATION": 1, "SPEC_VIOLATION": 2, "HARD": 3}

    scan_paths = []
    if targets:
        for t in targets:
            p = root / t
            if p.exists():
                scan_paths.append(p)
    else:
        scan_paths = [repo]

    for scan_path in scan_paths:
        if scan_path.is_file():
            files = [scan_path]
        else:
            files = [f for f in scan_path.rglob("*") if f.is_file()]

        for f in files:
            if is_exempt(f):
                continue
            f_mtime = get_mtime(f)
            if f_mtime <= spec_mtime:
                continue
            delta = f_mtime - spec_mtime
            severity = classify_drift(delta, spec_has_breaking)
            finding = {
                "file": str(f.relative_to(root)),
                "file_mtime": datetime.fromtimestamp(f_mtime, tz=timezone.utc).isoformat(),
                "spec_mtime": datetime.fromtimestamp(spec_mtime, tz=timezone.utc).isoformat(),
                "delta_seconds": round(delta),
                "severity": severity,
            }
            findings.append(finding)
            if worst_severity is None or severity_order.get(severity, 0) > severity_order.get(worst_severity, 0):
                worst_severity = severity

    exit_code_map = {"WARNING": 0, "STALENESS_VIOLATION": 1, "SPEC_VIOLATION": 2, "HARD": 3}
    exit_code = exit_code_map.get(worst_severity, 0) if worst_severity else 0

    return {
        "status": worst_severity or "CLEAN",
        "spec_mtime": datetime.fromtimestamp(spec_mtime, tz=timezone.utc).isoformat(),
        "spec_has_breaking_delta": spec_has_breaking,
        "findings_count": len(findings),
        "findings": findings,
        "exit_code": exit_code,
        "scanned_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Detect reverse drift between spec and implementation.")
    parser.add_argument("--wave-plan", help="Path to wave-plan.md for targeted scanning")
    parser.add_argument("--root", help="Project root (default: auto-detect)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    root = Path(args.root) if args.root else find_wabblespec_root(Path.cwd())
    wave_plan_path = Path(args.wave_plan) if args.wave_plan else None

    result = scan(root, wave_plan_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = result["status"]
        count = result["findings_count"]
        print(f"reverse-drift-detector: {status} ({count} findings)")
        for f in result["findings"]:
            print(f"  [{f['severity']}] {f['file']} (+{f['delta_seconds']}s after spec)")

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
