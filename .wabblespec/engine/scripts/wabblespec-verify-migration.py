"""wabblespec-verify-migration.py — verify the v6.2 reorganization is complete.

Checks:
  1. Zero project/repo references outside .wabblespec/engine/ and CLAUDE.md
  2. No skill-rules.json with "owns": ["project/repo/**/*"] authority patterns
  3. All hook paths in .claude/settings.json resolve to existing files
  4. .claude/skills/ is current with engine/modules/ for all managed skills
  5. .wabblespec/state/ is in .gitignore
  6. .wabblespec/engine/ exists with expected subdirectories
  7. .wabblespec/wabblespec.yaml exists
  8. guard-check.py handles product_space: true

Exit 0 = all checks pass. Exit 1 = failures found.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Bootstrap
_HERE = Path(__file__).resolve()
_probe = _HERE
while _probe != _probe.parent:
    if (_probe / ".wabblespec").exists():
        break
    _probe = _probe.parent
ROOT = _probe

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
failures: list[str] = []


def check(label: str, result: bool, detail: str = "") -> None:
    status = PASS if result else FAIL
    msg = f"  [{status}] {label}"
    if not result and detail:
        msg += f"\n         {detail}"
    print(msg)
    if not result:
        failures.append(f"{label}: {detail}")


# ── Check 1: no project/repo references in engine files ──────────────────────

def check_no_project_repo() -> None:
    engine = ROOT / ".wabblespec" / "engine"
    hits = []
    for f in engine.rglob("*"):
        if not f.is_file() or f.suffix not in (".md", ".json", ".py", ".yaml", ".js"):
            continue
        if "__pycache__" in f.parts:
            continue
        if f.name == "wabblespec-verify-migration.py":
            continue  # self-exclude: this script uses the string in check descriptions
        try:
            if "project/repo" in f.read_text(encoding="utf-8", errors="replace"):
                hits.append(str(f.relative_to(ROOT)))
        except:
            pass
    check(
        "No project/repo refs in engine/",
        len(hits) == 0,
        f"{len(hits)} files still have project/repo: {hits[:3]}"
    )


# ── Check 2: no owns ["project/repo/**"] in skill-rules.json ─────────────────

def check_no_old_authority() -> None:
    bad = []
    for f in (ROOT / ".wabblespec" / "engine").rglob("skill-rules.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except:
            continue
        owns = data.get("authority", {}).get("owns", [])
        if any("project/repo" in o for o in owns):
            bad.append(str(f.relative_to(ROOT)))
    check(
        "No legacy project/repo authority.owns in skill-rules.json",
        len(bad) == 0,
        f"Files still using old pattern: {bad}"
    )


# ── Check 3: hook paths in settings.json resolve ─────────────────────────────

def check_hook_paths() -> None:
    settings_path = ROOT / ".claude" / "settings.json"
    if not settings_path.exists():
        check("settings.json hook paths resolve", False, "settings.json not found")
        return
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    # Extract all command strings
    missing = []
    def _walk(obj):
        if isinstance(obj, dict):
            cmd = obj.get("command", "")
            if cmd:
                # Extract path from quoted segments
                for match in re.finditer(r'"([^"]+\.(js|py|ps1))"', cmd):
                    p = Path(match.group(1))
                    if not p.exists():
                        missing.append(match.group(1))
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)
    _walk(data)
    check(
        "All hook script paths resolve",
        len(missing) == 0,
        f"Missing: {missing[:5]}"
    )


# ── Check 4: .claude/skills/ is current with engine/modules/ ─────────────────

def check_skills_current() -> None:
    try:
        import yaml
    except ImportError:
        check(".claude/skills/ current with engine/modules/", False, "pyyaml not installed")
        return

    yaml_path = ROOT / ".wabblespec" / "wabblespec.yaml"
    if not yaml_path.exists():
        check(".claude/skills/ current with engine/modules/", False, "wabblespec.yaml not found")
        return

    with yaml_path.open(encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    skills_dir = ROOT / ".claude" / "skills"
    stale = missing = 0
    for mod in registry.get("modules", []):
        mod_path = ROOT / mod.get("path", "").rstrip("/")
        skill_md = mod_path / "SKILL.md"
        if not skill_md.exists():
            continue
        name_m = re.search(r"^name:\s*(.+)$", skill_md.read_text(encoding="utf-8"), re.MULTILINE)
        if not name_m:
            continue
        name = name_m.group(1).strip()
        dst_skill_md = skills_dir / name / "SKILL.md"
        if not dst_skill_md.exists():
            missing += 1
        elif skill_md.read_bytes() != dst_skill_md.read_bytes():
            stale += 1

    check(
        ".claude/skills/ current with engine/modules/",
        missing == 0 and stale == 0,
        f"{missing} missing, {stale} stale skills in .claude/skills/"
    )


# ── Check 5: .wabblespec/state/ in .gitignore ────────────────────────────────

def check_gitignore() -> None:
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        check(".wabblespec/state/ in .gitignore", False, ".gitignore not found")
        return
    content = gitignore.read_text(encoding="utf-8")
    check(
        ".wabblespec/state/ in .gitignore",
        ".wabblespec/state/" in content,
        ".wabblespec/state/ not found in .gitignore"
    )


# ── Check 6: engine subdirectories exist ─────────────────────────────────────

def check_engine_structure() -> None:
    expected = ["modules", "shared", "hooks", "scripts", "packages", "docs"]
    engine = ROOT / ".wabblespec" / "engine"
    missing = [d for d in expected if not (engine / d).is_dir()]
    check(
        ".wabblespec/engine/ has expected subdirs",
        len(missing) == 0,
        f"Missing: {missing}"
    )


# ── Check 7: wabblespec.yaml exists ──────────────────────────────────────────

def check_yaml() -> None:
    p = ROOT / ".wabblespec" / "wabblespec.yaml"
    check(".wabblespec/wabblespec.yaml exists", p.exists())


# ── Check 8: guard-check.py has product_space support ────────────────────────

def check_guard_product_space() -> None:
    guard = ROOT / ".wabblespec" / "engine" / "shared" / "scripts" / "guard-check.py"
    if not guard.exists():
        check("guard-check.py has product_space support", False, "guard-check.py not found")
        return
    content = guard.read_text(encoding="utf-8")
    check(
        "guard-check.py has product_space support",
        "product_space" in content and "_FRAMEWORK_PREFIXES" in content,
        "product_space flag logic not found in guard-check.py"
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f"wabblespec-verify-migration — checking {ROOT}\n")

    check_engine_structure()
    check_yaml()
    check_gitignore()
    check_hook_paths()
    check_no_project_repo()
    check_no_old_authority()
    check_skills_current()
    check_guard_product_space()

    print()
    if failures:
        print(f"RESULT: {len(failures)} check(s) FAILED")
        sys.exit(1)
    else:
        print("RESULT: All checks PASS — ready to merge reorganize/v6.2 to main")
        sys.exit(0)


if __name__ == "__main__":
    main()
