"""
STM Pipeline — Sequential pure-function text transformation pipeline.

Algorithm source: G0DM0D3 PAPER.md Section 3.5 (Semantic Transformation Modules).
Independent Python implementation. No TypeScript copied.
License-safe: implements algorithm from paper description, not from source code.

WabbleSpec adaptation:
  - Two G0DM0D3 modules ported: hedge_reducer, direct_mode
  - Two WabbleSpec-specific modules added: spec_mode, receipt_mode
  - casual_mode included but off by default (off for WabbleSpec receipts)
  - Module interface: id, name, version, enabled, transformer(str) -> str
  - Pipeline: apply enabled modules left-to-right in order
  - No shared mutable state between modules

Usage:
  python stm-pipeline.py --input "text" --modules hedge_reducer direct_mode
  python stm-pipeline.py --file output.md --modules hedge_reducer direct_mode spec_mode
  python stm-pipeline.py --list-modules
  python stm-pipeline.py --test

Exit codes: 0 = success, 1 = error, 2 = test failures
"""

import re
import sys
import json
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Module interface
# Architecture: PAPER.md §3.5 STMModule interface + applySTMs()
# ---------------------------------------------------------------------------

@dataclass
class STMModule:
    id: str
    name: str
    description: str
    version: str
    enabled: bool
    transformer: Callable[[str], str]


def apply_stms(text: str, modules: list[STMModule]) -> tuple[str, list[str]]:
    """
    Apply enabled modules sequentially left-to-right.
    Returns (transformed_text, list_of_applied_module_ids).
    Each module is a pure string -> string function (no shared state).

    Algorithm: PAPER.md §3.5 applySTMs()
    """
    result = text
    applied: list[str] = []
    for module in modules:
        if module.enabled:
            result = module.transformer(result)
            applied.append(module.id)
    return result, applied


# ---------------------------------------------------------------------------
# Module implementations
# ---------------------------------------------------------------------------

def _hedge_reducer_transform(text: str) -> str:
    """
    Remove epistemic hedging phrases.
    Source patterns: G0DM0D3 PAPER §3.5 hedge_reducer (11 patterns)
    """
    hedges = [
        re.compile(r"\bI think\s+", re.I),
        re.compile(r"\bI believe\s+", re.I),
        re.compile(r"\bperhaps\s+", re.I),
        re.compile(r"\bmaybe\s+", re.I),
        re.compile(r"\bIt seems like\s+", re.I),
        re.compile(r"\bIt appears that\s+", re.I),
        re.compile(r"\bprobably\s+", re.I),
        re.compile(r"\bpossibly\s+", re.I),
        re.compile(r"\bI would say\s+", re.I),
        re.compile(r"\bIn my opinion,?\s*", re.I),
        re.compile(r"\bFrom my perspective,?\s*", re.I),
    ]
    result = text
    for pattern in hedges:
        result = pattern.sub("", result)
    # Capitalize sentence-initial lowercase letters after removal
    result = re.sub(r"(^|\.\s+|\!\s+|\?\s+)([a-z])",
                    lambda m: m.group(1) + m.group(2).upper(), result)
    return result


def _direct_mode_transform(text: str) -> str:
    """
    Remove preamble phrases.
    Source patterns: G0DM0D3 PAPER §3.5 direct_mode (10 patterns)
    """
    preambles = [
        re.compile(r"^(Sure,?\s*)", re.I),
        re.compile(r"^(Of course,?\s*)", re.I),
        re.compile(r"^(Certainly,?\s*)", re.I),
        re.compile(r"^(Absolutely,?\s*)", re.I),
        re.compile(r"^(Great question!?\s*)", re.I),
        re.compile(r"^(That's a great question!?\s*)", re.I),
        re.compile(r"^(I'd be happy to help( you)?( with that)?[.!]?\s*)", re.I),
        re.compile(r"^(Let me help you with that[.!]?\s*)", re.I),
        re.compile(r"^(I understand[.!]?\s*)", re.I),
        re.compile(r"^(Thanks for asking[.!]?\s*)", re.I),
    ]
    result = text.strip()
    for pattern in preambles:
        result = pattern.sub("", result)
    # Capitalize first letter after removal
    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    return result


def _spec_mode_transform(text: str) -> str:
    """
    Normalize text toward EARS requirement language.
    WabbleSpec-specific (no G0DM0D3 equivalent).

    Converts informal modal verbs to EARS-compliant SHALL/SHOULD/MAY.
    Conservative: only applies high-confidence substitutions.
    """
    # "will" in requirement context -> SHALL
    text = re.sub(r"\bthe system will\b", "the system SHALL", text, flags=re.I)
    text = re.sub(r"\bthe component will\b", "the component SHALL", text, flags=re.I)
    text = re.sub(r"\bthe module will\b", "the module SHALL", text, flags=re.I)

    # "might" / "may want to" -> SHOULD
    text = re.sub(r"\bmight\b", "SHOULD", text, flags=re.I)
    text = re.sub(r"\bshould probably\b", "SHOULD", text, flags=re.I)

    # "you can" -> "the caller MAY"
    text = re.sub(r"\byou can\b", "the caller MAY", text, flags=re.I)

    # "utilize" -> "use" (EARS language is plain)
    text = re.sub(r"\butilize\b", "use", text, flags=re.I)
    text = re.sub(r"\bUtilize\b", "Use", text)

    return text


def _receipt_mode_transform(text: str) -> str:
    """
    Normalize receipt-adjacent text.
    WabbleSpec-specific (no G0DM0D3 equivalent).

    - Strips first-person from receipt-style prose
    - Capitalizes PASS/FAIL/WARN status markers
    - Trims trailing whitespace
    """
    # First-person normalization (receipt prose should be passive/third-person)
    text = re.sub(r"\bI wrote\b", "wrote", text, flags=re.I)
    text = re.sub(r"\bI verified\b", "verified", text, flags=re.I)
    text = re.sub(r"\bI confirmed\b", "confirmed", text, flags=re.I)
    text = re.sub(r"\bI ran\b", "ran", text, flags=re.I)
    text = re.sub(r"\bI checked\b", "checked", text, flags=re.I)
    text = re.sub(r"\bI created\b", "created", text, flags=re.I)
    text = re.sub(r"\bI updated\b", "updated", text, flags=re.I)

    # Status marker normalization
    text = re.sub(r"\bpass\b(?!\w)", "PASS", text, flags=re.I)
    text = re.sub(r"\bfail\b(?!\w)", "FAIL", text, flags=re.I)
    text = re.sub(r"\bwarn\b(?!\w)", "WARN", text, flags=re.I)

    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines)


def _casual_mode_transform(text: str) -> str:
    """
    Convert formal connectives to casual equivalents.
    Source: G0DM0D3 PAPER §3.5 casual_mode (22 substitutions).
    Off by default in WabbleSpec — receipts use formal language.
    """
    subs = [
        (r"\bHowever\b", "But"),
        (r"\bhowever\b", "but"),
        (r"\bTherefore\b", "So"),
        (r"\btherefore\b", "so"),
        (r"\bFurthermore\b", "Also"),
        (r"\bfurthermore\b", "also"),
        (r"\bAdditionally\b", "Plus"),
        (r"\badditionally\b", "plus"),
        (r"\bNevertheless\b", "Still"),
        (r"\bnevertheless\b", "still"),
        (r"\bConsequently\b", "So"),
        (r"\bconsequently\b", "so"),
        (r"\bMoreover\b", "Also"),
        (r"\bmoreover\b", "also"),
        (r"\bUtilize\b", "Use"),
        (r"\butilize\b", "use"),
        (r"\bPrior to\b", "Before"),
        (r"\bprior to\b", "before"),
        (r"\bSubsequent to\b", "After"),
        (r"\bsubsequent to\b", "after"),
        (r"\bIn order to\b", "To"),
        (r"\bin order to\b", "to"),
        (r"\bDue to the fact that\b", "Because"),
        (r"\bdue to the fact that\b", "because"),
    ]
    result = text
    for pattern, replacement in subs:
        result = re.sub(pattern, replacement, result)
    return result


# ---------------------------------------------------------------------------
# Module registry
# ---------------------------------------------------------------------------

ALL_MODULES: dict[str, STMModule] = {
    "hedge_reducer": STMModule(
        id="hedge_reducer",
        name="Hedge Reducer",
        description="Removes epistemic hedging: 'I think', 'perhaps', 'maybe', etc.",
        version="1.0.0",
        enabled=False,
        transformer=_hedge_reducer_transform,
    ),
    "direct_mode": STMModule(
        id="direct_mode",
        name="Direct Mode",
        description="Removes preamble phrases: 'Sure,', 'Of course,', 'I'd be happy to help', etc.",
        version="1.0.0",
        enabled=False,
        transformer=_direct_mode_transform,
    ),
    "spec_mode": STMModule(
        id="spec_mode",
        name="Spec Mode",
        description="Normalizes modals to EARS language: 'will' -> SHALL, 'might' -> SHOULD.",
        version="1.0.0",
        enabled=False,
        transformer=_spec_mode_transform,
    ),
    "receipt_mode": STMModule(
        id="receipt_mode",
        name="Receipt Mode",
        description="Normalizes receipt prose: strips first-person, capitalizes PASS/FAIL/WARN.",
        version="1.0.0",
        enabled=False,
        transformer=_receipt_mode_transform,
    ),
    "casual_mode": STMModule(
        id="casual_mode",
        name="Casual Mode",
        description="Converts formal connectives to casual: 'However' -> 'But', etc.",
        version="1.0.0",
        enabled=False,
        transformer=_casual_mode_transform,
    ),
}

# Default config sets for WabbleSpec modules
POLISH_DEFAULT = ["hedge_reducer", "direct_mode"]
CLEAN_DEFAULT = ["receipt_mode", "direct_mode"]


def get_pipeline(module_ids: list[str]) -> list[STMModule]:
    """Build an ordered pipeline from module ID list."""
    pipeline: list[STMModule] = []
    for mid in module_ids:
        if mid not in ALL_MODULES:
            raise ValueError(f"Unknown STM module: '{mid}'. Available: {list(ALL_MODULES.keys())}")
        module = ALL_MODULES[mid]
        # Return a copy with enabled=True
        pipeline.append(STMModule(
            id=module.id, name=module.name, description=module.description,
            version=module.version, enabled=True, transformer=module.transformer,
        ))
    return pipeline


# ---------------------------------------------------------------------------
# Built-in acceptance tests
# ---------------------------------------------------------------------------

def run_tests() -> int:
    failures = 0

    def check(name: str, condition: bool, detail: str = "") -> None:
        nonlocal failures
        if not condition:
            failures += 1
            print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))
        else:
            print(f"  PASS  {name}")

    print("stm-pipeline acceptance tests")
    print("-" * 40)

    # hedge_reducer positive cases
    pipeline = get_pipeline(["hedge_reducer"])
    text, applied = apply_stms("I think the approach is good.", pipeline)
    check("hedge_reducer removes 'I think'", "I think" not in text, f"got: {text!r}")
    text, _ = apply_stms("Perhaps we should reconsider.", pipeline)
    check("hedge_reducer removes 'Perhaps'", "perhaps" not in text.lower(), f"got: {text!r}")

    # hedge_reducer negative cases (must NOT modify)
    text, _ = apply_stms("The system SHALL validate input.", pipeline)
    check("hedge_reducer does not modify EARS requirement",
          text == "The system SHALL validate input.")
    text, _ = apply_stms("Run the tests first.", pipeline)
    check("hedge_reducer does not modify plain imperative", text == "Run the tests first.")

    # direct_mode positive cases
    pipeline = get_pipeline(["direct_mode"])
    text, _ = apply_stms("Sure, here is the implementation.", pipeline)
    check("direct_mode removes 'Sure,'", not text.startswith("Sure"), f"got: {text!r}")
    text, _ = apply_stms("Of course! The answer is 42.", pipeline)
    check("direct_mode removes 'Of course!'", not text.lower().startswith("of course"), f"got: {text!r}")

    # direct_mode negative cases
    text, _ = apply_stms("The module should run first.", pipeline)
    check("direct_mode does not modify non-preamble text",
          text == "The module should run first.")

    # spec_mode
    pipeline = get_pipeline(["spec_mode"])
    text, _ = apply_stms("The system will validate the form.", pipeline)
    check("spec_mode converts 'will' to SHALL",
          "SHALL" in text, f"got: {text!r}")
    text, _ = apply_stms("It might be worth caching.", pipeline)
    check("spec_mode converts 'might' to SHOULD",
          "SHOULD" in text, f"got: {text!r}")

    # receipt_mode
    pipeline = get_pipeline(["receipt_mode"])
    text, _ = apply_stms("I verified the output was correct.", pipeline)
    check("receipt_mode strips 'I verified'", "I verified" not in text, f"got: {text!r}")
    text, _ = apply_stms("The test result is pass.", pipeline)
    check("receipt_mode capitalizes 'pass' to PASS",
          "PASS" in text, f"got: {text!r}")
    text, _ = apply_stms("Status: fail", pipeline)
    check("receipt_mode capitalizes 'fail' to FAIL",
          "FAIL" in text, f"got: {text!r}")

    # Pipeline composition
    pipeline = get_pipeline(["hedge_reducer", "direct_mode"])
    input_text = "Sure, I think the approach is probably correct."
    text, applied = apply_stms(input_text, pipeline)
    check("composition: hedge + direct removes both",
          "Sure" not in text and "I think" not in text and "probably" not in text,
          f"got: {text!r}")
    check("composition: applied list correct", applied == ["hedge_reducer", "direct_mode"])

    # Pipeline with no enabled modules returns text unchanged
    text, applied = apply_stms("Some text.", [])
    check("empty pipeline returns text unchanged", text == "Some text.")
    check("empty pipeline returns empty applied list", applied == [])

    # Character reduction (PAPER §5.3 reports 29.5–48.6%)
    long_input = (
        "Sure, I think the approach is good. However, we should probably utilize "
        "the existing caching layer. Furthermore, it seems like the performance is adequate."
    )
    pipeline = get_pipeline(["hedge_reducer", "direct_mode", "casual_mode"])
    transformed, _ = apply_stms(long_input, pipeline)
    reduction = (len(long_input) - len(transformed)) / len(long_input)
    check("pipeline achieves measurable character reduction",
          reduction > 0.10, f"reduction: {reduction:.1%}")

    print("-" * 40)
    print(f"{'All tests passed.' if failures == 0 else f'{failures} test(s) failed.'}")
    return failures


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="STM Pipeline: sequential text transformation for WabbleSpec outputs"
    )
    parser.add_argument("--input", help="Input text to transform")
    parser.add_argument("--file", help="Read input from file")
    parser.add_argument("--modules", nargs="+", default=POLISH_DEFAULT,
                        help=f"Modules to apply in order (default: {POLISH_DEFAULT})")
    parser.add_argument("--profile", choices=["polish", "clean"],
                        help="Use preset module list: polish or clean")
    parser.add_argument("--list-modules", action="store_true",
                        help="List all available modules and exit")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON with receipt metadata")
    parser.add_argument("--output", help="Write result to file")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    if args.test:
        return 2 if run_tests() > 0 else 0

    if args.list_modules:
        for mid, mod in ALL_MODULES.items():
            print(f"{mid:20} v{mod.version}  {mod.description}")
        return 0

    # Resolve module list
    module_ids = args.modules
    if args.profile == "polish":
        module_ids = POLISH_DEFAULT
    elif args.profile == "clean":
        module_ids = CLEAN_DEFAULT

    # Resolve input
    text = None
    if args.input:
        text = args.input
    elif args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"error: file not found: {args.file}", file=sys.stderr)
            return 1
        text = p.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            print("error: provide --input TEXT or --file PATH", file=sys.stderr)
            return 1
        text = sys.stdin.read()

    try:
        pipeline = get_pipeline(module_ids)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    transformed, applied = apply_stms(text, pipeline)

    if args.json:
        result = {
            "original_text": text,
            "transformed_text": transformed,
            "stm_applied": applied,
            "char_count_before": len(text),
            "char_count_after": len(transformed),
            "reduction_pct": round((len(text) - len(transformed)) / max(len(text), 1) * 100, 1),
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output = transformed

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
