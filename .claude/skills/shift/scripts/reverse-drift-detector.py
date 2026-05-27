#!/usr/bin/env python3
"""
WabbleSpec Shift — reverse-drift-detector.py

Takes --spec <path> --impl <path>. Checks if impl conforms to spec.
Returns: drift_detected bool + list of diverged sections.

Usage:
  python modules/l1/shift/scripts/reverse-drift-detector.py --spec SKILL.md --impl receipts/
  python modules/l1/shift/scripts/reverse-drift-detector.py --spec schemas/foo.schema.json --impl src/foo.py
"""
import argparse
import json
import re
import sys
from pathlib import Path


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"ERROR: Cannot read {path}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_required_fields_from_schema(schema_text: str) -> list[str]:
    """Extract required field names from a JSON Schema."""
    try:
        schema = json.loads(schema_text)
    except json.JSONDecodeError:
        return []
    return schema.get("required", [])


def extract_declared_modes(skill_text: str) -> list[str]:
    """Extract mode declarations from a SKILL.md (e.g. 'mode: create | rollout | audit | retire')."""
    modes = []
    for match in re.finditer(r'mode[:\s]+([a-z\s|]+)', skill_text, re.IGNORECASE):
        for mode in re.split(r'[\s|]+', match.group(1)):
            mode = mode.strip().lower()
            if mode and len(mode) > 2:
                modes.append(mode)
    return list(set(modes))


def extract_declared_steps(skill_text: str) -> list[str]:
    """Extract step headings from a SKILL.md."""
    return re.findall(r'^#{1,4}\s+Step\s+\d+[^\n]*', skill_text, re.MULTILINE)


def check_schema_drift(spec_path: Path, impl_path: Path) -> list[dict]:
    """Compare schema required fields against implementation file content."""
    divergences = []
    spec_text = load_text(spec_path)
    impl_text = load_text(impl_path)

    required_fields = extract_required_fields_from_schema(spec_text)
    for field in required_fields:
        # Check if the field name appears in implementation
        pattern = rf'\b{re.escape(field)}\b'
        if not re.search(pattern, impl_text):
            divergences.append({
                "type": "field-mismatch",
                "severity": "HIGH",
                "description": f"Required field '{field}' declared in spec but not found in impl",
                "spec_location": str(spec_path),
                "impl_location": str(impl_path),
            })
    return divergences


def check_skill_drift(spec_path: Path, impl_dir: Path) -> list[dict]:
    """Check if SKILL.md declared behaviors appear in receipt evidence in impl_dir."""
    divergences = []
    spec_text = load_text(spec_path)

    declared_steps = extract_declared_steps(spec_text)
    declared_modes = extract_declared_modes(spec_text)

    # Scan implementation directory for receipts / source files
    impl_texts: list[str] = []
    if impl_dir.is_dir():
        for f in impl_dir.rglob("*.json"):
            try:
                impl_texts.append(f.read_text(encoding="utf-8"))
            except OSError:
                pass
        for f in impl_dir.rglob("*.md"):
            try:
                impl_texts.append(f.read_text(encoding="utf-8"))
            except OSError:
                pass
    elif impl_dir.is_file():
        impl_texts = [load_text(impl_dir)]

    combined_impl = " ".join(impl_texts).lower()

    # Check modes appear in implementation
    for mode in declared_modes:
        if mode not in combined_impl:
            divergences.append({
                "type": "mode-gap",
                "severity": "HIGH",
                "description": f"Mode '{mode}' declared in spec but no evidence in impl",
                "spec_location": str(spec_path),
                "impl_location": str(impl_dir),
            })

    # Ordering check: if steps are declared, their keywords should appear in impl
    if declared_steps and len(declared_steps) > 3:
        step_keywords = [re.sub(r'^#{1,4}\s+Step\s+\d+\s*[-—]*\s*', '', s).strip().lower()
                         for s in declared_steps]
        missing_steps = [kw for kw in step_keywords if kw and len(kw) > 5 and kw not in combined_impl]
        if missing_steps:
            divergences.append({
                "type": "ordering-violation",
                "severity": "MEDIUM",
                "description": f"Steps declared in spec not evidenced in impl: {missing_steps[:3]}",
                "spec_location": str(spec_path),
                "impl_location": str(impl_dir),
            })

    return divergences


def main() -> None:
    parser = argparse.ArgumentParser(description="WabbleSpec Shift reverse-drift-detector")
    parser.add_argument("--spec", required=True, help="Path to spec file (SKILL.md or schema.json)")
    parser.add_argument("--impl", required=True, help="Path to implementation file or directory")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    impl_path = Path(args.impl)

    if not spec_path.exists():
        print(f"ERROR: spec path not found: {spec_path}", file=sys.stderr)
        sys.exit(1)
    if not impl_path.exists():
        print(f"ERROR: impl path not found: {impl_path}", file=sys.stderr)
        sys.exit(1)

    divergences: list[dict] = []

    if spec_path.suffix == ".json":
        divergences = check_schema_drift(spec_path, impl_path)
    else:
        divergences = check_skill_drift(spec_path, impl_path)

    result = {
        "spec": str(spec_path),
        "impl": str(impl_path),
        "drift_detected": len(divergences) > 0,
        "diverged_sections": divergences,
        "divergence_count": len(divergences),
    }

    print(json.dumps(result, indent=2))
    sys.exit(0 if not divergences else 1)


if __name__ == "__main__":
    main()
