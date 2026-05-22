"""
Migrate skill-rules.json files from old nested activation.triggers format
to the canonical top-level activators format.

Old format (found in L0 product/reference-load, L2 team-plan/model-router/economy,
L3 all platforms, L4 all gateways, L5 dream/entity-graph, L6 all, L7 scaffold):
  {
    "skill_id": "platform-cli",
    "activation": {
      "triggers": [...],
      "excludes": [...],
      "file_path_patterns": [...]
    },
    ...
  }

Canonical format (token-protocol Phase 9):
  {
    "module": "cli",
    "layer": "L3",
    "activators": [...],
    "anti_activators": [...],
    "loading_gate": "activation",
    "commands": [],
    "file_path_patterns": [...]
  }

Run: python scripts/migrate-old-skill-rules.py
     python scripts/migrate-old-skill-rules.py --dry-run
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent / "modules"
DRY_RUN = "--dry-run" in sys.argv

# Default values for canonical fields missing from old format
VERIFICATION_MODE_DEFAULTS = {
    "L0": "Observation",
    "L1": "Audit",
    "L2": "Audit",
    "L3": "Audit",
    "L4": "Audit",
    "L5": "Observation",
    "L6": "Observation",
    "L7": "Audit",
}

TIER_DEFAULTS = {
    "L0": 1, "L1": 1, "L2": 1, "L3": 2,
    "L4": 2, "L5": 2, "L6": 3, "L7": 2,
}

BUILD_TARGETS_DEFAULTS = {
    "L0": ["ALL"], "L1": ["ALL"], "L2": ["ALL"],
    "L3": None,  # derived from skill_id
    "L4": ["ALL"], "L5": ["ALL"], "L6": ["ALL"], "L7": ["ALL"],
}


def derive_module_name(data: dict, path: Path) -> str:
    """Extract canonical module name from skill_id or directory name."""
    skill_id = data.get("skill_id", "")
    if skill_id:
        # "platform-cli" -> "cli", "gateway-security" -> "security"
        parts = skill_id.split("-", 1)
        if len(parts) == 2 and parts[0] in ("platform", "gateway", "module"):
            return parts[1]
        return skill_id
    return path.parent.name


def migrate(data: dict, path: Path) -> tuple[dict, list[str]]:
    """Convert old format to canonical. Returns (migrated_data, changes_made)."""
    changes = []
    activation = data.get("activation", {})
    layer = data.get("layer", "L1")

    # 1. module field
    if "module" not in data:
        module_name = derive_module_name(data, path)
        data["module"] = module_name
        changes.append(f"added module: {module_name}")

    # 2. activators (from activation.triggers)
    if "activators" not in data and "triggers" in activation:
        data["activators"] = activation["triggers"]
        changes.append(f"moved activation.triggers -> activators ({len(activation['triggers'])} items)")

    # 3. anti_activators (from activation.excludes)
    if "anti_activators" not in data:
        excludes = activation.get("excludes", [])
        data["anti_activators"] = excludes
        if excludes:
            changes.append(f"moved activation.excludes -> anti_activators ({len(excludes)} items)")

    # 4. tier
    if "tier" not in data:
        data["tier"] = TIER_DEFAULTS.get(layer, 1)
        changes.append(f"added tier: {data['tier']}")

    # 5. build_targets
    if "build_targets" not in data:
        bt = BUILD_TARGETS_DEFAULTS.get(layer)
        if bt is None:
            # L3 platform: derive from module name
            module = data.get("module", "")
            bt = [module.upper().replace("-", "_")]
        data["build_targets"] = bt
        changes.append(f"added build_targets: {bt}")

    # 6. phases
    if "phases" not in data:
        phases_map = {
            "L0": ["Research"],
            "L1": ["Research", "Plan", "Execute"],
            "L2": ["Research", "Plan", "Execute"],
            "L3": ["Research", "Plan", "Execute"],
            "L4": ["Research", "Plan", "Execute"],
            "L5": ["ALL"],
            "L6": ["ALL"],
            "L7": ["Execute"],
        }
        data["phases"] = phases_map.get(layer, ["ALL"])
        changes.append(f"added phases: {data['phases']}")

    # 7. authority (basic scaffold if missing)
    if "authority" not in data:
        module = data.get("module", path.parent.name)
        data["authority"] = {
            "owns": [f".wabblespec/receipts/{module}-receipt-*.json"],
            "reads": [".wabblespec/plans/", ".wabblespec/receipts/"]
        }
        changes.append("added authority scaffold")

    # 8. verification_mode
    if "verification_mode" not in data:
        data["verification_mode"] = VERIFICATION_MODE_DEFAULTS.get(layer, "Audit")
        changes.append(f"added verification_mode: {data['verification_mode']}")

    # 9. receipt_required
    if "receipt_required" not in data:
        data["receipt_required"] = True
        changes.append("added receipt_required: true")

    # 10. collapse_eligible
    if "collapse_eligible" not in data:
        data["collapse_eligible"] = False
        changes.append("added collapse_eligible: false")

    # 11. requires_receipts_from (check for old receipts_required)
    if "receipts_required" in data:
        if "requires_receipts_from" not in data:
            data["requires_receipts_from"] = data["receipts_required"]
            changes.append(f"renamed receipts_required -> requires_receipts_from")
        del data["receipts_required"]

    # 12. Merge activation.file_path_patterns into top-level if different
    activation_fpp = activation.get("file_path_patterns", [])
    top_fpp = data.get("file_path_patterns", [])
    if activation_fpp and set(activation_fpp) - set(top_fpp):
        merged = list(dict.fromkeys(top_fpp + activation_fpp))  # deduplicate, preserve order
        data["file_path_patterns"] = merged
        changes.append(f"merged activation.file_path_patterns into top-level ({len(merged)} total)")

    # 13. Remove old fields
    for old_key in ("skill_id", "type", "version"):
        if old_key in data:
            del data[old_key]
            changes.append(f"removed {old_key}")

    # 14. Remove activation block (after migrating its contents)
    if "activation" in data:
        del data["activation"]
        changes.append("removed activation block (contents migrated)")

    return data, changes


def process_file(path: Path) -> tuple[bool, list[str]]:
    """Returns (was_migrated, changes)."""
    raw = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return False, [f"JSON ERROR: {e}"]

    # Check if this file needs migration (has old nested activation block with triggers)
    activation = data.get("activation", {})
    receipts_required = "receipts_required" in data
    needs_migration = "triggers" in activation or receipts_required

    if not needs_migration:
        return False, []

    migrated, changes = migrate(data, path)
    if not changes:
        return False, []

    if not DRY_RUN:
        path.write_text(json.dumps(migrated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return True, changes


def main():
    migrated_files = []
    skipped = []
    errors = []

    for p in sorted(ROOT.rglob("skill-rules.json")):
        try:
            was_migrated, changes = process_file(p)
            rel = str(p.relative_to(ROOT.parent))
            if was_migrated:
                migrated_files.append((rel, changes))
            else:
                if changes:  # has errors
                    errors.append((rel, changes))
                else:
                    skipped.append(rel)
        except Exception as e:
            errors.append((str(p), [str(e)]))

    print(f"{'DRY RUN — ' if DRY_RUN else ''}Migrated: {len(migrated_files)}")
    for f, changes in migrated_files:
        print(f"\n  {f}")
        for c in changes:
            print(f"    - {c}")

    print(f"\nAlready canonical (skipped): {len(skipped)}")

    if errors:
        print(f"\nErrors: {len(errors)}")
        for f, errs in errors:
            print(f"  {f}")
            for e in errs:
                print(f"    ! {e}")

    if DRY_RUN:
        print("\n[DRY RUN] No files written. Remove --dry-run to apply.")


if __name__ == "__main__":
    main()
