"""
markdown-extract.py — Markdown structural extraction and preservation check.

Used by Verifier to confirm that LLM document transformations (compress, polish,
translate, rewrite) do not drop or alter structural elements that must survive.

Checks:
  headings    — count, level, and text preserved
  code_blocks — fenced blocks preserved exactly (CommonMark-correct extraction)
  urls        — all URLs present in original are present in transformed
  inline_code — inline backtick spans not lost

Usage (standalone):
  python _shared/scripts/markdown-extract.py --check <original> <transformed>
  python _shared/scripts/markdown-extract.py --check <original> <transformed> --json

Exit codes:
  0 = preservation OK (zero errors; warnings are informational)
  1 = preservation FAIL (one or more errors)
  2 = input error (file not found, etc.)
"""

import re
import sys
import json
import argparse
from collections import Counter
from pathlib import Path

# ── Regex patterns ────────────────────────────────────────────────────────────

URL_REGEX = re.compile(r"https?://[^\s)\]>\"]+")
FENCE_OPEN_REGEX = re.compile(r"^(\s{0,3})(`{3,}|~{3,})(.*)$")
HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)


# ── Extraction functions ──────────────────────────────────────────────────────

def extract_headings(text: str) -> list:
    """Returns list of (level_str, title_str) tuples for all ATX headings."""
    return [(level, title.strip()) for level, title in HEADING_REGEX.findall(text)]


def extract_code_blocks(text: str) -> list:
    """
    CommonMark-correct fenced code block extractor.

    Handles nested fences: an outer 4-backtick fence wrapping an inner
    3-backtick fence is correctly parsed as one block. The closing fence
    must use the same character and be at least as long as the opening fence.
    An unclosed fence is discarded (not returned).
    """
    blocks = []
    lines = text.split("\n")
    i, n = 0, len(lines)
    while i < n:
        m = FENCE_OPEN_REGEX.match(lines[i])
        if not m:
            i += 1
            continue
        fence_char = m.group(2)[0]
        fence_len = len(m.group(2))
        block_lines = [lines[i]]
        i += 1
        closed = False
        while i < n:
            close_m = FENCE_OPEN_REGEX.match(lines[i])
            if (
                close_m
                and close_m.group(2)[0] == fence_char
                and len(close_m.group(2)) >= fence_len
                and close_m.group(3).strip() == ""
            ):
                block_lines.append(lines[i])
                closed = True
                i += 1
                break
            block_lines.append(lines[i])
            i += 1
        if closed:
            blocks.append("\n".join(block_lines))
    return blocks


def extract_urls(text: str) -> set:
    """Returns set of all http/https URLs found in text."""
    return set(URL_REGEX.findall(text))


def extract_inline_codes(text: str) -> Counter:
    """
    Returns Counter of inline backtick spans, excluding content inside
    fenced code blocks to avoid false positives.
    """
    # Remove fenced code blocks first
    stripped = re.sub(
        r"^(`{3,}|~{3,})[^\n]*\n.*?\n\1\s*$",
        "",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return Counter(re.findall(r"`([^`\n]+)`", stripped))


# ── Preservation check ────────────────────────────────────────────────────────

def preservation_check(original: str, transformed: str) -> dict:
    """
    Compare structural elements between original and transformed text.

    Returns:
        dict with keys:
          valid    (bool)   — True when errors is empty
          errors   (list)   — Blocking failures: dropped code blocks, lost URLs,
                              heading count change, inline code losses
          warnings (list)   — Non-blocking observations: heading text/order changes
    """
    errors, warnings = [], []

    # Headings
    h_orig = extract_headings(original)
    h_trans = extract_headings(transformed)
    if len(h_orig) != len(h_trans):
        errors.append(
            f"Heading count changed: {len(h_orig)} -> {len(h_trans)}"
        )
    elif h_orig != h_trans:
        warnings.append("Heading text or order changed (count matches)")

    # Code blocks — must be preserved exactly
    cb_orig = extract_code_blocks(original)
    cb_trans = extract_code_blocks(transformed)
    if cb_orig != cb_trans:
        if len(cb_orig) != len(cb_trans):
            errors.append(
                f"Code block count changed: {len(cb_orig)} -> {len(cb_trans)}"
            )
        else:
            errors.append("Code block content changed (count matches but content differs)")

    # URLs — all originals must survive
    u_orig = extract_urls(original)
    u_trans = extract_urls(transformed)
    lost_urls = u_orig - u_trans
    added_urls = u_trans - u_orig
    if lost_urls:
        errors.append(f"URLs lost: {sorted(lost_urls)}")
    if added_urls:
        warnings.append(f"URLs added (not in original): {sorted(added_urls)}")

    # Inline code — original spans must not be dropped
    ic_orig = extract_inline_codes(original)
    ic_trans = extract_inline_codes(transformed)
    lost_spans = {k for k in ic_orig if ic_orig[k] > ic_trans.get(k, 0)}
    if lost_spans:
        errors.append(f"Inline code spans lost: {sorted(lost_spans)}")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Check structural preservation between original and transformed markdown."
    )
    parser.add_argument("--check", nargs=2, metavar=("ORIGINAL", "TRANSFORMED"),
                        help="Paths to original and transformed markdown files.")
    parser.add_argument("--json", action="store_true",
                        help="Emit results as JSON instead of human-readable text.")
    args = parser.parse_args()

    if not args.check:
        parser.print_help()
        sys.exit(2)

    orig_path, trans_path = Path(args.check[0]), Path(args.check[1])

    if not orig_path.exists():
        print(f"ERROR: original file not found: {orig_path}", file=sys.stderr)
        sys.exit(2)
    if not trans_path.exists():
        print(f"ERROR: transformed file not found: {trans_path}", file=sys.stderr)
        sys.exit(2)

    original = orig_path.read_text(encoding="utf-8", errors="replace")
    transformed = trans_path.read_text(encoding="utf-8", errors="replace")

    result = preservation_check(original, transformed)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print(f"Preservation check: {status}")
        print(f"  Errors:   {len(result['errors'])}")
        print(f"  Warnings: {len(result['warnings'])}")
        if result["errors"]:
            print()
            print("ERRORS:")
            for e in result["errors"]:
                print(f"  - {e}")
        if result["warnings"]:
            print()
            print("WARNINGS:")
            for w in result["warnings"]:
                print(f"  - {w}")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
