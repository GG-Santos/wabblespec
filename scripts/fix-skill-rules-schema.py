"""
Fix Gap 1: add loading_gate, commands, file_path_patterns to all skill-rules.json files.
Built schema is canonical. token-protocol Phase 9 spec was written before implementation.
"""

import json
import os
from pathlib import Path

ROOT = Path(r"C:\Vaults\WabbleSpec v6.1\modules")

LOADING_GATE = {
    # L0 — intake, runs at recipe/session start
    "recipe": "recipe",
    "product": "recipe",
    "reference-load": "recipe",
    "runtime-probe": "recipe",
    # L1 — routing/spec, loads at stage boundaries
    "scope-frame": "stage",
    "specify": "stage",
    "decompose": "stage",
    "apply": "stage",
    "explore": "stage",
    "interview": "stage",
    "propose": "stage",
    "migrate": "stage",
    "clean": "stage",
    "test": "stage",
    "triage": "stage",
    # L2 — orchestration, loads at phase execution
    "executor": "phase",
    "verifier": "phase",
    "guard": "phase",
    "reviewer": "phase",
    "autopilot": "phase",
    "model-router": "phase",
    "ensemble": "phase",
    "economy": "phase",
    "rollback": "phase",
    "team-plan": "phase",
    # L3 — platform packages, on-demand via target detection
    "cli": "activation",
    "web": "activation",
    "api-service": "activation",
    "library": "activation",
    "extension": "activation",
    "desktop": "activation",
    "mobile": "activation",
    "data-pipeline": "activation",
    "ai-agent": "activation",
    "game": "activation",
    "iot": "activation",
    # L4 — gateways, on-demand when gateway triggered
    "security": "activation",
    "engineering": "activation",
    "ai": "activation",
    "aesthetic": "activation",
    "design": "activation",
    "experience": "activation",
    # L5 — memory layer, on-demand
    "memory": "activation",
    "memory-search": "activation",
    "provenance": "activation",
    "dream": "activation",
    "entity-graph": "activation",
    "memory-mine": "activation",
    "forget": "activation",
    # L6 — expression layer, on-demand
    "homowabian": "activation",
    "document": "activation",
    "polish": "activation",
    "research-log": "activation",
    # L7 — delivery, phase-triggered
    "archive": "phase",
    "package": "phase",
    "deploy": "phase",
    "release": "phase",
    "scaffold": "stage",
    "monitor": "phase",
}

COMMANDS = {
    "recipe": ["/recipe"],
    "product": ["/product"],
    "reference-load": ["/ref-load"],
    "runtime-probe": ["/probe"],
    "specify": ["/specify"],
    "decompose": ["/decompose"],
    "explore": ["/explore"],
    "interview": ["/interview"],
    "propose": ["/propose"],
    "archive": ["/archive"],
    "dream": ["/dream"],
    "memory-mine": ["/mine"],
    "entity-graph": ["/graph"],
    "document": ["/document"],
    "polish": ["/polish"],
    "deploy": ["/deploy"],
    "release": ["/release"],
    "scaffold": ["/scaffold"],
    "memory-search": ["/memory-search"],
    "forget": ["/forget"],
}

FILE_PATH_PATTERNS = {
    "cli": ["**/bin/**", "**/cmd/**", "**/*.sh", "**/*.ps1"],
    "web": ["**/src/**/*.tsx", "**/src/**/*.vue", "**/src/**/*.svelte", "**/*.html"],
    "api-service": ["**/routes/**", "**/api/**", "**/controllers/**", "**/handlers/**"],
    "library": ["**/src/**", "**/lib/**", "**/index.*"],
    "extension": ["**/manifest.json", "**/background/**", "**/content/**", "**/popup/**"],
    "desktop": ["**/src-tauri/**", "**/electron/**", "**/main.ts", "**/preload.ts"],
    "mobile": ["**/ios/**", "**/android/**", "**/*.dart", "**/*.swift", "**/*.kt"],
    "data-pipeline": ["**/dags/**", "**/pipelines/**", "**/etl/**", "**/transforms/**"],
    "ai-agent": ["**/agents/**", "**/prompts/**", "**/chains/**", "**/evals/**"],
    "game": ["**/Assets/**", "**/scenes/**", "**/*.gd", "**/*.cs", "**/*.unity"],
    "iot": ["**/*.c", "**/*.cpp", "**/firmware/**", "**/CMakeLists.txt", "**/*.ld"],
}

updated = []
skipped = []
errors = []

for skill_rules_path in ROOT.rglob("skill-rules.json"):
    module_name = skill_rules_path.parent.name

    try:
        with open(skill_rules_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        changed = False

        if "loading_gate" not in data:
            gate = LOADING_GATE.get(module_name)
            if gate is None:
                errors.append(f"UNKNOWN module '{module_name}' at {skill_rules_path} — no loading_gate mapped")
                continue
            data["loading_gate"] = gate
            changed = True

        if "commands" not in data:
            data["commands"] = COMMANDS.get(module_name, [])
            changed = True

        if "file_path_patterns" not in data:
            data["file_path_patterns"] = FILE_PATH_PATTERNS.get(module_name, [])
            changed = True

        if changed:
            with open(skill_rules_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.write("\n")
            updated.append(str(skill_rules_path.relative_to(ROOT.parent)))
        else:
            skipped.append(module_name)

    except Exception as e:
        errors.append(f"ERROR {skill_rules_path}: {e}")

print(f"Updated: {len(updated)}")
for p in updated:
    print(f"  {p}")

if skipped:
    print(f"\nSkipped (already had fields): {skipped}")

if errors:
    print(f"\nErrors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
