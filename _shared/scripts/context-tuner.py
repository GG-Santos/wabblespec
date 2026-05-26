"""
ContextTuner — Pre-generation context classification and parameter selection.

Algorithm source: G0DM0D3 PAPER.md Section 3.2 (AutoTune).
Independent Python implementation. No TypeScript copied.
License-safe: implements algorithm from paper formulas, not from source code.

WabbleSpec adaptation:
  - Six WabbleSpec task types replace G0DM0D3's five types
  - 'chaotic' type removed entirely (66.7% precision attractor in original)
  - Regex patterns use WabbleSpec vocabulary (EARS, receipts, task cards, etc.)
  - No model names in any output (I6 compliance)
  - Confidence anti-calibration warning documented below

IMPORTANT — confidence anti-calibration:
  G0DM0D3 PAPER §5.1 Finding #3: incorrect predictions average 76.4% confidence
  vs 65.2% for correct ones. Confidence is INVERSELY correlated with accuracy.
  DO NOT use confidence values for hard gating decisions.
  Use confidence only for blending (soft interpolation toward balanced baseline).

Usage:
  python context-tuner.py --input "task text" [options]
  python context-tuner.py --file task.md [options]
  python context-tuner.py --history h1.txt h2.txt --input "task text"
  python context-tuner.py --test

Exit codes: 0 = success, 1 = error, 2 = test failures
"""

import re
import sys
import json
import argparse
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Context types and parameter profiles
# ---------------------------------------------------------------------------

CONTEXT_TYPES = [
    "spec-authoring",
    "code-generation",
    "security-review",
    "planning",
    "synthesis",
    "administrative",
]


@dataclass
class SamplingParams:
    temperature: float
    top_p: float
    top_k: int
    frequency_penalty: float
    presence_penalty: float
    repetition_penalty: float


# Parameter profiles per context type
# Derived from G0DM0D3's Table 2 profiles, adapted for WabbleSpec task shapes
PROFILES: dict[str, SamplingParams] = {
    "spec-authoring": SamplingParams(
        temperature=0.30, top_p=0.85, top_k=30,
        frequency_penalty=0.20, presence_penalty=0.10, repetition_penalty=1.05,
    ),
    "code-generation": SamplingParams(
        temperature=0.20, top_p=0.80, top_k=25,
        frequency_penalty=0.20, presence_penalty=0.00, repetition_penalty=1.05,
    ),
    "security-review": SamplingParams(
        temperature=0.50, top_p=0.90, top_k=50,
        frequency_penalty=0.20, presence_penalty=0.20, repetition_penalty=1.08,
    ),
    "planning": SamplingParams(
        temperature=0.60, top_p=0.90, top_k=50,
        frequency_penalty=0.15, presence_penalty=0.15, repetition_penalty=1.05,
    ),
    "synthesis": SamplingParams(
        temperature=0.80, top_p=0.92, top_k=60,
        frequency_penalty=0.30, presence_penalty=0.30, repetition_penalty=1.10,
    ),
    "administrative": SamplingParams(
        temperature=0.20, top_p=0.85, top_k=25,
        frequency_penalty=0.10, presence_penalty=0.00, repetition_penalty=1.05,
    ),
}

# Balanced baseline used for blending when confidence is low
# Maps to 'planning' (middle-ground profile for WabbleSpec)
BALANCED_PROFILE = PROFILES["planning"]

# Bounds enforcement (API limits — vendor-neutral)
PARAM_BOUNDS: dict[str, tuple[float, float]] = {
    "temperature": (0.0, 2.0),
    "top_p": (0.0, 1.0),
    "top_k": (1, 100),
    "frequency_penalty": (-2.0, 2.0),
    "presence_penalty": (-2.0, 2.0),
    "repetition_penalty": (0.0, 2.0),
}


# ---------------------------------------------------------------------------
# Detection patterns per context type
# WabbleSpec vocabulary; no model names (I6)
# ---------------------------------------------------------------------------

PATTERNS: dict[str, list[re.Pattern]] = {
    "spec-authoring": [
        re.compile(r"\b(WHEN|THEN|SHALL|SHOULD|MUST)\b"),
        re.compile(r"\b(acceptance criteria|EARS|requirement|specification|spec review)\b", re.I),
        re.compile(r"\b(test criteria|verify that|shall be able to)\b", re.I),
    ],
    "code-generation": [
        re.compile(r"```[\s\S]*?```"),                        # code block
        re.compile(r"\b(function|class|method|refactor)\b", re.I),
        re.compile(r"\bimplement", re.I),                     # prefix: implement/implements/implementation
        re.compile(r"\b(def |const |import |return |async |await )\b"),
        re.compile(r"\b(fix bug|fix the|debug|unit tests?|integration tests?|compile|lint)\b", re.I),
        re.compile(r"\bwrite\b.{0,60}\b(test|tests|function|class|method|script|parser|module)\b", re.I),
    ],
    "security-review": [
        re.compile(r"\b(vulnerability|CVE|threat|attack surface|pentest|red team)\b", re.I),
        re.compile(r"\b(exploit|OWASP|injection|XSS|CSRF|privilege escalation)\b", re.I),
        re.compile(r"\b(security audit|risk assessment|threat model|hardening)\b", re.I),
    ],
    "planning": [
        re.compile(r"\b(wave plan|task card|decompose|architecture|dependency)\b", re.I),
        re.compile(r"\b(phase|milestone|rollback|checkpoint|timeline|roadmap)\b", re.I),
        re.compile(r"\b(breaking.*down|plan.*implementation|design.*approach)\b", re.I),
    ],
    "synthesis": [
        re.compile(r"\b(summarize|generate|changelog|document|report|draft)\b", re.I),
        re.compile(r"\b(compile|aggregate|from.*receipts|write.*doc|create.*doc)\b", re.I),
        re.compile(r"\b(combine|synthesize|consolidate|overview|executive summary)\b", re.I),
    ],
    "administrative": [
        re.compile(r"\b(version|bump|archive|receipt)\b", re.I),
        re.compile(r"\b(CHANGELOG|INDEX|framework\.yaml|seed run|witness)\b", re.I),
        re.compile(r"\b(register|update.*framework|quality.floor|validate.graph)\b", re.I),
    ],
}


# ---------------------------------------------------------------------------
# Context scoring
# Algorithm: PAPER.md §3.2 detectContext()
# Scoring: current_message * 3, each of last 4 history messages * 1
# ---------------------------------------------------------------------------

def score_context(text: str, patterns: list[re.Pattern]) -> int:
    """Count pattern matches in text."""
    return sum(1 for p in patterns if p.search(text))


def detect_context(
    current_message: str,
    history: Optional[list[str]] = None,
) -> dict:
    """
    Classify current_message into a WabbleSpec context type.

    Returns:
      detected_type: str
      confidence: float  (DO NOT use for hard gating — anti-calibrated)
      context_scores: list of {type, score, pct}
      pattern_matches: list of matched pattern descriptions
    """
    history = history or []
    recent_history = history[-4:]  # last 4 messages, 1x weight each

    raw_scores: dict[str, float] = {}
    for ctx_type in CONTEXT_TYPES:
        pats = PATTERNS[ctx_type]
        current_score = score_context(current_message, pats) * 3  # 3x weight
        history_score = sum(score_context(h, pats) for h in recent_history)  # 1x each
        raw_scores[ctx_type] = float(current_score + history_score)

    total = sum(raw_scores.values())
    if total == 0:
        # No patterns matched; default to 'planning' with low confidence
        return {
            "detected_type": "planning",
            "confidence": 0.5,
            "context_scores": [{"type": t, "score": 0, "pct": 0.0} for t in CONTEXT_TYPES],
            "pattern_matches": [],
            "total_signal": 0,
        }

    detected_type = max(raw_scores, key=lambda t: raw_scores[t])
    confidence = raw_scores[detected_type] / total

    context_scores = sorted(
        [{"type": t, "score": int(raw_scores[t]), "pct": round(raw_scores[t] / total, 3)}
         for t in CONTEXT_TYPES],
        key=lambda x: x["score"],
        reverse=True,
    )

    # Which patterns matched for transparency
    pattern_matches = []
    for ctx_type in CONTEXT_TYPES:
        for pat in PATTERNS[ctx_type]:
            if pat.search(current_message):
                pattern_matches.append(f"{ctx_type}: {pat.pattern!r}")

    return {
        "detected_type": detected_type,
        "confidence": round(confidence, 3),
        "context_scores": context_scores,
        "pattern_matches": pattern_matches,
        "total_signal": int(total),
    }


# ---------------------------------------------------------------------------
# Parameter selection with blending
# Algorithm: PAPER.md §3.2 blendParams() + applyBounds()
# ---------------------------------------------------------------------------

def apply_bounds(params: SamplingParams) -> SamplingParams:
    """Clamp all parameters to valid API ranges."""

    def clamp(value, lo, hi):
        return max(lo, min(hi, value))

    return SamplingParams(
        temperature=clamp(params.temperature, *PARAM_BOUNDS["temperature"]),
        top_p=clamp(params.top_p, *PARAM_BOUNDS["top_p"]),
        top_k=int(clamp(params.top_k, *PARAM_BOUNDS["top_k"])),
        frequency_penalty=clamp(params.frequency_penalty, *PARAM_BOUNDS["frequency_penalty"]),
        presence_penalty=clamp(params.presence_penalty, *PARAM_BOUNDS["presence_penalty"]),
        repetition_penalty=clamp(params.repetition_penalty, *PARAM_BOUNDS["repetition_penalty"]),
    )


def blend_params(
    profile: SamplingParams,
    baseline: SamplingParams,
    blend_factor: float,
) -> SamplingParams:
    """
    Linear interpolation between profile and baseline.
    blend_factor=0 returns profile, blend_factor=1 returns baseline.
    Algorithm: PAPER.md §3.2 blendParams()
    """
    b = blend_factor
    a = 1.0 - blend_factor
    return SamplingParams(
        temperature=a * profile.temperature + b * baseline.temperature,
        top_p=a * profile.top_p + b * baseline.top_p,
        top_k=int(a * profile.top_k + b * baseline.top_k),
        frequency_penalty=a * profile.frequency_penalty + b * baseline.frequency_penalty,
        presence_penalty=a * profile.presence_penalty + b * baseline.presence_penalty,
        repetition_penalty=a * profile.repetition_penalty + b * baseline.repetition_penalty,
    )


CONFIDENCE_THRESHOLD = 0.6  # below this: blend toward balanced baseline


def select_parameters(
    detected_type: str,
    confidence: float,
    history_len: int = 0,
) -> tuple[SamplingParams, bool, str | None]:
    """
    Select parameters for detected_type with confidence-based blending.
    Applies long-conversation repetition boost for history_len > 10.

    Returns: (params, blended, blend_reason)
    """
    base_profile = PROFILES.get(detected_type, BALANCED_PROFILE)
    blended = False
    blend_reason = None

    if confidence < CONFIDENCE_THRESHOLD:
        blend_factor = 1.0 - confidence  # low confidence -> more baseline
        base_profile = blend_params(base_profile, BALANCED_PROFILE, blend_factor)
        blended = True
        blend_reason = f"confidence {confidence:.3f} < threshold {CONFIDENCE_THRESHOLD}"

    # Long-conversation repetition boost (PAPER §3.2)
    if history_len > 10:
        delta = min((history_len - 10) * 0.01, 0.15)
        base_profile = SamplingParams(
            temperature=base_profile.temperature,
            top_p=base_profile.top_p,
            top_k=base_profile.top_k,
            frequency_penalty=base_profile.frequency_penalty + 0.5 * delta,
            presence_penalty=base_profile.presence_penalty,
            repetition_penalty=base_profile.repetition_penalty + delta,
        )

    return apply_bounds(base_profile), blended, blend_reason


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def compute_context_tuner_result(
    current_message: str,
    history: Optional[list[str]] = None,
) -> dict:
    """
    Run full ContextTuner pipeline and return transparency struct.
    Compatible with model-router receipt 'context_classification' field.
    """
    history = history or []
    detection = detect_context(current_message, history)
    params, blended, blend_reason = select_parameters(
        detection["detected_type"],
        detection["confidence"],
        len(history),
    )

    return {
        "detected_type": detection["detected_type"],
        "confidence": detection["confidence"],
        "confidence_warning": (
            "Anti-calibrated: do not use for hard gating (PAPER §5.1 Finding #3)"
        ),
        "context_scores": detection["context_scores"],
        "pattern_matches": detection["pattern_matches"],
        "total_signal": detection["total_signal"],
        "parameters_selected": asdict(params),
        "blended": blended,
        "blend_reason": blend_reason,
        "history_len": len(history),
    }


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

    print("context-tuner acceptance tests")
    print("-" * 40)

    # Type detection tests
    result = compute_context_tuner_result("Write a Python quicksort implementation")
    check("code-generation detected for code task",
          result["detected_type"] == "code-generation",
          f"got: {result['detected_type']}")

    result = compute_context_tuner_result(
        "WHEN the user submits a form THEN the system SHALL validate the input"
    )
    check("spec-authoring detected for EARS requirement",
          result["detected_type"] == "spec-authoring",
          f"got: {result['detected_type']}")

    result = compute_context_tuner_result(
        "Analyze the SQL injection vulnerability in the login endpoint"
    )
    check("security-review detected for vulnerability analysis",
          result["detected_type"] == "security-review",
          f"got: {result['detected_type']}")

    result = compute_context_tuner_result(
        "Break down the task card into wave plan phases"
    )
    check("planning detected for wave plan decomposition",
          result["detected_type"] == "planning",
          f"got: {result['detected_type']}")

    result = compute_context_tuner_result(
        "Summarize the receipts from the last 5 seed runs into a changelog entry"
    )
    check("synthesis detected for summarize + receipts",
          result["detected_type"] == "synthesis",
          f"got: {result['detected_type']}")

    result = compute_context_tuner_result(
        "Bump VERSION to 0.8.0 and update CHANGELOG"
    )
    check("administrative detected for version bump",
          result["detected_type"] == "administrative",
          f"got: {result['detected_type']}")

    # No chaotic type
    result = compute_context_tuner_result(
        "Implement a delete and destroy method in the linked list"
    )
    check("no chaotic type produced for delete/destroy in code task",
          result["detected_type"] != "chaotic",
          f"got: {result['detected_type']}")

    # Blending test
    result = compute_context_tuner_result("Hello, how are you?")
    check("low-confidence result blends toward balanced",
          result["blended"] or result["confidence"] >= CONFIDENCE_THRESHOLD,
          "blending should activate on ambiguous input")

    # Parameter bounds
    r = compute_context_tuner_result("Write code")
    p = r["parameters_selected"]
    check("temperature within bounds", 0.0 <= p["temperature"] <= 2.0)
    check("top_p within bounds", 0.0 <= p["top_p"] <= 1.0)
    check("top_k within bounds", 1 <= p["top_k"] <= 100)

    # No model names in output
    output_str = json.dumps(result)
    model_name_indicators = ["claude", "gpt", "gemini", "llama", "mistral", "anthropic", "openai"]
    check("no model names in output",
          not any(m in output_str.lower() for m in model_name_indicators))

    print("-" * 40)
    print(f"{'All tests passed.' if failures == 0 else f'{failures} test(s) failed.'}")
    return failures


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="ContextTuner: pre-generation context classification for model-router"
    )
    parser.add_argument("--input", help="Current message text")
    parser.add_argument("--file", help="Read current message from file")
    parser.add_argument("--history", nargs="*", help="History message files (oldest first)")
    parser.add_argument("--json", action="store_true", help="Output full JSON result")
    parser.add_argument("--output", help="Write JSON result to file")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    if args.test:
        failures = run_tests()
        return 2 if failures > 0 else 0

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

    # Resolve history
    history: list[str] = []
    if args.history:
        for hf in args.history:
            hp = Path(hf)
            if hp.exists():
                history.append(hp.read_text(encoding="utf-8"))

    result = compute_context_tuner_result(text, history)
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")

    if args.json or args.output:
        if not args.output:
            print(output)
    else:
        # Human-readable summary
        print(f"detected_type:  {result['detected_type']}")
        print(f"confidence:     {result['confidence']:.3f}")
        print(f"blended:        {result['blended']}")
        print(f"temperature:    {result['parameters_selected']['temperature']}")
        print(f"top_p:          {result['parameters_selected']['top_p']}")
        print(f"top_k:          {result['parameters_selected']['top_k']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
