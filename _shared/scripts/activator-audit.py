#!/usr/bin/env python3
"""
activator-audit.py — Routing-hostile language scanner for WabbleSpec SKILL.md files.

Checks the routing-sensitive sections of every modules/**/SKILL.md for language
patterns that degrade LLM module-selection, per the ADR-0002 rubric extracted
from context-mode's empirically validated tool description style guide.

SCOPE: Only checks these SKILL.md sections (the routing-sensitive surface):
  - "## What this skill does" (the description body)
  - "## When to use" (positive activator conditions)

Not checked: output contracts, examples, state machine tables, cold-start
procedures, or instructional text for the executing agent. Those sections
legitimately use instructional language that is not routing vocabulary.

Also excluded from all checks:
  - Lines inside code fences (``` ... ```)
  - Lines that are Markdown table rows (starting with |)
  - Bold section-header lines (**Do not use when:**)

Forbidden tokens that harm routing quality:
  MANDATORY:      Developer-policy opener — never a selection cue
  BLOCKED (prose) Reserved for true security denials per ADR-0003; BLOCKED
                  as a WabbleSpec receipt STATUS NAME is excluded (see --strict)
  PREFER.*OVER    Tradeoff framing; use positive WHEN condition instead
  Do NOT [verb]   Inline negative imperative in description prose
  Never use       Same class as Do NOT
  SESSION STATE   Role-persistence clause (belongs in hooks, not descriptions)
  ✅ / ❌          Tokenizer inconsistency across LLM families

Usage:
  python _shared/scripts/activator-audit.py
  python _shared/scripts/activator-audit.py --module modules/l2/guard/SKILL.md
  python _shared/scripts/activator-audit.py --fix     # auto-removes ✅/❌ only
  python _shared/scripts/activator-audit.py --verbose # show all files checked
  python _shared/scripts/activator-audit.py --json    # machine-readable output
  python _shared/scripts/activator-audit.py --strict  # also check non-routing sections
"""

import re
import os
import sys
import json
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Forbidden token patterns
# Each entry: (pattern, description, severity, auto_fixable)
# ---------------------------------------------------------------------------
FORBIDDEN = [
    (
        re.compile(r'^MANDATORY:', re.MULTILINE),
        'MANDATORY: as line opener — use affirmative positive condition instead',
        'error',
        False,
    ),
    (
        # "BLOCKED" in prose — excludes table rows (handled by line filter) and
        # WabbleSpec status names (BLOCKED as a value in a receipt state list).
        # Still flags bare BLOCKED in description/when-to-use sentences.
        re.compile(r'(?<!\|)\s\bBLOCKED\b(?!\s*\|)(?!\s*→)(?!\s*status)'),
        'bare BLOCKED in prose — reserved for true security denials (ADR-0003); '
        'use "gated" or "requires attestation" for WabbleSpec flow states',
        'error',
        False,
    ),
    (
        re.compile(r'\bPREFER\b.{0,50}\bOVER\b', re.IGNORECASE),
        'PREFER X OVER Y tradeoff framing — use WHEN: positive trigger instead',
        'warning',
        False,
    ),
    (
        # Match "Do not use", "do not write", etc. but NOT "**Do not use when:**"
        # (bold section headers) and NOT at start of a bold line
        re.compile(r'(?<!\*\*)\bDo not\s+(use|read|pull|write|call|run|invoke)\b(?! when\*\*)', re.IGNORECASE),
        'Do not [verb] inline imperative — rewrite as affirmative WHEN NOT condition',
        'error',
        False,
    ),
    (
        re.compile(r'\bNever use\b', re.IGNORECASE),
        'Never use — express as WHEN NOT condition instead',
        'error',
        False,
    ),
    (
        re.compile(r'\bSESSION STATE\b'),
        'SESSION STATE clause — role persistence belongs in hooks, not descriptions',
        'warning',
        False,
    ),
    (
        re.compile(r'[✅❌]'),
        '✅ or ❌ emoji — tokenizes inconsistently across LLM families',
        'warning',
        True,   # safe to remove mechanically
    ),
]

# Sections to check (routing-sensitive surface only)
ROUTING_SECTIONS = {
    'what this skill does',
    'when to use',
}

# Heading pattern to detect section boundaries
HEADING_RE = re.compile(r'^#{1,4}\s+(.+)', re.IGNORECASE)


def extract_routing_sections(text: str) -> list[tuple[int, str]]:
    """
    Return list of (line_number, line_text) pairs that belong to routing-
    sensitive sections (## What this skill does, ## When to use).
    Line numbers are 1-based.
    """
    result = []
    lines = text.splitlines()
    in_target = False
    in_code = False

    for i, line in enumerate(lines, start=1):
        # Track code fences
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue

        # Skip table rows
        stripped = line.strip()
        if stripped.startswith('|'):
            continue

        # Check for heading
        m = HEADING_RE.match(stripped)
        if m:
            heading = m.group(1).strip().lower().rstrip(':')
            in_target = heading in ROUTING_SECTIONS
            continue

        if in_target:
            result.append((i, line))

    return result


def extract_all_sections(text: str) -> list[tuple[int, str]]:
    """Return all non-code, non-table lines with line numbers (for --strict mode)."""
    result = []
    lines = text.splitlines()
    in_code = False
    for i, line in enumerate(lines, start=1):
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        stripped = line.strip()
        if stripped.startswith('|'):
            continue
        result.append((i, line))
    return result


def audit_lines(numbered_lines: list[tuple[int, str]], path: Path) -> list[dict]:
    """Check a list of (line_num, text) pairs against all forbidden patterns."""
    violations = []
    for line_num, line in numbered_lines:
        for pattern, message, severity, auto_fixable in FORBIDDEN:
            for match in pattern.finditer(line):
                violations.append({
                    'file': str(path),
                    'line': line_num,
                    'token': match.group(0).strip()[:40],
                    'message': message,
                    'severity': severity,
                    'auto_fixable': auto_fixable,
                })
    return violations


def audit_file(path: Path, strict: bool = False) -> list[dict]:
    try:
        raw = path.read_text(encoding='utf-8')
    except Exception as e:
        return [{'file': str(path), 'line': 0, 'token': 'READ_ERROR',
                 'message': str(e), 'severity': 'error', 'auto_fixable': False}]

    if strict:
        lines = extract_all_sections(raw)
    else:
        lines = extract_routing_sections(raw)

    return audit_lines(lines, path)


def fix_file(path: Path) -> int:
    """Auto-fix only safe (auto_fixable=True) violations. Returns count fixed."""
    try:
        raw = path.read_text(encoding='utf-8')
    except Exception:
        return 0
    fixed = raw
    count = 0
    for pattern, _, _, auto_fixable in FORBIDDEN:
        if not auto_fixable:
            continue
        new = pattern.sub('', fixed)
        if new != fixed:
            count += len(pattern.findall(fixed))
            fixed = new
    if fixed != raw:
        path.write_text(fixed, encoding='utf-8')
    return count


def find_skill_files(root: Path, single: Path | None) -> list[Path]:
    if single:
        return [single] if single.exists() else []
    return sorted(root.glob('modules/**/SKILL.md'))


def main():
    parser = argparse.ArgumentParser(
        description='Audit SKILL.md routing sections for LLM-hostile language'
    )
    parser.add_argument('--module', type=Path, help='Audit a single SKILL.md file')
    parser.add_argument('--fix', action='store_true',
                        help='Auto-fix safe violations (✅/❌ removal only)')
    parser.add_argument('--verbose', action='store_true',
                        help='Show all files checked, not just violations')
    parser.add_argument('--json', action='store_true', dest='json_out',
                        help='Output machine-readable JSON')
    parser.add_argument('--strict', action='store_true',
                        help='Check all sections, not just routing-sensitive ones')
    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent
    files = find_skill_files(root, args.module)

    if not files:
        print('No SKILL.md files found.', file=sys.stderr)
        sys.exit(0)

    all_violations = []
    fixed_count = 0

    for f in files:
        if args.fix:
            fixed_count += fix_file(f)
        violations = audit_file(f, strict=args.strict)
        all_violations.extend(violations)
        if args.verbose and not violations:
            print(f'  CLEAN  {f}')

    errors   = [v for v in all_violations if v['severity'] == 'error']
    warnings = [v for v in all_violations if v['severity'] == 'warning']

    if args.json_out:
        print(json.dumps({
            'files_checked': len(files),
            'total_violations': len(all_violations),
            'errors': len(errors),
            'warnings': len(warnings),
            'fixed': fixed_count,
            'violations': all_violations,
        }, indent=2))
        sys.exit(1 if errors else 0)

    # Human-readable output
    if all_violations:
        mode = '(all sections)' if args.strict else '(routing sections only)'
        print(f'\nActivator audit {mode} — {len(files)} files checked\n')
        for v in all_violations:
            try:
                rel = Path(v['file']).relative_to(root)
            except ValueError:
                rel = Path(v['file'])
            tag = 'ERROR  ' if v['severity'] == 'error' else 'WARNING'
            fix_tag = ' [auto-fixable with --fix]' if v['auto_fixable'] else ''
            print(f'  {tag}  {rel}:{v["line"]}')
            print(f'         token: {repr(v["token"])}')
            print(f'         {v["message"]}{fix_tag}')
            print()
        print(f'  {len(errors)} error(s)  {len(warnings)} warning(s)  across {len(files)} files')
        if fixed_count:
            print(f'  {fixed_count} auto-fix(es) applied')
        print()
    else:
        mode = '(all sections)' if args.strict else '(routing sections only)'
        print(f'CLEAN {mode} — {len(files)} SKILL.md files, 0 violations.')
        if fixed_count:
            print(f'  {fixed_count} auto-fix(es) applied')

    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
