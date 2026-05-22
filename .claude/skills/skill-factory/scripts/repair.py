"""Repair-loop helpers for classification, prompt guidance, and history."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from scripts.observability import write_redacted_json_artifact


REPAIR_CAUSES = {
    "missing_file",
    "invalid_yaml",
    "generic_body",
    "missing_safety",
    "missing_output_contract",
    "verbosity",
    "encoding",
    "copy_path",
    "blocked_by_filter",
    "trigger_false_negative",
    "trigger_false_positive",
    "description_length",
}

CRITICAL_REPAIR_CAUSES = {
    "missing_file",
    "invalid_yaml",
    "missing_safety",
    "missing_output_contract",
    "encoding",
    "blocked_by_filter",
}


def classify_repair_causes(
    validation_report: dict[str, Any] | None = None,
    eval_results: dict[str, Any] | None = None,
    error_text: str = "",
) -> list[str]:
    """Classify repair causes from validators, evals, and error strings."""
    causes: set[str] = set()
    lower_error = error_text.lower()
    report = validation_report or {}

    for item in report.get("findings", []):
        code = str(item.get("code", "")).lower()
        if "missing_skill" in code or "missing_file" in code:
            causes.add("missing_file")
        if "yaml" in code or "frontmatter" in code:
            causes.add("invalid_yaml")
        if "generic" in code:
            causes.add("generic_body")
        if "safety" in code or "refusal" in code or "recency" in code:
            causes.add("missing_safety")
        if "output_contract" in code:
            causes.add("missing_output_contract")
        if "length" in code or "token" in code or "verbosity" in code:
            causes.add("verbosity")
        if "utf8" in code or "mojibake" in code or "encoding" in code:
            causes.add("encoding")

    if eval_results:
        for result in eval_results.get("results", []):
            if result.get("pass"):
                continue
            if result.get("should_trigger"):
                causes.add("trigger_false_negative")
            else:
                causes.add("trigger_false_positive")

    if any(term in lower_error for term in ["not found", "missing", "no skill.md"]):
        causes.add("missing_file")
    if any(term in lower_error for term in ["yaml", "frontmatter"]):
        causes.add("invalid_yaml")
    if any(term in lower_error for term in ["copy", "shutil", "permission", "access is denied"]):
        causes.add("copy_path")
    if any(term in lower_error for term in ["blocked", "safety filter", "content filter"]):
        causes.add("blocked_by_filter")
    if any(term in lower_error for term in ["too long", "over limit", "1024"]):
        causes.add("description_length")

    return sorted(causes)


def build_preserve_list(
    current_description: str,
    eval_results: dict[str, Any] | None = None,
    max_items: int = 8,
) -> list[str]:
    """Extract description phrases and passing-trigger cues to preserve."""
    preserve: list[str] = []
    for part in current_description.replace(";", ",").split(","):
        item = " ".join(part.split()).strip(" .")
        if 8 <= len(item) <= 120 and item not in preserve:
            preserve.append(item)

    if eval_results:
        for result in eval_results.get("results", []):
            if result.get("pass") and result.get("should_trigger"):
                query = str(result.get("query", "")).strip()
                if query and query not in preserve:
                    preserve.append(query[:120])
            if len(preserve) >= max_items:
                break

    return preserve[:max_items]


def build_target_sections(causes: list[str], eval_results: dict[str, Any] | None = None) -> list[str]:
    """Map repair causes to focused prompt targets."""
    targets: list[str] = []
    mapping = {
        "trigger_false_negative": "Add broader intent coverage for missed should-trigger queries.",
        "trigger_false_positive": "Tighten boundaries so unrelated queries do not trigger.",
        "description_length": "Compress wording without dropping core trigger terms.",
        "missing_safety": "Add safety, refusal, recency, or safe-redirect language.",
        "missing_output_contract": "Add the output contract section.",
        "generic_body": "Replace generic scaffold wording with domain-specific text.",
        "verbosity": "Reduce repeated or low-signal wording.",
        "encoding": "Normalize corrupted text.",
        "blocked_by_filter": "Use defensive or allowed framing.",
        "copy_path": "Fix artifact path/copy handling.",
        "invalid_yaml": "Fix YAML/frontmatter syntax.",
        "missing_file": "Ensure required file exists at the expected path.",
    }
    for cause in causes:
        target = mapping.get(cause)
        if target and target not in targets:
            targets.append(target)

    if eval_results:
        misses = [r for r in eval_results.get("results", []) if not r.get("pass")]
        if misses and "Address only failing eval rows; do not overfit passing rows." not in targets:
            targets.append("Address only failing eval rows; do not overfit passing rows.")

    return targets


def is_critical_repair(causes: list[str]) -> bool:
    return bool(set(causes) & CRITICAL_REPAIR_CAUSES)


def growth_ratio(before: str, after: str) -> float:
    if not before:
        return 1.0 if after else 0.0
    return max(0.0, (len(after) - len(before)) / max(len(before), 1))


def within_growth_cap(before: str, after: str, causes: list[str], max_growth_ratio: float = 0.35) -> bool:
    if is_critical_repair(causes):
        return True
    return growth_ratio(before, after) <= max_growth_ratio


def build_repair_guidance_section(
    causes: list[str],
    preserve: list[str],
    targets: list[str],
    max_growth_ratio: float = 0.35,
) -> str:
    """Render compact guidance for a repair prompt."""
    lines = ["REPAIR CONTEXT:"]
    lines.append(f"- Causes: {', '.join(causes) if causes else 'unknown'}")
    lines.append(f"- Token/length cap: keep growth <= {int(max_growth_ratio * 100)}% unless fixing critical safety/validity.")
    if preserve:
        lines.append("- Preserve:")
        lines.extend(f"  - {item}" for item in preserve)
    if targets:
        lines.append("- Target only:")
        lines.extend(f"  - {item}" for item in targets)
    lines.append("- Do not make the artifact more verbose just to satisfy a checklist.")
    return "\n".join(lines)


def make_repair_entry(
    *,
    iteration: int | None,
    stage: str,
    causes: list[str],
    before: str,
    after: str,
    accepted: bool,
    preserve: list[str],
    targets: list[str],
    note: str = "",
) -> dict[str, Any]:
    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "iteration": iteration,
        "stage": stage,
        "causes": causes,
        "critical": is_critical_repair(causes),
        "before_chars": len(before),
        "after_chars": len(after),
        "growth_ratio": round(growth_ratio(before, after), 3),
        "accepted": accepted,
        "preserve": preserve,
        "targets": targets,
        "note": note,
    }


def append_repair_history(log_dir: Path | None, entry: dict[str, Any]) -> Path | None:
    """Append one repair entry to repair_history.json under log_dir."""
    if log_dir is None:
        return None
    path = log_dir / "repair_history.json"
    existing: list[dict[str, Any]] = []
    if path.exists():
        try:
            import json
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except Exception:
            existing = []
    existing.append(entry)
    write_redacted_json_artifact(log_dir, "repair_history.json", existing)
    return path
