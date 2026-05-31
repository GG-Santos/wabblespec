#!/usr/bin/env python3
"""
slide-token-validator.py — Token compliance checker for generated HTML slides.

Scans HTML files for raw CSS values that violate the design token contract:
all visual property values must use CSS custom property references (var(--token)).

Violations detected:
  raw-hex   Raw hexadecimal colors (#xxx, #xxxxxx) in CSS property values
  raw-rgb   Raw rgb() / rgba() calls in CSS property values

CSS custom property DEFINITIONS are exempt:
  --color-primary: #2563EB;        <- ALLOWED (definition)
  color: #2563EB;                  <- VIOLATION (usage)
  --shadow-sm: 0 1px 2px rgba(...) <- ALLOWED (definition)
  box-shadow: rgba(0,0,0,0.1);     <- VIOLATION (usage)

Usage:
    python slide-token-validator.py <file.html> [<file2.html> ...]

Exit codes:
    0   No violations found
    1   One or more violations found
    2   File not found or unreadable
"""

import re
import sys
import argparse
from pathlib import Path

# --- Patterns ---

# Raw hex color value: #RGB, #RRGGBB, #RRGGBBAA
_RAW_HEX = re.compile(r'#([0-9a-fA-F]{3,8})\b')

# Raw rgb() / rgba() call
_RAW_RGB = re.compile(r'\brgba?\s*\(')


def _split_declarations(css_text: str):
    """
    Split a CSS text fragment (inside a {} block or a style= value) into
    individual declarations separated by ';'.
    Returns a list of declaration strings (may be empty or whitespace-only).
    """
    # Remove brace pairs first so we don't split on content inside nested blocks
    # For our purposes (flat CSS), this is sufficient.
    inner = re.sub(r'\{[^}]*\}', '', css_text)
    return inner.split(';')


def _declaration_is_custom_prop(decl: str) -> bool:
    """Return True if this CSS declaration defines a custom property (--name: value)."""
    stripped = decl.strip()
    return stripped.startswith('--')


def _find_violations_in_text(text: str, base_lineno: int, raw_lines):
    """
    Scan text for raw hex / rgb violations, accounting for custom property exemptions.

    text: the CSS content to scan (may span multiple lines)
    base_lineno: the 1-based line number where this text starts
    raw_lines: the original file lines list (for precise line-number reporting)

    Returns list of (lineno, vtype, raw_value, line_text).
    """
    violations = []

    # We operate line-by-line for line-number accuracy
    text_lines = text.splitlines()

    for i, line in enumerate(text_lines):
        lineno = base_lineno + i
        original = raw_lines[lineno - 1] if lineno <= len(raw_lines) else line

        # Split this line into individual CSS declarations
        # Handle both "prop: val;" and ":root { --x: val; color: val; }" on one line
        # Strategy: find all property declarations by splitting on ';' and also
        # handling the content between '{' and '}' if present.

        # Strip off surrounding selectors and braces to get declaration text
        decl_text = line

        # Remove CSS selectors (text up to and including the first '{') unless the
        # brace itself contains a declaration (single-line block)
        # Split into declaration chunks at every ';'
        chunks = re.split(r';', decl_text)

        for chunk in chunks:
            # Further split if the chunk has nested braces (e.g., :root { --x: val)
            # Extract the part after the last '{' as the declaration candidate
            parts = re.split(r'\{', chunk)
            for part in parts:
                part = part.rstrip('}').strip()
                if not part:
                    continue

                # Check if this is a custom property definition
                if _declaration_is_custom_prop(part):
                    continue  # Exempt — this is a token definition

                # Find the value portion (after the first ':' that follows a property name)
                colon_idx = part.find(':')
                if colon_idx == -1:
                    # No colon — CSS selector or empty; skip
                    continue

                prop_name = part[:colon_idx].strip()
                value = part[colon_idx + 1:]

                # Skip pseudo-selectors like :root, :hover, ::before
                if not prop_name or prop_name.startswith(':'):
                    continue

                # Check for raw hex in value
                for m in _RAW_HEX.finditer(value):
                    violations.append((lineno, 'raw-hex', m.group(0), original.rstrip()))

                # Check for raw rgb()/rgba() in value
                for m in _RAW_RGB.finditer(value):
                    rgb_token = m.group(0).rstrip('( ') + '()'
                    violations.append((lineno, 'raw-rgb', rgb_token, original.rstrip()))

    return violations


def _extract_style_blocks(html_text: str):
    """
    Yield (start_lineno, block_text) for each <style> block and style="" attribute.
    start_lineno is 1-based.
    """
    lines = html_text.splitlines()
    full_text = html_text

    # --- <style> blocks ---
    style_block_re = re.compile(r'<style[^>]*>(.*?)</style>', re.IGNORECASE | re.DOTALL)
    for m in style_block_re.finditer(full_text):
        start_char = m.start(1)
        # Convert character offset to line number
        start_lineno = full_text[:start_char].count('\n') + 1
        yield start_lineno, m.group(1), lines

    # --- inline style="..." attributes ---
    style_attr_re = re.compile(r'\bstyle\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
    for m in style_attr_re.finditer(full_text):
        start_char = m.start(1)
        start_lineno = full_text[:start_char].count('\n') + 1
        yield start_lineno, m.group(1), lines


def check_file(filepath: str):
    """
    Check a single HTML file for token violations.
    Returns list of (lineno, vtype, raw_value, line_text).
    Calls sys.exit(2) on read error.
    """
    try:
        text = Path(filepath).read_text(encoding='utf-8', errors='replace')
    except OSError as exc:
        print(f"ERROR: Cannot read '{filepath}': {exc}", file=sys.stderr)
        sys.exit(2)

    raw_lines = text.splitlines()
    violations = []

    for start_lineno, block_text, lines_ref in _extract_style_blocks(text):
        violations.extend(
            _find_violations_in_text(block_text, start_lineno, lines_ref)
        )

    # Deduplicate (same line + type + value may surface from overlapping matches)
    seen = set()
    unique = []
    for v in violations:
        key = (v[0], v[1], v[2])
        if key not in seen:
            seen.add(key)
            unique.append(v)

    return sorted(unique, key=lambda x: x[0])


def main():
    parser = argparse.ArgumentParser(
        description='Validate HTML slides for CSS token compliance.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        'files',
        nargs='+',
        metavar='file.html',
        help='HTML file(s) to validate',
    )
    args = parser.parse_args()

    total_violations = 0

    for filepath in args.files:
        violations = check_file(filepath)
        if not violations:
            print(f"PASS  {filepath}  (0 violations)")
        else:
            total_violations += len(violations)
            print(f"FAIL  {filepath}  ({len(violations)} violation(s))")
            for lineno, vtype, value, snippet in violations:
                display = snippet[:100] + ('...' if len(snippet) > 100 else '')
                print(f"      Line {lineno:4d}  [{vtype}]  {value!r}")
                print(f"             {display}")

    if total_violations > 0:
        print(f"\nTotal: {total_violations} violation(s) across {len(args.files)} file(s).")
        print("Fix: replace raw values with var(--token-name) references.")
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
