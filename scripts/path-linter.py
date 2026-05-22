#!/usr/bin/env python3
"""
WabbleSpec path consistency linter.

Validates schema, module, and shared-reference path references in
spec-reference/planning/**/*.md against the module registry in framework.yaml.

Skips: runtime artifact paths (.wabblespec/receipts/, plans/, memory/, etc.),
       template placeholders (<timestamp>, <wave>, etc.),
       .wabblespec/ session files (recipe.json, scope.md, meta.md, etc.)

Exit 0 = no violations. Exit 1 = violations found.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).parent.parent

# Paths to scan — only check things that must match framework.yaml
CHECKABLE_PATTERNS = [
    re.compile(r'`(_shared/schemas/[^`\s<>]+)`'),
    re.compile(r'`(_shared/references/[^`\s<>]+)`'),
    re.compile(r'`(_shared/dev/[^`\s<>]+)`'),
    re.compile(r'`(modules/[^`\s<>]+)`'),
]

# Runtime paths that are valid but not registered in framework.yaml
RUNTIME_PREFIXES = (
    ".wabblespec/receipts/",
    ".wabblespec/plans/",
    ".wabblespec/memory/",
    ".wabblespec/checkpoints/",
    ".wabblespec/archive/",
    ".wabblespec/session/",
    ".wabblespec/runtime/",
    ".wabblespec/experiments/",
)

RUNTIME_FILES = {
    ".wabblespec/recipe.json",
    ".wabblespec/scope.md",
    ".wabblespec/meta.md",
    ".wabblespec/specs",
    ".wabblespec/VERSION",
    ".wabblespec/CHANGELOG.md",
    ".wabblespec/INDEX.md",
    ".wabblespec/plans/v61",
}

TEMPLATE_MARKER = re.compile(r'<[^>]+>')


def load_framework_yaml() -> dict:
    fw_path = REPO_ROOT / "framework.yaml"
    if not fw_path.exists():
        print(f"ERROR: framework.yaml not found at {fw_path}", file=sys.stderr)
        sys.exit(2)
    with open(fw_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_known_paths(fw: dict) -> set[str]:
    """All paths registered in framework.yaml, plus their directory prefixes."""
    paths = set()
    for schema in fw.get("shared", {}).get("schemas", []):
        paths.add(schema["path"].rstrip("/"))
    for ref in fw.get("shared", {}).get("references", []):
        paths.add(ref["path"].rstrip("/"))
    for module in fw.get("modules", []):
        paths.add(module["path"].rstrip("/"))
    # Add directory prefixes so e.g. `_shared/dev` matches `_shared/dev/languages/`
    prefixes = set()
    for p in paths:
        parts = Path(p).parts
        for i in range(1, len(parts)):
            prefixes.add(str(Path(*parts[:i])))
    return paths | prefixes


def normalize(raw: str) -> str:
    """Strip trailing slash, normalize separators."""
    return raw.replace("\\", "/").rstrip("/")


def is_runtime_path(raw: str) -> bool:
    if raw in RUNTIME_FILES:
        return True
    for prefix in RUNTIME_PREFIXES:
        if raw.startswith(prefix):
            return True
    if raw.startswith(".wabblespec/_shared/"):
        return True
    return False


def scan_markdown_files() -> dict[str, list[tuple[int, str]]]:
    results = {}
    spec_dir = REPO_ROOT / "spec-reference" / "planning"
    if not spec_dir.exists():
        return results
    for md_file in spec_dir.rglob("*.md"):
        hits = []
        with open(md_file, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                for pattern in CHECKABLE_PATTERNS:
                    for match in pattern.finditer(line):
                        raw = normalize(match.group(1))
                        if TEMPLATE_MARKER.search(raw):
                            continue
                        if is_runtime_path(raw):
                            continue
                        hits.append((lineno, raw))
        if hits:
            results[str(md_file.relative_to(REPO_ROOT))] = hits
    return results


def main() -> None:
    fw = load_framework_yaml()
    known = build_known_paths(fw)

    scanned = scan_markdown_files()
    violations = []
    checked = 0

    for filepath, hits in scanned.items():
        for lineno, raw in hits:
            checked += 1
            if raw in known:
                continue
            # Check prefix match
            if any(raw.startswith(k + "/") or raw == k for k in known):
                continue
            violations.append((filepath, lineno, raw))

    if violations:
        print(f"PATH LINTER — {len(violations)} violation(s) ({checked} paths checked)\n")
        current_file = None
        for filepath, lineno, raw in sorted(violations):
            if filepath != current_file:
                print(f"\n{filepath}:")
                current_file = filepath
            print(f"  line {lineno}: {raw!r}")
        sys.exit(1)
    else:
        print(f"PATH LINTER — OK. {checked} paths checked. No violations.")
        sys.exit(0)


if __name__ == "__main__":
    main()
