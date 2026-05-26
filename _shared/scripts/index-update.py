"""
index-update.py — Regenerate auto-managed sections in .wabblespec/INDEX.md.

Replaces Claude reading validate-graph output, quality-floor-check output,
receipt-index.json, and VERSION file to manually update specific sections of INDEX.md.
Each data source is already scriptable — this aggregates them.

Managed sections (overwritten on each run):
    ## Active Modules     — module count from framework.yaml
    ## Quality Floor      — pass rate from quality-floor-check.py (or framework.yaml stats)
    ## Receipt Archive    — entry count from receipt-index.json + receipts/ file count
    ## Witness            — entry count and date from archive/witness.json
    ## Version            — current VERSION file contents

Non-managed sections (never touched):
    ## L8 Gate, ## Cold-Start Coverage, ## Evolution Experiments,
    ## Planned Tasks, ## Hook System, ## Session State, ## Research Outputs,
    and any section not listed above.

Marker pattern used to identify managed content:
    <!-- auto-updated: index-update.py -->
    ...content...
    <!-- end auto-updated -->

On first run, wraps existing section content in markers. Subsequent runs replace
between markers. If markers are absent, replaces from section header to the next
## header or end of file.

Usage:
    # Update all managed sections:
    python _shared/scripts/index-update.py

    # Update only specific sections:
    python _shared/scripts/index-update.py --sections modules quality receipts witness version

    # Dry run — show what would be written:
    python _shared/scripts/index-update.py --dry-run

    # JSON summary only:
    python _shared/scripts/index-update.py --json

Exit codes:
    0  updated (or dry-run showed output)
    1  INDEX.md not found
    2  required data sources not readable
"""

import sys
import os
import re
import json
import argparse
import subprocess
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def find_wabblespec(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        ws = os.path.join(candidate, ".wabblespec")
        if os.path.isdir(ws):
            return ws
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def find_framework(start=None):
    candidate = start or os.getcwd()
    for _ in range(12):
        path = os.path.join(candidate, "framework.yaml")
        if os.path.isfile(path):
            return path
        parent = os.path.dirname(candidate)
        if parent == candidate:
            break
        candidate = parent
    return None


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

def gather_version(ws):
    version_path = os.path.join(ws, "VERSION")
    if not os.path.isfile(version_path):
        return None, "VERSION file not found"
    try:
        with open(version_path, encoding="utf-8") as f:
            return f.read().strip(), None
    except OSError as e:
        return None, str(e)


def gather_modules(framework_path):
    """Count modules from framework.yaml without importing pyyaml into this script."""
    if framework_path is None or not os.path.isfile(framework_path):
        return None, "framework.yaml not found"
    try:
        with open(framework_path, encoding="utf-8-sig") as f:
            content = f.read()
        # Count '  - id:' entries as a proxy for module count
        count = len(re.findall(r"^\s{2}- id:", content, re.MULTILINE))
        return count, None
    except OSError as e:
        return None, str(e)


def gather_quality(ws):
    """Run quality-floor-check.py and extract the pass count."""
    script = os.path.join(SCRIPT_DIR, "quality-floor-check.py")
    if not os.path.isfile(script):
        return None, None, "quality-floor-check.py not found"
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True, text=True, cwd=os.path.dirname(ws)
        )
        output = result.stdout
        # Pattern: "96/99 modules pass both gates" or "X/Y modules"
        m = re.search(r"(\d+)/(\d+)\s+modules?\s+pass", output, re.IGNORECASE)
        if m:
            return int(m.group(1)), int(m.group(2)), None
        # Fallback: just count lines
        return None, None, f"Could not parse quality-floor-check output: {output[:200]}"
    except Exception as e:
        return None, None, str(e)


def gather_receipts(ws):
    """Count receipt-index.json entries and receipts/ directory files."""
    index_path = os.path.join(ws, "archive", "receipt-index.json")
    receipts_dir = os.path.join(ws, "receipts")

    index_count = None
    receipts_count = None

    if os.path.isfile(index_path):
        try:
            with open(index_path, encoding="utf-8") as f:
                data = json.load(f)
            # Support both formats:
            # - {"tasks": [...]} (current format)
            # - {"entries": [...]} (alternate)
            # - [...]  (bare list)
            entries = (data.get("tasks") or
                       data.get("entries") or
                       (data if isinstance(data, list) else None))
            index_count = len(entries) if isinstance(entries, (list, dict)) else None
        except (OSError, json.JSONDecodeError):
            pass

    if os.path.isdir(receipts_dir):
        receipts_count = len([
            f for f in os.listdir(receipts_dir) if f.endswith(".json")
        ])

    return index_count, receipts_count


def gather_witness(ws):
    """Read archive/witness.json for module count and date."""
    witness_path = os.path.join(ws, "archive", "witness.json")
    if not os.path.isfile(witness_path):
        return None, None
    try:
        with open(witness_path, encoding="utf-8") as f:
            data = json.load(f)
        recorded_at = data.get("recorded_at", "")
        # Count entries in the modules dict
        modules = data.get("modules", {})
        count = len(modules)
        return count, recorded_at
    except (OSError, json.JSONDecodeError):
        return None, None


# ---------------------------------------------------------------------------
# Section content builders
# ---------------------------------------------------------------------------

def build_version_content(ws):
    version, err = gather_version(ws)
    if err:
        return f"Current: (error reading VERSION: {err})", False
    return f"Current: {version}", True


def build_modules_content(framework_path, ws):
    count, err = gather_modules(framework_path)
    if err:
        return f"(error: {err})", False
    return (
        f"{count} modules registered in `framework.yaml`. "
        f"See `framework.yaml` for canonical registry — this file tracks session-level state only."
    ), True


def build_quality_content(ws):
    passed, total, err = gather_quality(ws)
    if err or passed is None:
        # Fallback: just report from framework.yaml count
        framework_path = find_framework(os.path.dirname(ws))
        count, ferr = gather_modules(framework_path)
        if count:
            return (
                f"Quality floor status: see `quality-floor-check.py` output. "
                f"({count} modules registered)"
            ), True
        return f"(could not gather quality data: {err})", False
    return (
        f"{passed}/{total} modules PASS both gates "
        f"(run `python _shared/scripts/quality-floor-check.py` for detail)."
    ), True


def build_receipts_content(ws):
    index_count, receipts_count = gather_receipts(ws)
    parts = []
    if index_count is not None:
        parts.append(f"Completed tasks: `.wabblespec/archive/receipt-index.json` ({index_count} entries).")
    if receipts_count is not None:
        parts.append(
            f"Seed pipeline receipts: `.wabblespec/receipts/` — "
            f"{receipts_count} individual receipts accumulated."
        )
    if not parts:
        return "(could not read receipt data)", False
    return "\n\n".join(parts), True


def build_witness_content(ws):
    count, recorded_at = gather_witness(ws)
    if count is None:
        return (
            "Module file integrity witness: `.wabblespec/archive/witness.json` (not yet recorded). "
            "Run `python _shared/scripts/validate-graph.py --record-witness` to create."
        ), True
    date_str = recorded_at[:10] if recorded_at and len(recorded_at) >= 10 else recorded_at
    return (
        f"Module file integrity witness recorded at `.wabblespec/archive/witness.json` "
        f"({count} modules, {date_str}). "
        f"Re-record after any intentional module file change with "
        f"`python _shared/scripts/validate-graph.py --record-witness`. "
        f"Check drift with `--check-hashes`."
    ), True


SECTION_BUILDERS = {
    "modules": ("## Active Modules", build_modules_content),
    "quality": ("## Quality Floor", build_quality_content),
    "receipts": ("## Receipt Archive", build_receipts_content),
    "witness": ("## Witness", build_witness_content),
    "version": ("## Version", build_version_content),
}


# ---------------------------------------------------------------------------
# INDEX.md patching
# ---------------------------------------------------------------------------

BEGIN_MARKER = "<!-- auto-updated: index-update.py -->"
END_MARKER = "<!-- end auto-updated -->"

BEGIN_RE = re.compile(r"^<!-- auto-updated: index-update\.py -->$")
END_RE = re.compile(r"^<!-- end auto-updated -->$")
SECTION_H2 = re.compile(r"^## ")


def patch_section(lines, section_header, new_content):
    """
    Find the section_header in lines, replace managed block with new_content.
    Returns modified lines list and True/False for whether a change was made.
    """
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip() == section_header.strip():
            header_idx = i
            break

    if header_idx is None:
        return lines, False  # Section not found

    # Check if there's already a managed block
    begin_idx = None
    end_idx = None
    next_h2 = None

    for i in range(header_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if BEGIN_RE.match(stripped) and begin_idx is None:
            begin_idx = i
        if END_RE.match(stripped) and begin_idx is not None:
            end_idx = i
            break
        if SECTION_H2.match(stripped) and begin_idx is None:
            next_h2 = i
            break

    new_block = [
        BEGIN_MARKER,
        new_content,
        END_MARKER,
    ]

    if begin_idx is not None and end_idx is not None:
        # Replace between markers (inclusive)
        new_lines = lines[:begin_idx] + new_block + lines[end_idx + 1:]
    elif next_h2 is not None:
        # Replace from header+1 to next_h2 (exclusive)
        # Insert managed block between header and next section
        before = lines[:header_idx + 1]
        after = lines[next_h2:]
        # Preserve any blank line after header
        blank = [""]
        new_lines = before + blank + new_block + [""] + after
    else:
        # Section is at end of file or no next header
        # Replace from header+1 to end
        before = lines[:header_idx + 1]
        blank = [""]
        new_lines = before + blank + new_block + [""]

    return new_lines, True


def read_index(index_path):
    try:
        with open(index_path, encoding="utf-8") as f:
            return f.read().splitlines(keepends=False)
    except OSError as e:
        print(f"ERROR: Cannot read {index_path}: {e}", file=sys.stderr)
        sys.exit(1)


def write_index(index_path, lines, dry_run=False):
    text = "\n".join(lines)
    if not text.endswith("\n"):
        text += "\n"
    if dry_run:
        print(f"--- [DRY RUN] {index_path} ---")
        print(text[:3000])
        if len(text) > 3000:
            print(f"... ({len(text) - 3000} chars truncated)")
        return
    tmp = index_path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, index_path)
    except OSError as e:
        print(f"ERROR: Cannot write {index_path}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Updated {index_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Regenerate auto-managed sections in .wabblespec/INDEX.md.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--sections", nargs="*",
                        choices=list(SECTION_BUILDERS.keys()),
                        default=list(SECTION_BUILDERS.keys()),
                        help="Which sections to update (default: all).")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="emit_json")
    parser.add_argument("--wabblespec-dir", metavar="PATH")

    args = parser.parse_args()

    ws = args.wabblespec_dir or find_wabblespec()
    if ws is None:
        print("ERROR: Cannot find .wabblespec/. Run from inside the repo.", file=sys.stderr)
        sys.exit(1)

    index_path = os.path.join(ws, "INDEX.md")
    if not os.path.isfile(index_path):
        print(f"ERROR: INDEX.md not found at {index_path}", file=sys.stderr)
        sys.exit(1)

    framework_path = find_framework(os.path.dirname(ws))

    # Build content for each requested section
    section_results = {}
    for key in args.sections:
        header, builder_fn = SECTION_BUILDERS[key]
        if key in ("modules",):
            content, ok = builder_fn(framework_path, ws)
        else:
            content, ok = builder_fn(ws)
        section_results[key] = {
            "header": header,
            "content": content,
            "ok": ok,
        }

    if args.emit_json:
        summary = {
            "index_path": index_path,
            "sections_updated": list(args.sections),
            "data": {
                k: {"content_preview": v["content"][:100], "ok": v["ok"]}
                for k, v in section_results.items()
            },
        }
        print(json.dumps(summary, indent=2))
        sys.exit(0)

    # Read and patch INDEX.md
    lines = read_index(index_path)
    changed_sections = []

    for key, info in section_results.items():
        if not info["ok"]:
            print(f"  WARN  {key}: {info['content']}")
            continue
        lines, changed = patch_section(lines, info["header"], info["content"])
        if changed:
            changed_sections.append(key)
            print(f"  OK    {info['header']}")
        else:
            print(f"  SKIP  {info['header']} (section not found in INDEX.md)")

    if changed_sections:
        write_index(index_path, lines, dry_run=args.dry_run)
        if not args.dry_run:
            print(f"\nUpdated sections: {', '.join(changed_sections)}")
    else:
        print("\nNo sections updated (none found or no changes needed).")

    sys.exit(0)


if __name__ == "__main__":
    main()
