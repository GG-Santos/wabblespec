#!/usr/bin/env python3
"""
attestation-hash.py — Compute the canonical content_hash for a framework-maintenance attestation.

Usage:
    python .wabblespec/engine/modules/l2/framework-maintenance/scripts/attestation-hash.py

Reads SKILL.md and skill-rules.json from the framework-maintenance module directory
and prints the sha256 hex digest used as `content_hash` in the attestation JSON.

The canonical recipe:
    sha256(SKILL.md_bytes + b'\\x00---attestation-separator---\\x00' + skill-rules.json_bytes)
"""

import hashlib
import os
import sys

MODULE_DIR = os.path.join(
    os.path.dirname(__file__), ".."
)

skill_path = os.path.join(MODULE_DIR, "SKILL.md")
rules_path = os.path.join(MODULE_DIR, "skill-rules.json")

for path in (skill_path, rules_path):
    if not os.path.isfile(path):
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)

skill = open(skill_path, "rb").read()
rules = open(rules_path, "rb").read()

digest = hashlib.sha256(skill + b"\x00---attestation-separator---\x00" + rules).hexdigest()
print(digest)
