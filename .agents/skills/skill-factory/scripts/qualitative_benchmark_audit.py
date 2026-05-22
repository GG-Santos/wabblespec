#!/usr/bin/env python3
"""Audit benchmark outputs for qualitative weaknesses structural scoring misses."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


GENERIC_MARKERS = [
    "Create a {title.lower()}",
    "from a messy note",
    "Apply the niche checklist",
    "Fill the contract fields",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def finding(severity: str, code: str, path: Path, message: str) -> dict[str, str]:
    return {"severity": severity, "code": code, "path": str(path), "message": message}


def normalized_role_body(text: str) -> str:
    text = re.sub(r"^---[\s\S]*?---", "", text).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def audit_task(task_dir: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    task = read_json(task_dir / "task.json")
    target = task.get("output_target", {})
    skill_count = int(target.get("skill_count", 1))
    files = [path for path in task_dir.rglob("*") if path.is_file()]
    text_files = [
        path for path in files
        if path.suffix.lower() in {".md", ".txt", ".json", ".py"}
    ]
    combined = "\n\n".join(read_text(path) for path in text_files)

    for marker in GENERIC_MARKERS:
        if marker in combined:
            findings.append(finding("warning", "generic_marker", task_dir, f"Generic marker remains: {marker}"))

    if "## Domain Lens" not in combined:
        findings.append(finding("error", "domain_lens_missing", task_dir, "No domain lens section found."))

    if skill_count > 1:
        for required in ["shared-interface.md", "shared-safety.md", "routing.md"]:
            if not (task_dir / required).is_file():
                findings.append(finding("error", "shared_system_file_missing", task_dir / required, "Missing shared system file."))
        role_bodies = [
            normalized_role_body(read_text(path))
            for path in sorted((task_dir / "skills").glob("skill-*/SKILL.md"))
        ]
        duplicates = sum(count - 1 for count in Counter(role_bodies).values() if count > 1)
        if duplicates:
            findings.append(finding("warning", "duplicated_role_bodies", task_dir, f"{duplicates} duplicate role bodies found."))

    if "mcp" in target.get("folders", []):
        mcp_text = read_text(task_dir / "mcp" / "integration.md")
        for marker in ["## Expected Calls", "audit_domain_lens", "safe_fallback"]:
            if marker not in mcp_text:
                findings.append(finding("error", "mcp_contract_thin", task_dir / "mcp" / "integration.md", f"Missing MCP marker: {marker}"))

    return findings


def audit_dirs(root: Path, task_dirs: list[Path], write_report: bool = False) -> dict[str, Any]:
    task_dirs = sorted(task_dirs)
    findings: list[dict[str, str]] = []
    for task_dir in task_dirs:
        try:
            findings.extend(audit_task(task_dir))
        except Exception as exc:
            findings.append(finding("error", "audit_exception", task_dir, str(exc)))

    counts = Counter(item["severity"] for item in findings)
    code_counts = Counter(item["code"] for item in findings)
    report = {
        "schema_version": "benchmark-qualitative-audit-1.0",
        "root": str(root),
        "tasks": len(task_dirs),
        "valid": counts["error"] == 0,
        "summary": {
            "errors": counts["error"],
            "warnings": counts["warning"],
            "codes": dict(sorted(code_counts.items())),
        },
        "findings": findings[:200],
        "findings_truncated": max(0, len(findings) - 200),
    }
    if write_report:
        (root / "qualitative_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def audit_root(root: Path, limit: int | None = None) -> dict[str, Any]:
    task_dirs = sorted(path.parent for path in root.rglob("task.json"))
    if limit is not None:
        task_dirs = task_dirs[:limit]
    return audit_dirs(root, task_dirs, write_report=limit is None)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit benchmark outputs for qualitative weaknesses.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = audit_root(args.root, limit=args.limit)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        status = "PASS" if report["valid"] else "FAIL"
        print(f"qualitative_benchmark_audit: {status} tasks={report['tasks']} errors={summary['errors']} warnings={summary['warnings']}")
        for item in report["findings"]:
            print(f"[{item['severity']}] {item['code']}: {item['path']}: {item['message']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
