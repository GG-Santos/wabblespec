#!/usr/bin/env python3
"""
ears-validate.py

Validates EARS (Easy Approach to Requirements Syntax) requirements in spec files.
Rejects vague adverbs, enforces measurable thresholds, verifies requirement-to-test mapping.

Usage:
    python ears-validate.py <spec_file> [--test-dir <path>] [--json]

Exit codes:
    0 — All requirements valid
    1 — Validation failures found
    2 — File not found or parse error
"""

import re
import sys
import json
import argparse
from pathlib import Path


# EARS requirement patterns
EARS_PATTERNS = {
    "ubiquitous": re.compile(r"^The\s+\w.+\s+shall\s+.+\.", re.IGNORECASE),
    "event_driven": re.compile(r"^When\s+.+,\s+the\s+\w.+\s+shall\s+.+\.", re.IGNORECASE),
    "state_driven": re.compile(r"^While\s+.+,\s+the\s+\w.+\s+shall\s+.+\.", re.IGNORECASE),
    "unwanted": re.compile(r"^If\s+.+,\s+then\s+the\s+\w.+\s+shall\s+.+\.", re.IGNORECASE),
    "optional": re.compile(r"^Where\s+.+,\s+the\s+\w.+\s+shall\s+.+\.", re.IGNORECASE),
}

# Vague adverbs that make requirements unmeasurable
VAGUE_ADVERBS = [
    "seamlessly", "properly", "appropriately", "efficiently", "effectively",
    "quickly", "easily", "smoothly", "correctly", "adequately", "reasonably",
    "sufficiently", "appropriately", "suitably", "satisfactorily", "acceptably",
    "robustly", "reliably", "consistently", "transparently", "gracefully",
    "intuitively", "cleanly", "safely", "securely", "optimally",
]

# Weak normative terms (should use SHALL or MUST)
WEAK_NORMATIVE = re.compile(r"\bshould\b|\bmay\b|\bcould\b|\bwould\b|\bmight\b", re.IGNORECASE)

# Measurable threshold patterns (good — these are what we want)
MEASURABLE_PATTERNS = [
    re.compile(r"\d+\s*(ms|milliseconds?|seconds?|minutes?|hours?)\b", re.IGNORECASE),
    re.compile(r"\d+\s*(%|percent)\b", re.IGNORECASE),
    re.compile(r"\d+\s*(bytes?|kb|mb|gb|requests?|items?|rows?|records?)\b", re.IGNORECASE),
    re.compile(r"within\s+\d+", re.IGNORECASE),
    re.compile(r"at\s+least\s+\d+", re.IGNORECASE),
    re.compile(r"no\s+more\s+than\s+\d+", re.IGNORECASE),
    re.compile(r"exactly\s+\d+", re.IGNORECASE),
]


def extract_requirements(text: str) -> list[dict]:
    """Extract EARS-style SHALL requirements from markdown text."""
    requirements = []
    lines = text.splitlines()
    current_req = []
    in_req = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Start of a requirement: line containing SHALL
        if re.search(r"\bshall\b|\bSHALL\b|\bMUST\b|\bmust\b", stripped):
            if current_req:
                requirements.append({
                    "text": " ".join(current_req).strip(),
                    "line_start": i - len(current_req) + 1,
                })
                current_req = []
            current_req = [stripped]
            in_req = True
        elif in_req and stripped and not stripped.startswith("#") and not stripped.startswith("|"):
            # Continuation of multi-line requirement
            if stripped.endswith("."):
                current_req.append(stripped)
                requirements.append({
                    "text": " ".join(current_req).strip(),
                    "line_start": i - len(current_req) + 1,
                })
                current_req = []
                in_req = False
            else:
                current_req.append(stripped)
        else:
            if current_req:
                requirements.append({
                    "text": " ".join(current_req).strip(),
                    "line_start": i - len(current_req) + 1,
                })
                current_req = []
            in_req = False

    if current_req:
        requirements.append({"text": " ".join(current_req).strip(), "line_start": len(lines)})

    return requirements


def classify_ears_type(text: str) -> str:
    for ears_type, pattern in EARS_PATTERNS.items():
        if pattern.match(text):
            return ears_type
    return "unknown"


def find_vague_adverbs(text: str) -> list[str]:
    found = []
    words = re.findall(r"\b\w+\b", text.lower())
    for adverb in VAGUE_ADVERBS:
        if adverb in words:
            found.append(adverb)
    return found


def has_measurable_threshold(text: str) -> bool:
    return any(p.search(text) for p in MEASURABLE_PATTERNS)


def check_test_mapping(req_text: str, test_dir: Path) -> bool:
    """Check if any test file references key terms from this requirement."""
    if not test_dir or not test_dir.exists():
        return None  # Cannot check — not_tested

    # Extract key nouns from requirement (simplified: words after SHALL)
    match = re.search(r"\bshall\b\s+(.+)", req_text, re.IGNORECASE)
    if not match:
        return None

    action_phrase = match.group(1)[:50]  # First 50 chars of action
    # Look for any test file mentioning key words
    key_words = [w for w in action_phrase.split() if len(w) > 4 and w.isalpha()]

    for test_file in test_dir.rglob("*.py"):
        content = test_file.read_text(encoding="utf-8", errors="replace").lower()
        if any(kw.lower() in content for kw in key_words[:3]):
            return True

    return False


def validate_requirement(req: dict, test_dir: Path | None) -> dict:
    text = req["text"]
    violations = []
    warnings = []

    # Check EARS type
    ears_type = classify_ears_type(text)
    if ears_type == "unknown":
        violations.append({
            "code": "EARS_TYPE_UNKNOWN",
            "message": "Requirement does not match any EARS pattern (Ubiquitous/Event-driven/State-driven/Unwanted/Optional)",
        })

    # Check for vague adverbs
    vague = find_vague_adverbs(text)
    if vague:
        violations.append({
            "code": "VAGUE_ADVERB",
            "message": f"Vague adverb(s) found: {', '.join(vague)}. Replace with measurable threshold.",
        })

    # Check for weak normative terms
    weak_match = WEAK_NORMATIVE.search(text)
    if weak_match:
        violations.append({
            "code": "WEAK_NORMATIVE",
            "message": f"Weak normative term '{weak_match.group()}' found. Use SHALL or MUST.",
        })

    # Check measurability for performance/quality claims
    performance_indicators = ["time", "latency", "speed", "fast", "performance", "response", "load", "memory"]
    has_perf_claim = any(indicator in text.lower() for indicator in performance_indicators)
    if has_perf_claim and not has_measurable_threshold(text):
        warnings.append({
            "code": "UNMEASURABLE_THRESHOLD",
            "message": "Performance claim detected but no measurable threshold (e.g., '< 200ms', '< 10%') found.",
        })

    # Check test mapping
    test_mapped = None
    if test_dir:
        test_mapped = check_test_mapping(text, test_dir)
        if test_mapped is False:
            warnings.append({
                "code": "NO_TEST_MAPPING",
                "message": "No test file found referencing key terms from this requirement.",
            })

    return {
        "text": text[:120] + ("..." if len(text) > 120 else ""),
        "line": req.get("line_start", 0),
        "ears_type": ears_type,
        "violations": violations,
        "warnings": warnings,
        "valid": len(violations) == 0,
        "test_mapped": test_mapped,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate EARS requirements in spec files.")
    parser.add_argument("spec_file", help="Path to spec file (.md)")
    parser.add_argument("--test-dir", help="Path to test directory for mapping check")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        print(f"ERROR: File not found: {spec_path}", file=sys.stderr)
        sys.exit(2)

    test_dir = Path(args.test_dir) if args.test_dir else None

    try:
        text = spec_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"ERROR: Cannot read file: {e}", file=sys.stderr)
        sys.exit(2)

    requirements = extract_requirements(text)
    results = [validate_requirement(req, test_dir) for req in requirements]

    total = len(results)
    valid = sum(1 for r in results if r["valid"])
    violations = sum(len(r["violations"]) for r in results)
    warnings = sum(len(r["warnings"]) for r in results)

    report = {
        "file": str(spec_path),
        "requirements_found": total,
        "requirements_valid": valid,
        "requirements_invalid": total - valid,
        "total_violations": violations,
        "total_warnings": warnings,
        "results": results,
        "status": "PASS" if violations == 0 else "FAIL",
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ears-validate: {report['status']} — {valid}/{total} valid, {violations} violation(s), {warnings} warning(s)")
        for r in results:
            if r["violations"] or r["warnings"]:
                print(f"\n  Line {r['line']}: {r['text'][:80]}...")
                for v in r["violations"]:
                    print(f"    [VIOLATION] {v['code']}: {v['message']}")
                for w in r["warnings"]:
                    print(f"    [WARNING]   {w['code']}: {w['message']}")

    sys.exit(0 if violations == 0 else 1)


if __name__ == "__main__":
    main()
