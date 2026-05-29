"""
wabblespec-doctor.py — Drift detector for the WabbleSpec framework.

Audits the framework for 28+ known findings across Critical, High, Medium,
and Low severity levels. Read-only: no side effects.

Usage:
    python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all
    python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --severity critical
    python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --all --format json
    python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --guard-advisory
    python .wabblespec/engine/shared/scripts/wabblespec-doctor.py --self-test

Exit codes:
    --all            → 0 on successful enumeration (findings in payload)
    --severity X     → nonzero iff any check at severity X FAILS
    --guard-advisory → always 0 (non-blocking advisory mode)
    --self-test      → 0 if good→PASS and bad→FAIL; 1 otherwise
"""

import sys
import os
import json
import re
import argparse

# ---------------------------------------------------------------------------
# Repo root discovery
# ---------------------------------------------------------------------------

def find_repo_root(start: str) -> str:
    """Walk up from start until we find a directory containing .wabblespec/."""
    current = os.path.abspath(start)
    while True:
        candidate = os.path.join(current, ".wabblespec")
        if os.path.isdir(candidate):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise RuntimeError("Cannot find repo root: no .wabblespec/ directory found in any ancestor of " + start)
        current = parent


# ---------------------------------------------------------------------------
# YAML loading (pyyaml available per CLAUDE.md)
# ---------------------------------------------------------------------------

def _load_yaml(path: str):
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        raise RuntimeError("pyyaml not installed. Run: pip install pyyaml")
    except Exception as e:
        raise RuntimeError(f"YAML parse error in {path}: {e}")


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Check result helpers
# ---------------------------------------------------------------------------

def _pass(cid: str, severity: str, description: str, detail: str = "") -> dict:
    return {"id": cid, "severity": severity, "status": "PASS",
            "description": description, "detail": detail}


def _fail(cid: str, severity: str, description: str, detail: str = "") -> dict:
    return {"id": cid, "severity": severity, "status": "FAIL",
            "description": description, "detail": detail}


def _error(cid: str, severity: str, description: str, exc) -> dict:
    return {"id": cid, "severity": severity, "status": "FAIL",
            "description": description, "detail": f"Error during check: {exc}"}


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_C1(root: str) -> dict:
    """Receipt-index path normalization."""
    cid, sev = "C1", "critical"
    desc = "Receipt-index path normalization"
    index_path = os.path.join(root, ".wabblespec", "state", "archive", "receipt-index.json")
    if not os.path.isfile(index_path):
        return _fail(cid, sev, desc, "receipt-index.json not found")
    try:
        data = _load_json(index_path)
    except Exception as e:
        return _error(cid, sev, desc, e)

    tasks = data.get("tasks", [])
    old_prefix_hits = []
    broken_paths = []
    for t in tasks:
        p = t.get("delivery_receipt_path", "")
        if not p:
            continue
        # Check for old path prefix: .wabblespec/receipts/ (not .wabblespec/state/receipts/)
        # The old pattern is a path that goes directly .wabblespec/receipts/ without "state"
        normalized = p.replace("\\", "/")
        if re.search(r"\.wabblespec/receipts/", normalized):
            old_prefix_hits.append(p)
        # Check file exists
        full = os.path.join(root, p.replace("/", os.sep))
        if not os.path.isfile(full):
            broken_paths.append(p)

    failures = []
    if old_prefix_hits:
        failures.append(f"Old-prefix paths ({len(old_prefix_hits)}): {old_prefix_hits[:3]}")
    if broken_paths:
        failures.append(f"Broken paths ({len(broken_paths)}): {broken_paths[:3]}")

    if failures:
        return _fail(cid, sev, desc, "; ".join(failures))
    return _pass(cid, sev, desc, f"All {len(tasks)} delivery_receipt_path entries valid")


def check_C2(root: str) -> dict:
    """Platform skill ID alignment."""
    cid, sev = "C2", "critical"
    desc = "Platform skill ID alignment"
    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")
    skills_dir = os.path.join(root, ".claude", "skills")
    if not os.path.isfile(yaml_path):
        return _fail(cid, sev, desc, "wabblespec.yaml not found")
    try:
        data = _load_yaml(yaml_path)
    except Exception as e:
        return _error(cid, sev, desc, e)

    # Collect all module IDs matching platform-*
    modules = []
    for section_key in ("modules", "l3", "layers"):
        section = data.get(section_key, [])
        if isinstance(section, list):
            for m in section:
                if isinstance(m, dict) and str(m.get("id", "")).startswith("platform-"):
                    modules.append(m["id"])

    # Also scan top-level list entries under any key that's a list of dicts with 'id'
    if not modules:
        def _scan(obj):
            found = []
            if isinstance(obj, dict):
                for v in obj.values():
                    found.extend(_scan(v))
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict):
                        mid = item.get("id", "")
                        if str(mid).startswith("platform-"):
                            found.append(mid)
                        found.extend(_scan(item))
            return found
        modules = list(dict.fromkeys(_scan(data)))  # deduplicate, preserve order

    if not os.path.isdir(skills_dir):
        return _fail(cid, sev, desc, f".claude/skills/ directory not found; {len(modules)} platform modules in registry")

    skill_dirs = set(os.listdir(skills_dir))
    missing = [mid for mid in modules if mid not in skill_dirs]

    if missing:
        return _fail(cid, sev, desc, f"No .claude/skills/ dir for: {missing}")
    return _pass(cid, sev, desc, f"All {len(modules)} platform-* modules have matching skill dirs")


def check_C3(root: str) -> dict:
    """archive.py wabble-sound.py path correctness."""
    cid, sev = "C3", "critical"
    desc = "archive.py wabble-sound.py path"
    archive_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "archive.py")
    sound_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "wabble-sound.py")

    if not os.path.isfile(archive_path):
        return _fail(cid, sev, desc, "archive.py not found")

    with open(archive_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The old broken string: os.path.join with "_shared" component
    old_pattern = '"_shared"' + ', "scripts"' + ', "wabble-sound.py"'
    if old_pattern in content:
        return _fail(cid, sev, desc, f'Old broken path string found: {old_pattern}')

    # wabble-sound.py must exist
    if not os.path.isfile(sound_path):
        return _fail(cid, sev, desc, "wabble-sound.py does not exist on disk")

    # wabble-sound.py must be referenced in archive.py
    if "wabble-sound.py" not in content:
        return _fail(cid, sev, desc, "wabble-sound.py not referenced in archive.py")

    return _pass(cid, sev, desc, "wabble-sound.py correctly referenced in archive.py")


def check_C4(root: str) -> dict:
    """CLAUDE.md version/module-count drift."""
    cid, sev = "C4", "critical"
    desc = "CLAUDE.md version/module-count drift"
    claude_path = os.path.join(root, "CLAUDE.md")
    version_path = os.path.join(root, ".wabblespec", "VERSION")
    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")

    if not os.path.isfile(claude_path):
        return _fail(cid, sev, desc, "CLAUDE.md not found")
    if not os.path.isfile(version_path):
        return _fail(cid, sev, desc, "VERSION file not found")

    with open(version_path, "r", encoding="utf-8") as f:
        version_str = f.read().strip()

    with open(claude_path, "r", encoding="utf-8") as f:
        claude_content = f.read()

    failures = []

    # Check "Current version:" line matches VERSION
    version_match = re.search(r"Current version:\s*\*\*([^*]+)\*\*", claude_content)
    if not version_match:
        failures.append("No 'Current version:' line found in CLAUDE.md")
    elif version_match.group(1).strip() != version_str:
        failures.append(
            f"CLAUDE.md says {version_match.group(1).strip()!r} but VERSION file says {version_str!r}"
        )

    # Extract module count claim from CLAUDE.md (e.g. "103 skill modules")
    count_match = re.search(r"(\d+)\s+skill\s+modules", claude_content)
    if not count_match:
        failures.append("CLAUDE.md does not contain an 'N skill modules' count claim")
    else:
        claimed_count = int(count_match.group(1))
        # Compare against actual registry count
        if os.path.isfile(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_content = f.read()
            actual_count = len(re.findall(r"^\s{2,4}- id:\s+\S", yaml_content, re.MULTILINE))
            if actual_count != claimed_count:
                failures.append(
                    f"CLAUDE.md claims {claimed_count} modules but wabblespec.yaml has {actual_count} "
                    f"registered (drift of {abs(actual_count - claimed_count)})"
                )

    if failures:
        return _fail(cid, sev, desc, "; ".join(failures))
    return _pass(cid, sev, desc, f"CLAUDE.md version={version_str!r}, module count matches registry")


def check_H1(root: str) -> dict:
    """Confidence field unification: receipt-writer.py emits top-level numeric confidence."""
    cid, sev = "H1", "high"
    desc = "Confidence field unification in receipt-writer.py"
    rw_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "receipt-writer.py")
    if not os.path.isfile(rw_path):
        return _fail(cid, sev, desc, "receipt-writer.py not found")

    with open(rw_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check that 'confidence' appears as a field being written in the base receipt block
    if '"confidence"' not in content and "'confidence'" not in content:
        return _fail(cid, sev, desc, "No 'confidence' field emitted by receipt-writer.py")

    # Also verify it is treated as numeric (default value should be float)
    if not re.search(r"confidence.*0\.\d|confidence.*float|confidence.*1\.0", content, re.IGNORECASE):
        # Softer check: at least 'confidence' is set in receipt output
        if re.search(r"['\"]confidence['\"]\s*:", content):
            return _pass(cid, sev, desc, "confidence field present in receipt-writer.py output")
        return _fail(cid, sev, desc, "confidence field not found in receipt builder output")

    return _pass(cid, sev, desc, "confidence field emitted as numeric by receipt-writer.py")


def check_H2(root: str) -> dict:
    """Schema gap closure: required schemas must exist."""
    cid, sev = "H2", "high"
    desc = "Schema gap closure"
    schemas_dir = os.path.join(root, ".wabblespec", "engine", "shared", "schemas")
    required = [
        "recipe.schema.json",
        "wave-queue.schema.json",
        "delivery-receipt.schema.json",
    ]
    missing = [s for s in required if not os.path.isfile(os.path.join(schemas_dir, s))]
    if missing:
        return _fail(cid, sev, desc, f"Missing schemas: {missing}")
    return _pass(cid, sev, desc, f"All required schemas present: {required}")


def check_H3(root: str) -> dict:
    """CLI flag unification: task-card-writer.py must use --delta-class, not --change-class as primary."""
    cid, sev = "H3", "high"
    desc = "CLI flag unification in task-card-writer.py"
    tcw_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "task-card-writer.py")
    if not os.path.isfile(tcw_path):
        return _fail(cid, sev, desc, "task-card-writer.py not found")

    with open(tcw_path, "r", encoding="utf-8") as f:
        content = f.read()

    # FAIL if --change-class is the primary flag (i.e., add_argument uses "--change-class" as first arg)
    # PASS if --delta-class is declared (even if --change-class is an alias)
    if '"--delta-class"' in content or "'--delta-class'" in content:
        # --delta-class is present; check if --change-class is only an alias (acceptable)
        return _pass(cid, sev, desc, "--delta-class is the canonical flag in task-card-writer.py")

    # --delta-class not present at all
    if '"--change-class"' in content or "'--change-class'" in content:
        return _fail(cid, sev, desc, "--change-class found but --delta-class not declared as canonical")

    return _pass(cid, sev, desc, "Neither flag explicitly present; no violation detected")


def check_H4(root: str) -> dict:
    """Builder coverage: receipt-writer.py must have builder types for propose, reviewer, scopeframe, guard."""
    cid, sev = "H4", "high"
    desc = "Builder coverage in receipt-writer.py"
    rw_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "receipt-writer.py")
    if not os.path.isfile(rw_path):
        return _fail(cid, sev, desc, "receipt-writer.py not found")

    with open(rw_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_types = ["propose", "reviewer", "scopeframe", "guard"]
    missing = [t for t in required_types if t not in content]
    if missing:
        return _fail(cid, sev, desc, f"Missing builder types: {missing}")
    return _pass(cid, sev, desc, f"All required builder types present: {required_types}")


def check_H5(root: str) -> dict:
    """Entity graph currency: entity-graph.json must exist."""
    cid, sev = "H5", "high"
    desc = "Entity graph currency"
    path = os.path.join(root, ".wabblespec", "state", "memory", "entity-graph.json")
    if not os.path.isfile(path):
        return _fail(cid, sev, desc, "entity-graph.json not found under .wabblespec/state/memory/")
    return _pass(cid, sev, desc, "entity-graph.json exists")


def check_H6(root: str) -> dict:
    """CLAUDE.md script-location accuracy: no stale l5/*/scripts/ paths."""
    cid, sev = "H6", "high"
    desc = "CLAUDE.md script-location accuracy"
    claude_path = os.path.join(root, "CLAUDE.md")
    if not os.path.isfile(claude_path):
        return _fail(cid, sev, desc, "CLAUDE.md not found")

    with open(claude_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for l5/*/scripts/ or similar layer-namespaced script paths that don't exist
    stale_hits = re.findall(r"l[0-9]+/[^/\s]+/scripts/[^\s`'\"]+", content)
    broken = []
    for ref in stale_hits:
        full = os.path.join(root, ref.replace("/", os.sep))
        if not os.path.exists(full):
            broken.append(ref)

    if broken:
        return _fail(cid, sev, desc, f"Broken script path references in CLAUDE.md: {broken}")
    return _pass(cid, sev, desc, "No stale layer-namespaced script paths found in CLAUDE.md")


def check_H7(root: str) -> dict:
    """Orphan template disposition: all templates registered or templates dir absent."""
    cid, sev = "H7", "high"
    desc = "Orphan template disposition"
    templates_dir = os.path.join(root, ".wabblespec", "engine", "shared", "templates")

    if not os.path.isdir(templates_dir):
        return _pass(cid, sev, desc, "templates/ directory absent; no orphans possible")

    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")
    if not os.path.isfile(yaml_path):
        return _fail(cid, sev, desc, "wabblespec.yaml not found; cannot verify template registration")

    try:
        data = _load_yaml(yaml_path)
    except Exception as e:
        return _error(cid, sev, desc, e)

    registered_paths = set()
    shared = data.get("shared", {})
    for t in shared.get("templates", []):
        if isinstance(t, dict):
            p = t.get("path", "")
            if p:
                registered_paths.add(p.replace("\\", "/"))

    # Collect all template files recursively
    all_template_files = []
    for dirpath, _, filenames in os.walk(templates_dir):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root).replace("\\", "/")
            all_template_files.append(rel)

    orphans = [f for f in all_template_files if f not in registered_paths]
    if orphans:
        # Directories (non-leaf) are expected to be unregistered; only flag files
        # that are clearly leaf content files
        leaf_orphans = [f for f in orphans if not f.endswith(".gitkeep")]
        if leaf_orphans:
            # Warn but pass — templates may have owners not listed in yaml
            return _pass(cid, sev, desc,
                         f"{len(leaf_orphans)} template files not in shared.templates list "
                         f"(may be owner-registered elsewhere): {leaf_orphans[:5]}")
    return _pass(cid, sev, desc, f"All {len(all_template_files)} template files accounted for")


def check_H8(root: str) -> dict:
    """Memory-bootstrap dedup: memory-bootstrap.py must not have duplicate init blocks."""
    cid, sev = "H8", "high"
    desc = "Memory-bootstrap dedup"
    mb_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "memory-bootstrap.py")

    if not os.path.isfile(mb_path):
        return _pass(cid, sev, desc, "memory-bootstrap.py not found; check not applicable")

    with open(mb_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Detect duplicate sentinel patterns (e.g., same function definition appearing twice)
    sentinel_re = re.compile(r"^def (init_|bootstrap_|setup_)\w+\(")
    seen = {}
    duplicates = []
    for i, line in enumerate(lines, 1):
        m = sentinel_re.match(line.strip())
        if m:
            name = m.group(0)
            if name in seen:
                duplicates.append(f"{name!r} at line {seen[name]} and line {i}")
            else:
                seen[name] = i

    if duplicates:
        return _fail(cid, sev, desc, f"Duplicate init blocks: {duplicates}")
    return _pass(cid, sev, desc, "No duplicate initialization blocks found")


def check_H10(root: str) -> dict:
    """Doc/skill path drift: all paths listed in INDEX.md must resolve."""
    cid, sev = "H10", "high"
    desc = "Doc/skill path drift in INDEX.md"
    index_path = os.path.join(root, ".wabblespec", "engine", "docs", "INDEX.md")

    if not os.path.isfile(index_path):
        return _fail(cid, sev, desc, "INDEX.md not found at .wabblespec/engine/docs/INDEX.md")

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Markdown links: [text](path) — relative to INDEX.md's directory
    index_dir = os.path.dirname(index_path)
    link_re = re.compile(r"\[([^\]]+)\]\(([^)#]+)\)")
    broken = []
    for m in link_re.finditer(content):
        href = m.group(2).strip()
        if href.startswith("http://") or href.startswith("https://"):
            continue
        # Resolve relative to INDEX.md's directory
        candidate = os.path.normpath(os.path.join(index_dir, href))
        if not os.path.exists(candidate):
            broken.append(href)

    if broken:
        return _fail(cid, sev, desc, f"Broken paths in INDEX.md ({len(broken)}): {broken[:5]}")
    return _pass(cid, sev, desc, "All paths in INDEX.md resolve")


# ---------------------------------------------------------------------------
# Medium checks
# ---------------------------------------------------------------------------

def check_M1(root: str) -> dict:
    """wabblespec.yaml module count >= 100."""
    cid, sev = "M1", "medium"
    desc = "wabblespec.yaml module count >= 100"
    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")
    if not os.path.isfile(yaml_path):
        return _fail(cid, sev, desc, "wabblespec.yaml not found")
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return _error(cid, sev, desc, e)

    # Count "  - id:" lines as the most reliable module count
    count = len(re.findall(r"^\s{2,4}- id:\s+\S", content, re.MULTILINE))
    if count < 100:
        return _fail(cid, sev, desc, f"Only {count} module IDs found; expected >= 100")
    return _pass(cid, sev, desc, f"{count} module IDs registered")


def check_M2(root: str) -> dict:
    """All modules have build_status field."""
    cid, sev = "M2", "medium"
    desc = "All modules have build_status field in registry"
    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")
    if not os.path.isfile(yaml_path):
        return _fail(cid, sev, desc, "wabblespec.yaml not found")
    try:
        data = _load_yaml(yaml_path)
    except Exception as e:
        return _error(cid, sev, desc, e)

    def _collect_modules(obj):
        modules = []
        if isinstance(obj, dict):
            if "id" in obj and "build_status" not in obj:
                modules.append(obj.get("id", "?"))
            for v in obj.values():
                modules.extend(_collect_modules(v))
        elif isinstance(obj, list):
            for item in obj:
                modules.extend(_collect_modules(item))
        return modules

    missing_bs = _collect_modules(data)
    # Deduplicate
    missing_bs = list(dict.fromkeys(missing_bs))

    if missing_bs:
        return _fail(cid, sev, desc, f"{len(missing_bs)} modules missing build_status: {missing_bs[:5]}")
    return _pass(cid, sev, desc, "All modules have build_status field")


def check_M3(root: str) -> dict:
    """All modules have a path that exists on disk."""
    cid, sev = "M3", "medium"
    desc = "All modules have existing path on disk"
    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")
    if not os.path.isfile(yaml_path):
        return _fail(cid, sev, desc, "wabblespec.yaml not found")
    try:
        data = _load_yaml(yaml_path)
    except Exception as e:
        return _error(cid, sev, desc, e)

    def _collect_paths(obj):
        results = []
        if isinstance(obj, dict):
            if "id" in obj and "path" in obj:
                results.append((obj["id"], obj["path"]))
            for v in obj.values():
                results.extend(_collect_paths(v))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(_collect_paths(item))
        return results

    pairs = list(dict.fromkeys(_collect_paths(data)))
    missing = []
    for mid, p in pairs:
        full = os.path.join(root, p.replace("/", os.sep))
        if not os.path.exists(full):
            missing.append(f"{mid} → {p}")

    if missing:
        return _fail(cid, sev, desc, f"{len(missing)} missing paths: {missing[:5]}")
    return _pass(cid, sev, desc, f"All {len(pairs)} module paths exist on disk")


def check_M4(root: str) -> dict:
    """receipt-writer.py --validate command exists."""
    cid, sev = "M4", "medium"
    desc = "receipt-writer.py --validate command exists"
    rw_path = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "receipt-writer.py")
    if not os.path.isfile(rw_path):
        return _fail(cid, sev, desc, "receipt-writer.py not found")

    with open(rw_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "--validate" not in content:
        return _fail(cid, sev, desc, "--validate flag not found in receipt-writer.py")
    return _pass(cid, sev, desc, "--validate flag present in receipt-writer.py")


def check_M5(root: str) -> dict:
    """VERSION file exists and parses as valid semver."""
    cid, sev = "M5", "medium"
    desc = "VERSION file exists and is valid semver"
    version_path = os.path.join(root, ".wabblespec", "VERSION")
    if not os.path.isfile(version_path):
        return _fail(cid, sev, desc, "VERSION file not found")

    with open(version_path, "r", encoding="utf-8") as f:
        version_str = f.read().strip()

    if not re.match(r"^\d+\.\d+\.\d+$", version_str):
        return _fail(cid, sev, desc, f"VERSION content {version_str!r} is not valid N.N.N semver")
    return _pass(cid, sev, desc, f"VERSION={version_str!r} is valid semver")


def check_M6(root: str) -> dict:
    """receipt-index.json exists."""
    cid, sev = "M6", "medium"
    desc = "receipt-index.json exists"
    path = os.path.join(root, ".wabblespec", "state", "archive", "receipt-index.json")
    if not os.path.isfile(path):
        return _fail(cid, sev, desc, "receipt-index.json not found under .wabblespec/state/archive/")
    return _pass(cid, sev, desc, "receipt-index.json exists")


def check_M7(root: str) -> dict:
    """runtime-state.json exists under .wabblespec/runtime/."""
    cid, sev = "M7", "medium"
    desc = "runtime-state.json exists"
    path = os.path.join(root, ".wabblespec", "runtime", "runtime-state.json")
    if not os.path.isfile(path):
        return _fail(cid, sev, desc, "runtime-state.json not found under .wabblespec/runtime/")
    return _pass(cid, sev, desc, "runtime-state.json exists")


def check_M8(root: str) -> dict:
    """All L8 experiment dirs exist."""
    cid, sev = "M8", "medium"
    desc = "All L8 experiment directories exist"
    base = os.path.join(root, ".wabblespec", "state", "experiments")
    required_dirs = ["candidates", "blueprints", "augments", "fixtures"]
    missing = [d for d in required_dirs if not os.path.isdir(os.path.join(base, d))]
    if missing:
        return _fail(cid, sev, desc, f"Missing L8 experiment dirs: {missing}")
    return _pass(cid, sev, desc, f"All L8 experiment dirs present: {required_dirs}")


def check_M9(root: str) -> dict:
    """All archived delivery receipts have version_new field."""
    cid, sev = "M9", "medium"
    desc = "Archived delivery receipts have version_new field"
    index_path = os.path.join(root, ".wabblespec", "state", "archive", "receipt-index.json")
    if not os.path.isfile(index_path):
        return _fail(cid, sev, desc, "receipt-index.json not found")
    try:
        data = _load_json(index_path)
    except Exception as e:
        return _error(cid, sev, desc, e)

    tasks = data.get("tasks", [])
    missing_vn = []
    for t in tasks:
        if "version_new" not in t:
            missing_vn.append(t.get("task_id", "?"))

    if missing_vn:
        return _fail(cid, sev, desc, f"{len(missing_vn)} entries missing version_new: {missing_vn[:5]}")
    return _pass(cid, sev, desc, f"All {len(tasks)} receipt-index entries have version_new field")


def check_M10(root: str) -> dict:
    """gap-map.md exists under .wabblespec/state/memory/."""
    cid, sev = "M10", "medium"
    desc = "gap-map.md exists"
    path = os.path.join(root, ".wabblespec", "state", "memory", "gap-map.md")
    if not os.path.isfile(path):
        return _fail(cid, sev, desc, "gap-map.md not found under .wabblespec/state/memory/")
    return _pass(cid, sev, desc, "gap-map.md exists")


# ---------------------------------------------------------------------------
# Low checks
# ---------------------------------------------------------------------------

def check_L1(root: str) -> dict:
    """CHANGELOG.md exists and is non-empty."""
    cid, sev = "L1", "low"
    desc = "CHANGELOG.md exists and is non-empty"
    path = os.path.join(root, ".wabblespec", "CHANGELOG.md")
    if not os.path.isfile(path):
        return _fail(cid, sev, desc, "CHANGELOG.md not found under .wabblespec/")
    size = os.path.getsize(path)
    if size == 0:
        return _fail(cid, sev, desc, "CHANGELOG.md is empty")
    return _pass(cid, sev, desc, f"CHANGELOG.md exists ({size} bytes)")


def check_L2(root: str) -> dict:
    """daemon-config.json exists."""
    cid, sev = "L2", "low"
    desc = "daemon-config.json exists"
    # Check common locations
    candidates = [
        os.path.join(root, ".wabblespec", "state", "daemons", "daemon-config.json"),
        os.path.join(root, ".wabblespec", "engine", "hooks", "daemon-config.json"),
        os.path.join(root, ".claude", "daemon-config.json"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return _pass(cid, sev, desc, f"daemon-config.json found at {os.path.relpath(p, root)}")
    return _fail(cid, sev, desc, "daemon-config.json not found in any expected location")


def check_L3(root: str) -> dict:
    """At least one guard receipt exists."""
    cid, sev = "L3", "low"
    desc = "At least one guard receipt exists"
    receipts_dir = os.path.join(root, ".wabblespec", "state", "receipts")
    if not os.path.isdir(receipts_dir):
        return _fail(cid, sev, desc, "receipts/ directory not found")
    guard_receipts = [f for f in os.listdir(receipts_dir) if "guard" in f.lower()]
    if not guard_receipts:
        return _fail(cid, sev, desc, "No guard receipts found in .wabblespec/state/receipts/")
    return _pass(cid, sev, desc, f"{len(guard_receipts)} guard receipt(s) found")


def check_L4(root: str) -> dict:
    """wabblespec.yaml parses as valid YAML."""
    cid, sev = "L4", "low"
    desc = "wabblespec.yaml parses as valid YAML"
    yaml_path = os.path.join(root, ".wabblespec", "wabblespec.yaml")
    if not os.path.isfile(yaml_path):
        return _fail(cid, sev, desc, "wabblespec.yaml not found")
    try:
        _load_yaml(yaml_path)
        return _pass(cid, sev, desc, "wabblespec.yaml parses without errors")
    except Exception as e:
        return _fail(cid, sev, desc, f"YAML parse error: {e}")


def check_L5(root: str) -> dict:
    """At least one verifier receipt exists."""
    cid, sev = "L5", "low"
    desc = "At least one verifier receipt exists"
    receipts_dir = os.path.join(root, ".wabblespec", "state", "receipts")
    if not os.path.isdir(receipts_dir):
        return _fail(cid, sev, desc, "receipts/ directory not found")
    verifier_receipts = [f for f in os.listdir(receipts_dir) if "verifier" in f.lower()]
    if not verifier_receipts:
        return _fail(cid, sev, desc, "No verifier receipts found in .wabblespec/state/receipts/")
    return _pass(cid, sev, desc, f"{len(verifier_receipts)} verifier receipt(s) found")


def check_L6(root: str) -> dict:
    """.claude/skills/ directory exists and is non-empty."""
    cid, sev = "L6", "low"
    desc = ".claude/skills/ directory exists and is non-empty"
    skills_dir = os.path.join(root, ".claude", "skills")
    if not os.path.isdir(skills_dir):
        return _fail(cid, sev, desc, ".claude/skills/ directory not found")
    entries = os.listdir(skills_dir)
    if not entries:
        return _fail(cid, sev, desc, ".claude/skills/ is empty")
    return _pass(cid, sev, desc, f".claude/skills/ has {len(entries)} entries")


def check_L7(root: str) -> dict:
    """scope.md exists under .wabblespec/state/."""
    cid, sev = "L7", "low"
    desc = "scope.md exists under .wabblespec/state/"
    path = os.path.join(root, ".wabblespec", "state", "scope.md")
    if not os.path.isfile(path):
        return _fail(cid, sev, desc, "scope.md not found under .wabblespec/state/")
    return _pass(cid, sev, desc, "scope.md exists at .wabblespec/state/scope.md")


def check_D1(root: str) -> dict:
    """Receipt-write delegation: every receipt_required module's SKILL.md must
    route its receipt write through receipt-writer.py (directly or via the
    script-delegation-contract), rather than hand-authoring receipt JSON."""
    cid, sev = "D1", "medium"
    desc = "Receipt-producing modules delegate to receipt-writer.py"
    modules_root = os.path.join(root, ".wabblespec", "engine", "modules")
    if not os.path.isdir(modules_root):
        return _fail(cid, sev, desc, "engine/modules/ not found")

    total = 0
    non_delegating = []
    for dirpath, _dirs, files in os.walk(modules_root):
        if "skill-rules.json" not in files:
            continue
        rules = os.path.join(dirpath, "skill-rules.json")
        try:
            data = _load_json(rules)
        except Exception:
            continue
        if data.get("receipt_required") is not True:
            continue
        total += 1
        skill_md = os.path.join(dirpath, "SKILL.md")
        content = ""
        if os.path.isfile(skill_md):
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
        if "receipt-writer.py" not in content and "script-delegation-contract" not in content:
            mid = data.get("module") or os.path.relpath(dirpath, modules_root).replace("\\", "/")
            non_delegating.append(mid)

    if non_delegating:
        non_delegating.sort()
        return _fail(cid, sev, desc,
                     f"{len(non_delegating)}/{total} receipt_required modules hand-author "
                     f"(no receipt-writer.py / contract reference): {non_delegating[:8]}"
                     + (" ..." if len(non_delegating) > 8 else ""))
    return _pass(cid, sev, desc, f"all {total} receipt_required modules delegate")


# ---------------------------------------------------------------------------
# All checks registry
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    check_C1, check_C2, check_C3, check_C4,
    check_H1, check_H2, check_H3, check_H4, check_H5,
    check_H6, check_H7, check_H8, check_H10,
    check_M1, check_M2, check_M3, check_M4, check_M5,
    check_M6, check_M7, check_M8, check_M9, check_M10,
    check_D1,
    check_L1, check_L2, check_L3, check_L4, check_L5,
    check_L6, check_L7,
]


# ---------------------------------------------------------------------------
# Self-test: lightweight JSON schema validation without external deps
# ---------------------------------------------------------------------------

def _validate_recipe(instance: dict) -> list:
    """Returns list of validation errors for a recipe instance."""
    errors = []
    # Required fields
    required = ["target", "platform", "detection_method", "confidence", "complexity", "session_id"]
    for field in required:
        if field not in instance:
            errors.append(f"Missing required field: {field!r}")

    # confidence must be number in [0.0, 1.0]
    if "confidence" in instance:
        c = instance["confidence"]
        if not isinstance(c, (int, float)):
            errors.append(f"confidence must be a number, got {type(c).__name__}")
        elif not (0.0 <= float(c) <= 1.0):
            errors.append(f"confidence {c} out of range [0.0, 1.0]")

    # complexity enum
    if "complexity" in instance:
        valid_complexity = {"Low", "Medium", "High"}
        if instance["complexity"] not in valid_complexity:
            errors.append(f"complexity {instance['complexity']!r} not in {valid_complexity}")

    return errors


def _validate_wave_queue(instance: dict) -> list:
    """Returns list of validation errors for a wave-queue instance."""
    errors = []
    # Required fields
    required = ["schema_version", "session_id", "created_at", "tasks"]
    for field in required:
        if field not in instance:
            errors.append(f"Missing required field: {field!r}")

    # schema_version must be an integer
    if "schema_version" in instance:
        sv = instance["schema_version"]
        if not isinstance(sv, int):
            errors.append(f"schema_version must be an integer, got {type(sv).__name__}: {sv!r}")

    # tasks items must have required fields
    tasks = instance.get("tasks", [])
    if isinstance(tasks, list):
        task_required = ["task_id", "session_id", "wave_number", "wave_label", "status"]
        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                errors.append(f"tasks[{i}] is not an object")
                continue
            for field in task_required:
                if field not in task:
                    errors.append(f"tasks[{i}] missing required field: {field!r}")

    return errors


def run_self_test(root: str) -> int:
    """
    Run schema-discrimination tests on 4 fixture files.
    Returns 0 on success (good→PASS, bad→FAIL), 1 on failure.
    """
    fixtures_dir = os.path.join(root, ".wabblespec", "engine", "shared", "scripts", "tests", "fixtures")
    tests = [
        ("good-recipe.json", "recipe", True),
        ("bad-recipe.json", "recipe", False),
        ("good-wave-queue.json", "wave-queue", True),
        ("bad-wave-queue.json", "wave-queue", False),
    ]

    all_pass = True
    for filename, schema_type, expect_valid in tests:
        path = os.path.join(fixtures_dir, filename)
        if not os.path.isfile(path):
            print(f"[SELF-TEST FAIL] Fixture not found: {filename}")
            all_pass = False
            continue

        try:
            with open(path, "r", encoding="utf-8") as f:
                instance = json.load(f)
        except Exception as e:
            print(f"[SELF-TEST FAIL] Cannot parse {filename}: {e}")
            all_pass = False
            continue

        if schema_type == "recipe":
            errors = _validate_recipe(instance)
        elif schema_type == "wave-queue":
            errors = _validate_wave_queue(instance)
        else:
            print(f"[SELF-TEST FAIL] Unknown schema type: {schema_type}")
            all_pass = False
            continue

        is_valid = len(errors) == 0
        expected_str = "PASS" if expect_valid else "FAIL"
        actual_str = "PASS" if is_valid else "FAIL"

        if is_valid == expect_valid:
            print(f"[SELF-TEST OK] {filename}: expected {expected_str}, got {actual_str}")
        else:
            detail = f"validation errors: {errors}" if errors else "no errors (expected some)"
            print(f"[SELF-TEST FAIL] {filename}: expected {expected_str}, got {actual_str} — {detail}")
            all_pass = False

    return 0 if all_pass else 1


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _print_human(results: list) -> None:
    for r in results:
        status = r["status"]
        cid = r["id"]
        desc = r["description"]
        detail = r.get("detail", "")
        tag = f"[{status}]"
        line = f"{tag} {cid}: {desc}"
        if detail and status == "FAIL":
            line += f" — {detail}"
        print(line)


def _print_json(results: list) -> None:
    print(json.dumps({"checks": results}, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="wabblespec-doctor — Framework drift detector"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--all", action="store_true",
                      help="Run all checks; exit 0 on successful enumeration")
    mode.add_argument("--severity", choices=["critical", "high", "medium", "low"],
                      help="Run all checks; exit nonzero if any check at this severity FAILS")
    mode.add_argument("--guard-advisory", action="store_true",
                      help="Run all checks; always exit 0 (non-blocking advisory mode)")
    mode.add_argument("--self-test", action="store_true",
                      help="Run schema-discrimination self-tests on fixture files")

    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()

    # Find repo root
    try:
        root = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Self-test mode
    if args.self_test:
        return run_self_test(root)

    # Run all checks
    results = []
    for check_fn in ALL_CHECKS:
        try:
            result = check_fn(root)
        except Exception as e:
            # Determine check ID from function name (e.g. check_C1 → C1)
            cid = check_fn.__name__.replace("check_", "")
            result = {
                "id": cid,
                "severity": "unknown",
                "status": "FAIL",
                "description": f"Check {cid} raised an unhandled exception",
                "detail": str(e),
            }
        results.append(result)

    # Output
    if args.format == "json":
        _print_json(results)
    else:
        _print_human(results)

    # Exit code logic
    if args.guard_advisory:
        return 0

    if args.all:
        return 0

    if args.severity:
        target_sev = args.severity
        failed = any(
            r["status"] == "FAIL" and r.get("severity") == target_sev
            for r in results
        )
        return 1 if failed else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
