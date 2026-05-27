"""
document-check.py — Structural checks on WabbleSpec document deliverables.

Replaces Claude reading an entire reference file just to confirm whether a
## Cross-references section exists and contains valid entries. This is a grep,
not a reasoning task — Claude should not load a potentially large file for it.

For --type reference: checks presence and content of ## Cross-references or
## See also / ## Cross-referencing section.

For other types (changelog, spec, etc.): applies appropriate structural checks.

Usage:
    # Check a reference file:
    python .wabblespec/engine/shared/scripts/document-check.py \\
        --file .wabblespec/engine/shared/references/invariants.md \\
        --type reference

    # Batch check all .md files in a directory:
    python .wabblespec/engine/shared/scripts/document-check.py \\
        --dir .wabblespec/engine/shared/references/ \\
        --type reference

    # JSON output (for Verifier receipt writing):
    python .wabblespec/engine/shared/scripts/document-check.py \\
        --file .wabblespec/engine/shared/references/invariants.md \\
        --type reference \\
        --json

    # Check a spec file for required sections:
    python .wabblespec/engine/shared/scripts/document-check.py \\
        --file .wabblespec/plans/task-card.md \\
        --type spec

    # Check a SKILL.md for quality-floor structure:
    python .wabblespec/engine/shared/scripts/document-check.py \\
        --file modules/l2/executor/SKILL.md \\
        --type skill

    # Check any file (detects type from path if --type omitted):
    python .wabblespec/engine/shared/scripts/document-check.py \\
        --file .wabblespec/engine/shared/references/foo.md

Exit codes:
    0  PASS or check not applicable for this type
    1  At least one structural check failed
    2  File not found or directory empty
"""

import sys
import os
import re
import json
import argparse
import glob as glob_module


# ---------------------------------------------------------------------------
# Cross-reference section patterns
# ---------------------------------------------------------------------------

# Section headers that count as cross-reference sections
CROSS_REF_HEADERS = re.compile(
    r"^##\s+(cross-ref|see also|cross-ref|cross-referencing)",
    re.IGNORECASE,
)

# A "real" cross-ref entry: a markdown list item with a path or URL reference
# Not just a bullet with placeholder text
CROSS_REF_ENTRY = re.compile(
    r"^[-*]\s+.{5,}",  # bullet with at least 5 chars of content
)

# HTML comment lines — not counted as real entries
HTML_COMMENT = re.compile(r"^\s*<!--")

# Placeholder-only patterns (not real entries)
PLACEHOLDER_PATTERNS = [
    re.compile(r"^\-\s+\[TBD\]", re.IGNORECASE),
    re.compile(r"^\-\s+TODO", re.IGNORECASE),
    re.compile(r"^\-\s+\.\.\.$"),
    re.compile(r"^\-\s+None\.?$", re.IGNORECASE),
    re.compile(r"^\-\s+N/A\.?$", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Document type detection
# ---------------------------------------------------------------------------

def detect_type(file_path):
    """Heuristic: detect document type from path."""
    basename = os.path.basename(file_path).lower()
    parts = file_path.replace("\\", "/").split("/")

    if "SKILL.md" in file_path or basename == "skill.md":
        return "skill"
    if ".wabblespec/engine/shared/references/" in file_path.replace("\\", "/"):
        return "reference"
    if ".wabblespec/engine/shared/templates/" in file_path.replace("\\", "/"):
        return "template"
    if basename in ("changelog.md", "changes.md"):
        return "changelog"
    if "task-card" in basename or "task_card" in basename:
        return "spec"
    if "wave-plan" in basename or "wave_plan" in basename:
        return "waveplan"
    if basename.endswith(".md") and "specs" in parts:
        return "spec"
    return "unknown"


# ---------------------------------------------------------------------------
# Cross-reference check (for reference-type documents)
# ---------------------------------------------------------------------------

def check_cross_references(lines, file_path):
    """
    Returns (found: bool, entry_count: int, finding: str|None)
    """
    in_section = False
    real_entries = 0
    section_line = None

    for i, line in enumerate(lines):
        stripped = line.rstrip()

        # Detect entering the cross-reference section
        if CROSS_REF_HEADERS.match(stripped):
            in_section = True
            section_line = i
            continue

        # Detect leaving the section (next ## header)
        if in_section and re.match(r"^##\s+", stripped) and not CROSS_REF_HEADERS.match(stripped):
            break

        if in_section:
            if not stripped or HTML_COMMENT.match(stripped):
                continue
            # Check for placeholder
            is_placeholder = any(p.match(stripped) for p in PLACEHOLDER_PATTERNS)
            if CROSS_REF_ENTRY.match(stripped) and not is_placeholder:
                real_entries += 1

    if not in_section:
        return False, 0, "CROSS_LINK_MISSING: no '## Cross-references' or '## See also' section found"

    if real_entries == 0:
        return True, 0, "CROSS_LINK_EMPTY: cross-references section found but contains no real entries (only placeholders or HTML comments)"

    return True, real_entries, None


# ---------------------------------------------------------------------------
# Type-specific checks
# ---------------------------------------------------------------------------

def check_reference(lines, file_path):
    found, count, finding = check_cross_references(lines, file_path)
    return {
        "cross_link_checked": True,
        "cross_link_verified": found and count > 0,
        "cross_link_section_found": found,
        "cross_link_entries": count,
        "finding": finding,
    }


def check_skill(lines, file_path):
    """Check SKILL.md for quality-floor required structure."""
    text = "\n".join(lines)
    findings = []

    if not re.search(r"^---\n", text):
        findings.append("SKILL_FRONTMATTER_MISSING: no YAML frontmatter block (---)")

    if not re.search(r"^name:", text, re.MULTILINE):
        findings.append("SKILL_NAME_MISSING: no 'name:' in frontmatter")

    if not re.search(r"^description:", text, re.MULTILINE):
        findings.append("SKILL_DESCRIPTION_MISSING: no 'description:' in frontmatter")

    if "## What this skill does" not in text:
        findings.append("SKILL_WHAT_MISSING: no '## What this skill does' section")

    if "## When to use" not in text:
        findings.append("SKILL_WHEN_MISSING: no '## When to use' section")

    # Output contract signal: any of these phrases
    output_contract_signals = [
        "output contract", "produces", "outputs", "receipt", "writes"
    ]
    has_contract = any(s in text.lower() for s in output_contract_signals)
    if not has_contract:
        findings.append("SKILL_OUTPUT_CONTRACT_MISSING: no output contract signal found")

    if len(text) < 200:
        findings.append(f"SKILL_BODY_SHORT: body is {len(text)} chars (minimum 200)")

    return {
        "structural_checks": 6,
        "findings": findings,
        "finding": "; ".join(findings) if findings else None,
    }


def check_spec(lines, file_path):
    """Check a spec/task-card file for required top-level sections."""
    text = "\n".join(lines)
    findings = []

    required_signals = ["## Goal", "## Criteria", "## Spec"]
    found_signals = [s for s in required_signals if s in text]
    if not found_signals:
        findings.append("SPEC_SECTIONS_MISSING: no ## Goal, ## Criteria, or ## Spec section found")

    return {
        "finding": "; ".join(findings) if findings else None,
    }


def check_changelog(lines, file_path):
    """Changelogs have no required cross-link section."""
    return {
        "cross_link_checked": False,
        "cross_link_verified": None,
        "finding": None,
    }


def check_unknown(lines, file_path):
    return {
        "cross_link_checked": False,
        "cross_link_verified": None,
        "finding": None,
    }


TYPE_CHECKERS = {
    "reference": check_reference,
    "skill": check_skill,
    "spec": check_spec,
    "changelog": check_changelog,
    "template": check_unknown,
    "waveplan": check_unknown,
    "unknown": check_unknown,
}


# ---------------------------------------------------------------------------
# Check one file
# ---------------------------------------------------------------------------

def check_file(file_path, doc_type=None):
    if not os.path.isfile(file_path):
        return {
            "file": file_path,
            "type": doc_type or "unknown",
            "verdict": "ERROR",
            "finding": f"FILE_NOT_FOUND: {file_path}",
        }

    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError as e:
        return {
            "file": file_path,
            "type": doc_type or "unknown",
            "verdict": "ERROR",
            "finding": f"READ_ERROR: {e}",
        }

    if doc_type is None:
        doc_type = detect_type(file_path)

    checker = TYPE_CHECKERS.get(doc_type, check_unknown)
    result = checker(lines, file_path)

    finding = result.get("finding")
    verdict = "FAIL" if finding else "PASS"

    return {
        "file": file_path,
        "type": doc_type,
        "verdict": verdict,
        **result,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_result(result):
    verdict = result["verdict"]
    f = result["file"]
    finding = result.get("finding")

    if verdict == "PASS":
        extras = []
        if result.get("cross_link_entries"):
            extras.append(f"{result['cross_link_entries']} cross-link entries")
        extra_str = f"  ({', '.join(extras)})" if extras else ""
        print(f"  PASS  {f}{extra_str}")
    elif verdict == "FAIL":
        print(f"  FAIL  {f}")
        print(f"        {finding}")
    else:
        print(f"  {verdict}  {f}: {finding}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Structural checks on WabbleSpec document deliverables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--file", metavar="PATH", help="Single file to check.")
    target.add_argument("--dir", metavar="PATH", help="Directory to check all .md files in.")

    parser.add_argument("--type", metavar="TYPE",
                        choices=["reference", "skill", "spec", "changelog",
                                 "template", "waveplan", "unknown"],
                        help="Document type (auto-detected from path if omitted).")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.file:
        result = check_file(args.file, args.type)
        results = [result]
    else:
        # Directory mode
        if not os.path.isdir(args.dir):
            print(f"ERROR: Directory not found: {args.dir}", file=sys.stderr)
            sys.exit(2)
        md_files = sorted(glob_module.glob(os.path.join(args.dir, "**/*.md"), recursive=True) +
                          glob_module.glob(os.path.join(args.dir, "*.md")))
        # Deduplicate
        md_files = sorted(set(md_files))
        if not md_files:
            print(f"No .md files found in {args.dir}")
            sys.exit(0)
        results = [check_file(f, args.type) for f in md_files]

    if args.emit_json:
        if len(results) == 1:
            print(json.dumps(results[0], indent=2))
        else:
            failures = [r for r in results if r["verdict"] == "FAIL"]
            print(json.dumps({
                "total": len(results),
                "pass": len(results) - len(failures),
                "fail": len(failures),
                "results": results,
            }, indent=2))
        fails = [r for r in results if r["verdict"] == "FAIL"]
        sys.exit(0 if not fails else 1)

    # Human-readable
    failures = [r for r in results if r["verdict"] == "FAIL"]

    if len(results) > 1:
        print(f"\nChecked {len(results)} files ({args.type or 'auto-detect'} type):")

    if args.verbose or len(results) == 1:
        for r in results:
            print_result(r)
    else:
        for r in results:
            if r["verdict"] != "PASS":
                print_result(r)
        if not failures:
            print(f"  All {len(results)} files PASS")

    if len(results) > 1:
        print(f"\n  PASS: {len(results) - len(failures)}/{len(results)}")
        if failures:
            print(f"  FAIL: {len(failures)}")

    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
