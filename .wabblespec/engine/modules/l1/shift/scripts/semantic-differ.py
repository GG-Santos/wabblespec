#!/usr/bin/env python3
"""
WabbleSpec Shift — semantic-differ.py

Takes --before <path> --after <path>. Classifies changes as
BREAKING / DEPRECATION / ADDITIVE / COSMETIC.
Outputs JSON with change_class array and list of changed sections.

Usage:
  python modules/l1/shift/scripts/semantic-differ.py --before old.md --after new.md
  python modules/l1/shift/scripts/semantic-differ.py --before v1.schema.json --after v2.schema.json
"""
import argparse
import json
import re
import sys
from pathlib import Path


BREAKING_SIGNALS = [
    r"\bremov(e|ed|ing)\b",
    r"\bren(ame|amed|aming)\b",
    r"\bbreak(ing|s)?\b",
    r"\bincompatible\b",
    r"\bmust\s+not\b",
    r"\bno\s+longer\b",
    r"\bdelet(e|ed|ing)\b",
    r"\bdrop(ped|ping)?\b",
]

DEPRECATION_SIGNALS = [
    r"\bdeprecate[ds]?\b",
    r"\bsunset\b",
    r"\blegacy\b",
    r"\bscheduled\s+for\s+removal\b",
    r"\bwill\s+be\s+removed\b",
]

ADDITIVE_SIGNALS = [
    r"\badd(ed|ing|s)?\b",
    r"\bnew\b",
    r"\bintroduc(e|ed|ing)\b",
    r"\bextend(ed|ing|s)?\b",
    r"\bsupport(s|ed|ing)?\b",
    r"\boptional\b",
]


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_sections_md(text: str) -> dict[str, str]:
    """Extract heading-delimited sections from markdown."""
    sections: dict[str, str] = {}
    current_heading = "__preamble__"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line.lstrip("# ").strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections[current_heading] = "\n".join(current_lines).strip()

    return sections


def extract_sections_json(text: str) -> dict[str, str]:
    """Flatten JSON into key: value string pairs for diffing."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"__raw__": text}

    def flatten(obj, prefix=""):
        items = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                items.update(flatten(v, f"{prefix}.{k}" if prefix else k))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                items.update(flatten(v, f"{prefix}[{i}]"))
        else:
            items[prefix] = str(obj)
        return items

    return flatten(data)


def classify_diff(before_text: str, after_text: str, changed_sections: list[str]) -> str:
    """Classify the overall change based on diff signals."""
    # Find lines added/removed
    before_lines = set(before_text.splitlines())
    after_lines = set(after_text.splitlines())
    removed = before_lines - after_lines
    added = after_lines - before_lines

    removed_text = " ".join(removed).lower()
    added_text = " ".join(added).lower()
    all_changed = (removed_text + " " + added_text).lower()

    # Check for breaking signals in removed content
    for pattern in BREAKING_SIGNALS:
        if re.search(pattern, removed_text, re.IGNORECASE):
            return "BREAKING"

    # Check for deprecation signals in added content
    for pattern in DEPRECATION_SIGNALS:
        if re.search(pattern, added_text, re.IGNORECASE):
            return "DEPRECATION"

    # Check for additive signals in added content (no removal)
    if added and not removed:
        return "ADDITIVE"

    for pattern in ADDITIVE_SIGNALS:
        if re.search(pattern, added_text, re.IGNORECASE) and not removed:
            return "ADDITIVE"

    # If only cosmetic changes (whitespace, punctuation, rewording)
    if added or removed:
        # Normalize and compare
        before_norm = re.sub(r'\s+', ' ', before_text).strip()
        after_norm = re.sub(r'\s+', ' ', after_text).strip()
        if before_norm != after_norm:
            # Has substantive changes but no breaking/deprecation/additive signals
            if added and removed:
                return "ADDITIVE"  # Conservative: has additions
            return "COSMETIC"

    return "COSMETIC"


def diff_sections(before: dict[str, str], after: dict[str, str]) -> list[dict]:
    """Compare section maps and return list of changed sections with classification."""
    changed = []

    all_keys = set(before) | set(after)
    for key in sorted(all_keys):
        b_val = before.get(key, "")
        a_val = after.get(key, "")

        if b_val == a_val:
            continue

        if key not in before:
            change_type = "ADDITIVE"
        elif key not in after:
            change_type = "BREAKING"
        else:
            change_type = classify_diff(b_val, a_val, [key])

        changed.append({
            "section": key,
            "change_type": change_type,
            "before_length": len(b_val),
            "after_length": len(a_val),
        })

    return changed


def overall_class(changed_sections: list[dict]) -> str:
    """Worst-class wins."""
    priority = {"BREAKING": 4, "DEPRECATION": 3, "ADDITIVE": 2, "COSMETIC": 1}
    if not changed_sections:
        return "COSMETIC"
    worst = max(changed_sections, key=lambda c: priority.get(c["change_type"], 0))
    return worst["change_type"]


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Shift semantic-differ")
    parser.add_argument("--before", required=True, help="Path to before file")
    parser.add_argument("--after", required=True, help="Path to after file")
    args = parser.parse_args()

    before_path = Path(args.before)
    after_path = Path(args.after)

    before_text = load_text(before_path)
    after_text = load_text(after_path)

    # Choose extraction strategy by file type
    if before_path.suffix == ".json":
        before_sections = extract_sections_json(before_text)
        after_sections = extract_sections_json(after_text)
    else:
        before_sections = extract_sections_md(before_text)
        after_sections = extract_sections_md(after_text)

    changed = diff_sections(before_sections, after_sections)
    change_class = overall_class(changed)

    result = {
        "before": str(before_path),
        "after": str(after_path),
        "change_class": change_class,
        "changed_sections": changed,
        "sections_changed_count": len(changed),
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
