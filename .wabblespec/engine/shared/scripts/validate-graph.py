"""
Validates framework.yaml module graph integrity.

Checks:
  1. All depends_on references resolve to a known module ID
  2. All shared file consumers reference a known module ID

Witness mode (--record-witness / --check-hashes):
  Records or verifies sha256 hashes of each module's SKILL.md and
  skill-rules.json. Detects file drift between framework runs without
  requiring a full quality-floor check.

  Witness file default: .wabblespec/archive/witness.json
  (relative to framework.yaml's directory; override with --witness)

Exit codes:
  0 = clean (zero violations / zero drift)
  1 = violations or drift found
  2 = input error (file not found, parse error, missing witness)
"""

import sys
import os
import json
import hashlib
import argparse
import subprocess
from collections import Counter
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ─── Witness helpers ──────────────────────────────────────────────────────────

def sha256_file(path):
    """Return hex sha256 of a file, or None if the file does not exist."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def module_witness_entry(framework_dir, module):
    """Compute hashes for a single module entry from framework.yaml."""
    rel_path = module.get("path", "")
    if not rel_path:
        return None
    module_dir = os.path.join(framework_dir, rel_path.replace("/", os.sep))
    skill_hash = sha256_file(os.path.join(module_dir, "SKILL.md"))
    rules_hash = sha256_file(os.path.join(module_dir, "skill-rules.json"))
    return {
        "path": rel_path,
        "skill_md_sha256": skill_hash,
        "skill_rules_sha256": rules_hash,
    }


def record_witness(framework_path, framework_dir, data, witness_path, target_id=None):
    """
    Compute and write witness.json for all modules (or a single module if
    target_id is given).  Existing entries for modules not in the current
    run are preserved so partial --module runs do not erase other entries.
    """
    import re
    standard_layer = re.compile(r"^L\d+$", re.IGNORECASE)
    modules = [
        m for m in data.get("modules", [])
        if standard_layer.match(str(m.get("layer", "")))
    ]
    if target_id:
        modules = [m for m in modules if m.get("id") == target_id]

    # Load existing witness if present (preserve entries not being re-recorded)
    existing = {}
    if os.path.isfile(witness_path):
        try:
            with open(witness_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            existing = {}

    entries = dict(existing.get("modules", {}))
    recorded_at = datetime.now(timezone.utc).isoformat()

    for m in modules:
        mid = m.get("id")
        if not mid:
            continue
        entry = module_witness_entry(framework_dir, m)
        if entry is not None:
            entry["recorded_at"] = recorded_at
            entries[mid] = entry

    witness = {
        "schema": "wabblespec-witness-v1",
        "framework_sha256": sha256_file(framework_path),
        "recorded_at": recorded_at,
        "modules": entries,
    }

    os.makedirs(os.path.dirname(witness_path), exist_ok=True)
    with open(witness_path, "w", encoding="utf-8") as f:
        json.dump(witness, f, indent=2)
        f.write("\n")

    print(f"Witness recorded: {len(entries)} module(s) -> {witness_path}")


def check_hashes(framework_path, framework_dir, data, witness_path, target_id=None):
    """
    Compare current module file hashes against witness.json.
    Emits MODULE_FILE_DRIFT for any mismatch.
    Returns True if all checked modules match, False if any drift detected.
    """
    import re
    if not os.path.isfile(witness_path):
        print(f"ERROR: witness file not found at {witness_path}", file=sys.stderr)
        print("       Run with --record-witness to create it.", file=sys.stderr)
        sys.exit(2)

    try:
        with open(witness_path, "r", encoding="utf-8") as f:
            witness = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Failed to read witness file: {e}", file=sys.stderr)
        sys.exit(2)

    recorded_entries = witness.get("modules", {})

    standard_layer = re.compile(r"^L\d+$", re.IGNORECASE)
    modules = [
        m for m in data.get("modules", [])
        if standard_layer.match(str(m.get("layer", "")))
    ]
    if target_id:
        modules = [m for m in modules if m.get("id") == target_id]

    results = []
    for m in modules:
        mid = m.get("id")
        if not mid:
            continue
        current = module_witness_entry(framework_dir, m)
        if current is None:
            continue

        if mid not in recorded_entries:
            results.append(("NEW", mid, "not in witness — run --record-witness to add"))
            continue

        recorded = recorded_entries[mid]
        drifted = []

        for field in ("skill_md_sha256", "skill_rules_sha256"):
            c = current.get(field)
            r = recorded.get(field)
            if c != r:
                label = "SKILL.md" if "skill_md" in field else "skill-rules.json"
                if r is None and c is not None:
                    drifted.append(f"{label} created (was absent at witness time)")
                elif r is not None and c is None:
                    drifted.append(f"{label} deleted (was present at witness time)")
                else:
                    drifted.append(f"{label} hash changed")

        if drifted:
            results.append(("DRIFT", mid, "; ".join(drifted)))
        else:
            results.append(("PASS", mid, None))

    drift_count = sum(1 for status, _, _ in results if status in ("DRIFT", "NEW"))
    pass_count = sum(1 for status, _, _ in results if status == "PASS")
    new_count = sum(1 for status, _, _ in results if status == "NEW")

    print(f"Hash witness check  (witness: {os.path.basename(witness_path)})")
    print(f"  Modules checked:  {len(results)}")
    print(f"  PASS:             {pass_count}")
    if new_count:
        print(f"  NEW (unwitnessed):{new_count}")
    print(f"  DRIFT:            {drift_count}")

    if drift_count:
        print()
        print("MODULE_FILE_DRIFT:")
        for status, mid, detail in results:
            if status in ("DRIFT", "NEW"):
                print(f"  [{status}] {mid} — {detail}")
        print()
        print("FAIL — module files have changed since witness was recorded")
        return False
    else:
        if new_count:
            print()
            print("NOTE: unwitnessed modules above — run --record-witness to include them")
        print()
        print("PASS — all witnessed modules match recorded hashes")
        return True


# ─── Framework loader ─────────────────────────────────────────────────────────

def load_framework(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse {path}: {e}", file=sys.stderr)
        sys.exit(2)


def collect_module_ids(data):
    ids = set()
    for module in data.get("modules", []):
        mid = module.get("id")
        if mid:
            ids.add(mid)
    return ids


def check_depends_on(data, known_ids):
    violations = []
    for module in data.get("modules", []):
        mid = module.get("id", "<unknown>")
        for dep in module.get("depends_on", []):
            if dep not in known_ids:
                violations.append({
                    "type": "depends_on",
                    "source": mid,
                    "invalid_ref": dep,
                    "message": f"Module '{mid}' depends_on '{dep}' which is not a known module ID"
                })
    return violations


def check_shared_consumers(data, known_ids):
    violations = []
    shared = data.get("shared", {})
    for section_name, section in shared.items():
        if not isinstance(section, list):
            continue
        for entry in section:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path", "<unknown>")
            consumers = entry.get("consumers", [])
            if not isinstance(consumers, list):
                continue
            for consumer in consumers:
                if consumer not in known_ids:
                    violations.append({
                        "type": "consumer",
                        "source": f"shared.{section_name}: {path}",
                        "invalid_ref": consumer,
                        "message": f"Shared file '{path}' lists consumer '{consumer}' which is not a known module ID"
                    })
    return violations


# ─── Centrality analysis ──────────────────────────────────────────────────────

def compute_centrality(data):
    """
    Rank modules and shared artifacts by incoming dependency count.

    Hub modules: modules most listed in other modules' depends_on arrays.
    Hub shared artifacts: shared files with the most declared consumers.
    """
    # ── Hub modules ──────────────────────────────────────────────────────────
    dep_counter = Counter()
    for module in data.get("modules", []):
        for dep in module.get("depends_on", []):
            dep_counter[dep] += 1

    print("=== Hub Modules (by incoming depends_on count) ===")
    if not dep_counter:
        print("  (no depends_on relationships found)")
    else:
        for rank, (mid, count) in enumerate(dep_counter.most_common(15), 1):
            noun = "module depends on this" if count == 1 else "modules depend on this"
            print(f"  {rank:>2}. {mid:<30} — {count} {noun}")

    # ── Hub shared artifacts ─────────────────────────────────────────────────
    print()
    print("=== Hub Shared Artifacts (by consumer count) ===")
    shared = data.get("shared", {})
    section_order = [
        "schemas", "references", "infrastructure", "scripts", "templates",
        "dev_frameworks", "dev_infrastructure", "gateway_rules",
    ]
    any_shared = False
    for section_name in section_order:
        section = shared.get(section_name)
        if not isinstance(section, list) or not section:
            continue
        ranked = sorted(
            [
                (e.get("path", "<unknown>"), len(e.get("consumers", [])))
                for e in section
                if isinstance(e, dict)
            ],
            key=lambda x: -x[1],
        )
        top = [(p, c) for p, c in ranked if c > 0][:10]
        if not top:
            continue
        any_shared = True
        print(f"  {section_name}:")
        for path, count in top:
            noun = "consumer" if count == 1 else "consumers"
            basename = os.path.basename(path)
            print(f"    {basename:<45} — {count} {noun}")
    if not any_shared:
        print("  (no shared artifacts with declared consumers found)")


# ─── Co-change coupling detection ─────────────────────────────────────────────

def detect_co_change(data, framework_dir, threshold=3):
    """
    Detect modules that co-commit frequently without a declared dependency.

    Parses git history to find pairs of modules that change together above
    the threshold. Compares against declared depends_on relationships and
    emits UNDECLARED_COUPLING for pairs with no declared link in either
    direction.

    Non-fatal if git is unavailable or the directory is not a git repo.
    """
    # Build path-prefix → module-id map from framework.yaml module paths
    path_to_module = {}
    for m in data.get("modules", []):
        mid = m.get("id")
        rel_path = m.get("path", "")
        if mid and rel_path:
            norm = rel_path.replace("\\", "/").rstrip("/")
            path_to_module[norm] = mid

    def file_to_module_id(filepath):
        norm = filepath.replace("\\", "/").rstrip("/")
        for mod_path, mid in path_to_module.items():
            if norm.startswith(mod_path + "/") or norm == mod_path:
                return mid
        return None

    # Run git log — all commits, name-only, separated by COMMIT_ sentinel
    try:
        result = subprocess.run(
            ["git", "log", "--name-only", "--pretty=format:COMMIT_%H"],
            capture_output=True, text=True, cwd=framework_dir, timeout=30,
        )
    except FileNotFoundError:
        print("WARNING: git not found. Skipping co-change analysis.")
        return
    except subprocess.TimeoutExpired:
        print("WARNING: git log timed out. Skipping co-change analysis.")
        return

    if result.returncode != 0:
        print("WARNING: git log failed. Skipping co-change analysis.")
        return

    # Parse output into per-commit module-id sets
    commits_to_module_sets = []
    current_files = []
    in_commit = False
    for line in result.stdout.split("\n"):
        stripped = line.strip()
        if stripped.startswith("COMMIT_"):
            if current_files:
                ids = {file_to_module_id(f) for f in current_files} - {None}
                if len(ids) >= 2:
                    commits_to_module_sets.append(sorted(ids))
            current_files = []
            in_commit = True
        elif stripped and in_commit:
            current_files.append(stripped)
    # Flush last commit block
    if current_files:
        ids = {file_to_module_id(f) for f in current_files} - {None}
        if len(ids) >= 2:
            commits_to_module_sets.append(sorted(ids))

    # Build co-commit frequency counter
    co_counts = Counter()
    for mod_list in commits_to_module_sets:
        for i in range(len(mod_list)):
            for j in range(i + 1, len(mod_list)):
                co_counts[(mod_list[i], mod_list[j])] += 1

    # Build declared dependency map (bidirectional lookup)
    declared_deps = {}
    for m in data.get("modules", []):
        mid = m.get("id")
        if mid:
            declared_deps[mid] = set(m.get("depends_on", []))

    # Find pairs above threshold with no declared link in either direction
    findings = []
    for (a, b), count in sorted(co_counts.items(), key=lambda x: -x[1]):
        if count >= threshold:
            if b not in declared_deps.get(a, set()) and a not in declared_deps.get(b, set()):
                findings.append((a, b, count))

    print(f"=== Co-Change Coupling Analysis (threshold: {threshold} co-commits) ===")
    print()
    if findings:
        for a, b, count in findings:
            print(f"UNDECLARED_COUPLING: {a} <-> {b} ({count} co-commits, no declared dependency)")
        print()
        print(f"{len(findings)} potential undeclared coupling(s) found.")
        print("Review: add to depends_on or confirm coupling is intentional.")
    else:
        print("No undeclared couplings detected above threshold.")
    print(f"\n(Analyzed {len(commits_to_module_sets)} commits touching 2+ modules)")


def main():
    parser = argparse.ArgumentParser(description="Validate framework.yaml module graph integrity")
    parser.add_argument(
        "--framework",
        default=".wabblespec/wabblespec.yaml",
        help="Path to framework.yaml (default: framework.yaml)"
    )
    parser.add_argument(
        "--witness",
        default=None,
        help="Path to witness.json (default: .wabblespec/archive/witness.json relative to framework.yaml)"
    )
    parser.add_argument(
        "--record-witness",
        action="store_true",
        help="Compute and write sha256 hashes for all module files to witness.json"
    )
    parser.add_argument(
        "--check-hashes",
        action="store_true",
        help="Compare current module file hashes against recorded witness.json; emit MODULE_FILE_DRIFT on mismatch"
    )
    parser.add_argument(
        "--module",
        metavar="ID",
        help="Restrict --record-witness or --check-hashes to a single module ID"
    )
    parser.add_argument(
        "--centrality",
        action="store_true",
        help="Rank modules and shared artifacts by incoming dependency count"
    )
    parser.add_argument(
        "--co-change",
        action="store_true",
        dest="co_change",
        help="Detect modules that co-commit frequently without a declared dependency"
    )
    parser.add_argument(
        "--co-change-threshold",
        type=int,
        default=3,
        dest="co_change_threshold",
        metavar="N",
        help="Minimum co-commit count to flag as potential undeclared coupling (default: 3)"
    )
    args = parser.parse_args()

    framework_path = os.path.abspath(args.framework)
    framework_dir = os.path.dirname(framework_path)

    # Resolve witness path
    if args.witness:
        witness_path = os.path.abspath(args.witness)
    else:
        witness_path = os.path.join(framework_dir, ".wabblespec", "archive", "witness.json")

    data = load_framework(framework_path)

    # ── Witness mode ────────────────────────────────────────────────────────
    if args.record_witness:
        record_witness(framework_path, framework_dir, data, witness_path, target_id=args.module)
        sys.exit(0)

    if args.check_hashes:
        ok = check_hashes(framework_path, framework_dir, data, witness_path, target_id=args.module)
        sys.exit(0 if ok else 1)

    # ── Centrality mode ──────────────────────────────────────────────────────
    if args.centrality:
        compute_centrality(data)
        sys.exit(0)

    # ── Co-change mode ───────────────────────────────────────────────────────
    if args.co_change:
        detect_co_change(data, framework_dir, threshold=args.co_change_threshold)
        sys.exit(0)

    # ── Graph integrity mode (default) ──────────────────────────────────────
    known_ids = collect_module_ids(data)
    module_count = len(known_ids)

    depends_violations = check_depends_on(data, known_ids)

    shared_file_count = sum(
        len(section) if isinstance(section, list) else 0
        for section in data.get("shared", {}).values()
    )
    consumer_violations = check_shared_consumers(data, known_ids)

    all_violations = depends_violations + consumer_violations

    print(f"framework.yaml integrity check")
    print(f"  Modules checked:      {module_count}")
    print(f"  Shared files checked: {shared_file_count}")
    print(f"  Violations found:     {len(all_violations)}")

    if all_violations:
        print()
        print("VIOLATIONS:")
        for v in all_violations:
            print(f"  [{v['type'].upper()}] {v['message']}")
        sys.exit(1)
    else:
        print()
        print("PASS — graph is consistent")
        sys.exit(0)


if __name__ == "__main__":
    main()
