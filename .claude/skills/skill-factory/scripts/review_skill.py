#!/usr/bin/env python3
"""Review a skill definition with the Skill Factory quality checklist."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from scripts.quick_validate import extract_frontmatter, parse_frontmatter
except ModuleNotFoundError:  # Allows `python scripts/review_skill.py ...`.
    from quick_validate import extract_frontmatter, parse_frontmatter


REQUIRED_SECTIONS = [
    "workflow",
    "output contract",
    "examples",
    "failure modes",
]

STANDARD_OPTIONAL_DIRS = {
    "agents",
    "assets",
    "commands",
    "config",
    "data",
    "eval-viewer",
    "eval_viewer",
    "evaluations",
    "examples",
    "hooks",
    "matchers",
    "mcp",
    "plugin",
    "references",
    "rules",
    "schemas",
    "scripts",
    "templates",
}


def item(check_id: str, category: str, status: str, title: str, note: str, suggestion: str = "") -> dict[str, str]:
    return {
        "id": check_id,
        "category": category,
        "status": status,
        "title": title,
        "note": note,
        "suggestion": suggestion,
    }


def _frontmatter(skill_md: Path) -> tuple[dict[str, Any], str, str]:
    content = skill_md.read_text(encoding="utf-8")
    frontmatter_text = extract_frontmatter(content)
    return parse_frontmatter(frontmatter_text), frontmatter_text, content


def _status_counts(items: list[dict[str, str]]) -> dict[str, int]:
    return {
        "pass": sum(1 for entry in items if entry["status"] == "pass"),
        "warning": sum(1 for entry in items if entry["status"] == "warning"),
        "fail": sum(1 for entry in items if entry["status"] == "fail"),
    }


def _category_counts(items: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    categories: dict[str, dict[str, int]] = {}
    for entry in items:
        bucket = categories.setdefault(entry["category"], {"pass": 0, "warning": 0, "fail": 0})
        bucket[entry["status"]] += 1
    return categories


def _referenced_files(content: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(r"`((?:references|scripts|templates|assets|agents|config)/[^`]+)`", content):
        ref = match.group(1).strip().rstrip(".,)")
        if "*" not in ref and "<" not in ref and ">" not in ref:
            refs.append(ref)
    return sorted(set(refs))


def review_skill(skill_path: str | Path) -> dict[str, Any]:
    """Return a 20-check definition review for a skill folder."""
    root = Path(skill_path).resolve()
    skill_md = root / "SKILL.md"
    results: list[dict[str, str]] = []
    frontmatter: dict[str, Any] = {}
    content = ""

    # Structure
    if skill_md.exists():
        results.append(item("S1", "Structure", "pass", "SKILL.md exists", "Entry file found."))
        try:
            frontmatter, _frontmatter_text, content = _frontmatter(skill_md)
        except Exception as exc:
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            results.append(item("F1", "Format", "fail", "YAML delimiters", f"Frontmatter parse failed: {exc}", "Use exact standalone --- delimiters."))
    else:
        results.append(item("S1", "Structure", "fail", "SKILL.md exists", "Entry file missing.", "Create SKILL.md at the skill root."))

    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", root.name):
        results.append(item("S2", "Structure", "pass", "Folder naming", f"Folder is kebab-case: {root.name}."))
    else:
        results.append(item("S2", "Structure", "fail", "Folder naming", f"Folder is not kebab-case: {root.name}.", "Use lowercase kebab-case folder names."))

    root_files = {path.name for path in root.iterdir()} if root.exists() and root.is_dir() else set()
    unknown_dirs = [
        path.name for path in root.iterdir()
        if path.is_dir() and path.name not in STANDARD_OPTIONAL_DIRS and not path.name.startswith(".")
    ] if root.exists() and root.is_dir() else []
    if "README.md" in root_files:
        results.append(item("S3", "Structure", "fail", "Directory structure", "Root README.md is not part of the skill package shape.", "Move package notes into SKILL.md or references/."))
    elif unknown_dirs:
        results.append(item("S3", "Structure", "warning", "Directory structure", f"Non-standard directories: {', '.join(unknown_dirs)}.", "Use standard directories unless the extra folder is required."))
    else:
        results.append(item("S3", "Structure", "pass", "Directory structure", "Uses standard skill directories."))

    name = frontmatter.get("name", "") if isinstance(frontmatter, dict) else ""
    if name == root.name:
        results.append(item("S4", "Structure", "pass", "Name consistency", "Folder name matches frontmatter name."))
    elif name:
        results.append(item("S4", "Structure", "warning", "Name consistency", f"Folder '{root.name}' differs from name '{name}'.", "Keep folder and name aligned when packaging."))
    else:
        results.append(item("S4", "Structure", "fail", "Name consistency", "No frontmatter name available.", "Add name to frontmatter."))

    # Format
    if not any(entry["id"] == "F1" for entry in results):
        results.append(item("F1", "Format", "pass", "YAML delimiters", "Frontmatter delimiters parse correctly."))

    if isinstance(name, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        results.append(item("F2", "Format", "pass", "name field", f"Valid kebab-case name: {name}."))
    else:
        results.append(item("F2", "Format", "fail", "name field", "Missing or invalid name.", "Use lowercase kebab-case."))

    description = frontmatter.get("description", "") if isinstance(frontmatter, dict) else ""
    if isinstance(description, str) and 0 < len(description.strip()) < 900:
        results.append(item("F3", "Format", "pass", "description field", f"Description present ({len(description)} chars)."))
    elif isinstance(description, str) and len(description) <= 1024:
        results.append(item("F3", "Format", "warning", "description field", f"Description near limit ({len(description)} chars).", "Shorten if trigger quality can be preserved."))
    else:
        results.append(item("F3", "Format", "fail", "description field", "Description missing or too long.", "Keep description under 1024 chars."))

    if isinstance(description, str) and ("<" in description or ">" in description):
        results.append(item("F4", "Format", "fail", "No forbidden frontmatter content", "Description contains angle brackets.", "Remove XML-style angle brackets from frontmatter."))
    else:
        results.append(item("F4", "Format", "pass", "No forbidden frontmatter content", "No angle brackets in description."))

    optional_fields = {key: frontmatter[key] for key in ("metadata", "license", "compatibility") if key in frontmatter}
    if optional_fields and not all(isinstance(value, (str, dict)) for value in optional_fields.values()):
        results.append(item("F5", "Format", "warning", "Optional fields", "Optional frontmatter fields have unusual types.", "Use strings or metadata maps."))
    else:
        results.append(item("F5", "Format", "pass", "Optional fields", "Optional fields are absent or valid."))

    # Content
    lower = content.lower()
    if isinstance(description, str) and len(description.split()) >= 8:
        results.append(item("C1", "Content", "pass", "Description WHAT", "Description states purpose."))
    else:
        results.append(item("C1", "Content", "warning", "Description WHAT", "Description is too short to clearly state purpose.", "Say what the skill creates or reviews."))

    if isinstance(description, str) and re.search(r"\b(use when|use this skill|when the user|user asks)\b", description, re.I):
        results.append(item("C2", "Content", "pass", "Description WHEN", "Description includes trigger conditions."))
    else:
        results.append(item("C2", "Content", "warning", "Description WHEN", "Description lacks clear trigger phrasing.", "Add 'Use when...' trigger language."))

    missing_sections = [section for section in REQUIRED_SECTIONS if section not in lower]
    if missing_sections:
        results.append(item("C3", "Content", "fail", "Instructions actionable", f"Missing required sections: {', '.join(missing_sections)}.", "Add workflow, output contract, examples, and failure modes."))
    else:
        results.append(item("C3", "Content", "pass", "Instructions actionable", "Core actionable sections are present."))

    if "troubleshooting" in lower or "tool failure" in lower or "error handling" in lower:
        results.append(item("C4", "Content", "pass", "Error handling", "Failure/error handling guidance is present."))
    else:
        results.append(item("C4", "Content", "warning", "Error handling", "No explicit troubleshooting or tool-failure section.", "Add compact error handling."))

    if "example" in lower and ("user:" in lower or "worked example" in lower):
        results.append(item("C5", "Content", "pass", "Examples", "Examples or worked examples are present."))
    else:
        results.append(item("C5", "Content", "warning", "Examples", "Examples are thin or absent.", "Add at least one input/output worked example."))

    missing_refs = [ref for ref in _referenced_files(content) if not (root / ref).exists()]
    if missing_refs:
        results.append(item("C6", "Content", "fail", "Reference links", f"Missing referenced files: {', '.join(missing_refs)}.", "Remove stale references or add the files."))
    else:
        results.append(item("C6", "Content", "pass", "Reference links", "Referenced bundled files exist."))

    line_count = len(content.splitlines())
    if line_count <= 500:
        results.append(item("C7", "Content", "pass", "Progressive disclosure", f"SKILL.md is {line_count} lines."))
    elif line_count <= 800:
        results.append(item("C7", "Content", "warning", "Progressive disclosure", f"SKILL.md is {line_count} lines.", "Move rare details to references/."))
    else:
        results.append(item("C7", "Content", "fail", "Progressive disclosure", f"SKILL.md is {line_count} lines.", "Split long material into references/."))

    if "safety" in lower and ("final check" in lower or "when you think you're done" in lower):
        results.append(item("C8", "Content", "pass", "Critical instructions", "Safety and final-check guidance are explicit."))
    else:
        results.append(item("C8", "Content", "warning", "Critical instructions", "Critical boundaries are not obvious.", "Add safety and final-check guidance."))

    # Trigger
    positive_triggers = re.findall(r"(?i)\b(create|improve|review|validate|package|benchmark|audit|optimize)\b", description if isinstance(description, str) else "")
    if len(set(word.lower() for word in positive_triggers)) >= 3:
        results.append(item("T1", "Trigger", "pass", "Positive triggers", "Multiple specific trigger verbs are present."))
    else:
        results.append(item("T1", "Trigger", "warning", "Positive triggers", "Trigger verbs are sparse.", "Add specific user intents."))

    if isinstance(description, str) and len(description) <= 1024 and "anything" not in description.lower():
        results.append(item("T2", "Trigger", "pass", "Trigger scope", "Trigger scope is bounded."))
    else:
        results.append(item("T2", "Trigger", "warning", "Trigger scope", "Trigger scope may be too broad.", "Narrow the description."))

    if "don't use this skill" in lower or "do not use this skill" in lower:
        results.append(item("T3", "Trigger", "pass", "Negative triggers", "Exclusions are present."))
    else:
        results.append(item("T3", "Trigger", "warning", "Negative triggers", "No explicit negative trigger section.", "Add when not to use this skill."))

    counts = _status_counts(results)
    return {
        "schema_version": "skill-review-1.0",
        "skill_path": str(root),
        "valid": counts["fail"] == 0,
        "summary": counts,
        "categories": _category_counts(results),
        "items": results,
    }


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["summary"]
    lines = [
        f"# Skill Review: {Path(report['skill_path']).name}",
        "",
        f"> Path: `{report['skill_path']}`",
        "",
        "## Summary",
        "",
        "| Category | Pass | Warn | Fail |",
        "|----------|------|------|------|",
    ]
    for category, bucket in report["categories"].items():
        lines.append(f"| {category} | {bucket['pass']} | {bucket['warning']} | {bucket['fail']} |")
    lines.extend([
        f"| **Total** | **{counts['pass']}** | **{counts['warning']}** | **{counts['fail']}** |",
        "",
        "## Checks",
        "",
    ])
    status_label = {"pass": "PASS", "warning": "WARN", "fail": "FAIL"}
    for entry in report["items"]:
        lines.append(f"- {status_label[entry['status']]} **{entry['id']} {entry['title']}** - {entry['note']}")
        if entry.get("suggestion"):
            lines.append(f"  Suggestion: {entry['suggestion']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Review a skill definition with the Skill Factory checklist")
    parser.add_argument("skill_path", type=Path, help="Path to skill folder")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    report = review_skill(args.skill_path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_markdown(report))
    raise SystemExit(0 if report["valid"] else 1)


if __name__ == "__main__":
    main()
