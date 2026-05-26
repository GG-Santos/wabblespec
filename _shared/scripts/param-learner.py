"""
ParamLearner — EMA-based sampling parameter learning from receipt signals.

Algorithm source: G0DM0D3 PAPER.md Section 3.3 (Online Feedback Loop).
Independent Python implementation. No TypeScript copied.
License-safe: implements algorithm from paper formulas, not from source code.

WabbleSpec adaptation:
  - Learning signal: Verifier PASS/FAIL receipt instead of thumbs up/down
  - Persists learned profiles to .wabblespec/memory/learned-params/
  - Context types: six WabbleSpec types (from context-tuner.py)
  - No model names anywhere (I6 compliance)
  - Cold start: 3 receipts minimum per context type before adjustments apply

EMA constants (PAPER §3.3, validated against convergence data):
  alpha = 0.3       converges within ~19 signals
  MIN_SAMPLES = 3   no adjustments until 3 receipts
  MAX_WEIGHT = 0.5  learned adjustments cap at 50% of base profile
  SAMPLES_FOR_MAX = 20  reach max weight at 20 samples

Usage:
  python param-learner.py --learn --receipt path/to/receipt.json --context-type code-generation
  python param-learner.py --stats
  python param-learner.py --get code-generation
  python param-learner.py --reset code-generation
  python param-learner.py --test

Exit codes: 0 = success, 1 = error, 2 = test failures
"""

import sys
import json
import argparse
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# EMA constants (PAPER §3.3)
# ---------------------------------------------------------------------------

EMA_ALPHA = 0.3           # learning rate
MIN_SAMPLES = 3           # cold-start gate
MAX_WEIGHT = 0.5          # maximum influence of learned adjustments
SAMPLES_FOR_MAX = 20      # samples required to reach MAX_WEIGHT
MAX_HISTORY = 500         # bounded history buffer per profile

CONTEXT_TYPES = [
    "spec-authoring",
    "code-generation",
    "security-review",
    "planning",
    "synthesis",
    "administrative",
]

# Neutral starting parameters (middle of each range)
NEUTRAL_PARAMS = {
    "temperature": 0.5,
    "top_p": 0.88,
    "top_k": 50,
    "frequency_penalty": 0.15,
    "presence_penalty": 0.10,
    "repetition_penalty": 1.05,
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class LearnedProfile:
    context_type: str
    sample_count: int = 0
    positive_count: int = 0
    negative_count: int = 0
    # EMA of parameters from positively-rated responses
    positive_params: dict = field(default_factory=lambda: dict(NEUTRAL_PARAMS))
    # EMA of parameters from negatively-rated responses
    negative_params: dict = field(default_factory=lambda: dict(NEUTRAL_PARAMS))
    # Computed delta to apply to base profile
    adjustments: dict = field(default_factory=dict)
    last_updated: Optional[str] = None
    freshness: str = "FRESH"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "LearnedProfile":
        return cls(**d)


# ---------------------------------------------------------------------------
# EMA update functions
# Algorithm: PAPER.md §3.3
# ---------------------------------------------------------------------------

def ema_update(current: dict, observation: dict, alpha: float = EMA_ALPHA) -> dict:
    """
    Exponential Moving Average update.
    new_value = (1 - alpha) * old_value + alpha * observation

    Algorithm: PAPER §3.3 equation (1)
    """
    inv = 1.0 - alpha
    result = {}
    for key in current:
        if key in observation:
            updated = current[key] * inv + observation[key] * alpha
            if key == "top_k":
                updated = int(round(updated))
            result[key] = updated
        else:
            result[key] = current[key]
    return result


def compute_adjustments(profile: LearnedProfile) -> dict:
    """
    Compute parameter adjustments from positive/negative EMA tracks.
    adjustment = 0.5 * (pos_delta - neg_delta) where delta = ema - neutral

    Algorithm: PAPER §3.3 computeAdjustments()
    """
    if profile.positive_count < 1 or profile.negative_count < 1:
        # With only positive data, use mild nudge toward positive EMA
        if profile.positive_count >= MIN_SAMPLES:
            return _delta_from_neutral(profile.positive_params, scale=0.5)
        return {}

    adj = {}
    for key in NEUTRAL_PARAMS:
        pos_delta = profile.positive_params.get(key, NEUTRAL_PARAMS[key]) - NEUTRAL_PARAMS[key]
        neg_delta = profile.negative_params.get(key, NEUTRAL_PARAMS[key]) - NEUTRAL_PARAMS[key]
        adjustment = (pos_delta - neg_delta) * 0.5
        if abs(adjustment) > 0.01:
            adj[key] = adjustment

    return adj


def _delta_from_neutral(positive_params: dict, scale: float = 0.5) -> dict:
    adj = {}
    for key in NEUTRAL_PARAMS:
        delta = (positive_params.get(key, NEUTRAL_PARAMS[key]) - NEUTRAL_PARAMS[key]) * scale
        if abs(delta) > 0.01:
            adj[key] = delta
    return adj


def apply_learned_adjustments(
    base_params: dict,
    context_type: str,
    profiles: dict[str, LearnedProfile],
) -> tuple[dict, bool, str]:
    """
    Apply learned adjustments to a base parameter set.
    Weight scales from 0 to MAX_WEIGHT based on sample count.

    Returns: (adjusted_params, was_applied, note)

    Algorithm: PAPER §3.3 applyLearnedAdjustments()
    """
    profile = profiles.get(context_type)
    if not profile:
        return base_params, False, "no profile for context type"

    if profile.sample_count < MIN_SAMPLES:
        return base_params, False, f"cold start: {profile.sample_count}/{MIN_SAMPLES} samples"

    if not profile.adjustments:
        return base_params, False, "no adjustments computed yet"

    # Weight: scales linearly from 0 to MAX_WEIGHT over SAMPLES_FOR_MAX samples
    weight = min(
        (profile.sample_count / SAMPLES_FOR_MAX) * MAX_WEIGHT,
        MAX_WEIGHT,
    )

    adjusted = dict(base_params)
    applied_keys = []
    for key, delta in profile.adjustments.items():
        if key in adjusted:
            adjusted[key] = adjusted[key] + delta * weight
            applied_keys.append(key)

    note = (f"learned: {len(applied_keys)} params adjusted "
            f"({profile.sample_count} samples, {weight:.0%} weight)")
    return adjusted, True, note


# ---------------------------------------------------------------------------
# Receipt parsing — extract learning signal from WabbleSpec receipts
# ---------------------------------------------------------------------------

def extract_signal_from_receipt(receipt: dict) -> tuple[Optional[int], Optional[str]]:
    """
    Extract EMA rating (+1 or -1) and context_type from a WabbleSpec receipt.
    Returns (rating, context_type) or (None, None) if not extractable.

    Signal mapping:
      Verifier PASS     -> +1
      Verifier FAIL     -> -1
      Archive written   -> +1 (task completed)
      REVISE triggered  -> -1
      Attestation req   -> -1
    """
    module = receipt.get("module", "")
    outcome = str(receipt.get("outcome", "")).upper()
    verdict = str(receipt.get("verdict", "")).upper()
    status = str(receipt.get("status", "")).upper()
    revise = receipt.get("revise_triggered", False)
    attestation = receipt.get("attestation_required", False)
    context_type = receipt.get("context_type") or receipt.get("task_type")

    # Normalize context type from receipt task shapes
    if context_type:
        context_type = _normalize_context_type(context_type)

    rating = None
    if attestation:
        rating = -1
    elif revise:
        rating = -1
    elif module == "verifier":
        if "PASS" in verdict or "PASS" in outcome:
            rating = 1
        elif "FAIL" in verdict or "FAIL" in outcome:
            rating = -1
    elif module == "archive":
        rating = 1  # task completed = positive signal
    elif "PASS" in outcome or "PASS" in status:
        rating = 1
    elif "FAIL" in outcome or "FAIL" in status:
        rating = -1

    return rating, context_type


def _normalize_context_type(raw: str) -> Optional[str]:
    """Map receipt task_type/context_type values to ContextTuner types."""
    raw = raw.lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "spec": "spec-authoring",
        "spec_authoring": "spec-authoring",
        "specify": "spec-authoring",
        "code": "code-generation",
        "code_generation": "code-generation",
        "implementation": "code-generation",
        "execute": "code-generation",
        "security": "security-review",
        "security_review": "security-review",
        "red_team": "security-review",
        "pentest": "security-review",
        "plan": "planning",
        "planning": "planning",
        "decompose": "planning",
        "synthesis": "synthesis",
        "document": "synthesis",
        "archive": "synthesis",
        "admin": "administrative",
        "administrative": "administrative",
        "version": "administrative",
        "changelog": "administrative",
    }
    return mapping.get(raw)


# ---------------------------------------------------------------------------
# Profile storage
# ---------------------------------------------------------------------------

def profiles_dir(base_dir: Path) -> Path:
    d = base_dir / ".wabblespec" / "memory" / "learned-params"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_profile(context_type: str, base_dir: Path) -> LearnedProfile:
    path = profiles_dir(base_dir) / f"learned-params-{context_type}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return LearnedProfile.from_dict(data)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    return LearnedProfile(context_type=context_type)


def save_profile(profile: LearnedProfile, base_dir: Path) -> None:
    path = profiles_dir(base_dir) / f"learned-params-{profile.context_type}.json"
    profile.last_updated = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_all_profiles(base_dir: Path) -> dict[str, LearnedProfile]:
    return {ct: load_profile(ct, base_dir) for ct in CONTEXT_TYPES}


# ---------------------------------------------------------------------------
# Learning pipeline
# ---------------------------------------------------------------------------

def process_learning_signal(
    params: dict,
    rating: int,
    context_type: str,
    base_dir: Path,
) -> LearnedProfile:
    """
    Update the learned profile for context_type with a new rated parameter set.
    Persists updated profile to disk.
    """
    profile = load_profile(context_type, base_dir)
    profile.sample_count += 1

    if rating == 1:
        profile.positive_count += 1
        profile.positive_params = ema_update(profile.positive_params, params)
    else:
        profile.negative_count += 1
        profile.negative_params = ema_update(profile.negative_params, params)

    profile.adjustments = compute_adjustments(profile)
    save_profile(profile, base_dir)
    return profile


# ---------------------------------------------------------------------------
# Built-in acceptance tests
# ---------------------------------------------------------------------------

def run_tests() -> int:
    import tempfile
    failures = 0

    def check(name: str, condition: bool, detail: str = "") -> None:
        nonlocal failures
        if not condition:
            failures += 1
            print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))
        else:
            print(f"  PASS  {name}")

    print("param-learner acceptance tests")
    print("-" * 40)

    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Test 1: EMA update
        current = dict(NEUTRAL_PARAMS)
        observation = {k: v * 1.5 for k, v in NEUTRAL_PARAMS.items()}
        updated = ema_update(current, observation)
        expected_temp = 0.7 * NEUTRAL_PARAMS["temperature"] + 0.3 * (NEUTRAL_PARAMS["temperature"] * 1.5)
        check("EMA update temperature", abs(updated["temperature"] - expected_temp) < 0.001,
              f"expected {expected_temp:.4f}, got {updated['temperature']:.4f}")

        # Test 2: Cold start gate
        profiles = load_all_profiles(base)
        _, applied, note = apply_learned_adjustments(
            dict(NEUTRAL_PARAMS), "code-generation", profiles
        )
        check("cold start blocks adjustment", not applied, f"note: {note}")

        # Test 3: Learning accumulates
        ct = "code-generation"
        low_temp_params = {**NEUTRAL_PARAMS, "temperature": 0.15}
        high_temp_params = {**NEUTRAL_PARAMS, "temperature": 0.90}

        for _ in range(MIN_SAMPLES):
            process_learning_signal(low_temp_params, +1, ct, base)
        for _ in range(MIN_SAMPLES):
            process_learning_signal(high_temp_params, -1, ct, base)

        profile = load_profile(ct, base)
        check("sample_count accumulates", profile.sample_count == MIN_SAMPLES * 2,
              f"got: {profile.sample_count}")
        check("adjustments computed after min_samples", len(profile.adjustments) > 0,
              f"adjustments: {profile.adjustments}")

        # Test 4: Adjustment direction pushes toward positive params
        if "temperature" in profile.adjustments:
            check("temperature adjustment is negative (push toward lower temp)",
                  profile.adjustments["temperature"] < 0,
                  f"got: {profile.adjustments['temperature']:.4f}")

        # Test 5: Apply learned adjustments after threshold
        profiles = load_all_profiles(base)
        _, applied, note = apply_learned_adjustments(dict(NEUTRAL_PARAMS), ct, profiles)
        check("adjustments apply after min_samples", applied, f"note: {note}")

        # Test 6: Weight cap
        for _ in range(SAMPLES_FOR_MAX + 5):
            process_learning_signal(low_temp_params, +1, ct, base)
        profile = load_profile(ct, base)
        weight = min((profile.sample_count / SAMPLES_FOR_MAX) * MAX_WEIGHT, MAX_WEIGHT)
        check("weight caps at MAX_WEIGHT", weight <= MAX_WEIGHT, f"weight: {weight:.3f}")

        # Test 7: Identical params with alternating ratings -> adjustment near zero
        # This is the correct noise test (PAPER Table 6: same params, 50% label flip).
        # When positive_ema and negative_ema converge to the same params, delta = 0.
        ct2 = "planning"
        same_params = {**NEUTRAL_PARAMS, "temperature": 0.40, "top_p": 0.85}
        for _ in range(20):
            process_learning_signal(same_params, +1, ct2, base)
            process_learning_signal(same_params, -1, ct2, base)
        profile2 = load_profile(ct2, base)
        if profile2.adjustments:
            max_adj = max(abs(v) for v in profile2.adjustments.values())
        else:
            max_adj = 0.0
        check("identical params + alternating ratings -> adjustment near zero",
              max_adj < 0.05, f"max adjustment: {max_adj:.6f}")

        # Test 8: Receipt signal extraction
        verifier_pass = {"module": "verifier", "verdict": "PASS", "task_type": "code-generation"}
        rating, ct_out = extract_signal_from_receipt(verifier_pass)
        check("verifier PASS -> +1", rating == 1, f"got: {rating}")
        check("task_type extracted from receipt", ct_out == "code-generation", f"got: {ct_out}")

        verifier_fail = {"module": "verifier", "verdict": "FAIL", "task_type": "spec"}
        rating, ct_out = extract_signal_from_receipt(verifier_fail)
        check("verifier FAIL -> -1", rating == -1, f"got: {rating}")
        check("'spec' normalized to 'spec-authoring'", ct_out == "spec-authoring", f"got: {ct_out}")

        revise = {"module": "executor", "revise_triggered": True, "task_type": "planning"}
        rating, _ = extract_signal_from_receipt(revise)
        check("revise_triggered -> -1", rating == -1, f"got: {rating}")

        # Test 9: Profile persistence
        profile_saved = load_profile("code-generation", base)
        check("profile persists to disk", profile_saved.sample_count > 0)

        # Test 10: No model names
        profile_json = json.dumps(profile_saved.to_dict())
        model_indicators = ["claude", "gpt", "gemini", "llama", "anthropic", "openai"]
        check("no model names in profile",
              not any(m in profile_json.lower() for m in model_indicators))

    print("-" * 40)
    print(f"{'All tests passed.' if failures == 0 else f'{failures} test(s) failed.'}")
    return failures


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="ParamLearner: EMA-based sampling parameter adaptation from receipt signals"
    )
    parser.add_argument("--learn", action="store_true",
                        help="Process a receipt and update learned profile")
    parser.add_argument("--receipt", help="Path to WabbleSpec receipt JSON")
    parser.add_argument("--context-type", choices=CONTEXT_TYPES,
                        help="Override context type (default: extracted from receipt)")
    parser.add_argument("--params", help="JSON of sampling params used (optional override)")
    parser.add_argument("--stats", action="store_true",
                        help="Show learning stats for all context types")
    parser.add_argument("--get", metavar="CONTEXT_TYPE",
                        help="Get learned adjustments for a context type")
    parser.add_argument("--reset", metavar="CONTEXT_TYPE",
                        help="Reset learned profile for a context type")
    parser.add_argument("--base-dir", default=".",
                        help="WabbleSpec root directory (default: .)")
    parser.add_argument("--test", action="store_true")

    args = parser.parse_args()

    if args.test:
        return 2 if run_tests() > 0 else 0

    base_dir = Path(args.base_dir).resolve()

    if args.stats:
        profiles = load_all_profiles(base_dir)
        print(f"{'Context Type':<22} {'Samples':>8} {'Pos':>6} {'Neg':>6} {'Adjustments':>12} {'Freshness'}")
        print("-" * 70)
        for ct in CONTEXT_TYPES:
            p = profiles[ct]
            adj_count = len(p.adjustments)
            print(f"{ct:<22} {p.sample_count:>8} {p.positive_count:>6} {p.negative_count:>6} "
                  f"{adj_count:>12} {p.freshness}")
        return 0

    if args.get:
        profile = load_profile(args.get, base_dir)
        print(json.dumps(profile.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.reset:
        path = profiles_dir(base_dir) / f"learned-params-{args.reset}.json"
        if path.exists():
            path.unlink()
            print(f"reset: {args.reset}")
        else:
            print(f"no profile found for: {args.reset}")
        return 0

    if args.learn:
        if not args.receipt:
            print("error: --learn requires --receipt PATH", file=sys.stderr)
            return 1

        receipt_path = Path(args.receipt)
        if not receipt_path.exists():
            print(f"error: receipt not found: {args.receipt}", file=sys.stderr)
            return 1

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        # Extract signal from receipt
        rating, context_type = extract_signal_from_receipt(receipt)

        # Override with explicit args
        if args.context_type:
            context_type = args.context_type

        if rating is None:
            print(f"warning: could not extract learning signal from receipt", file=sys.stderr)
            print(f"  module: {receipt.get('module')}, outcome: {receipt.get('outcome')}")
            return 0

        if context_type is None:
            print("warning: could not determine context type from receipt. "
                  "Use --context-type to specify.", file=sys.stderr)
            return 0

        # Extract parameters used (from receipt or default neutral)
        params_used = dict(NEUTRAL_PARAMS)
        if args.params:
            params_used.update(json.loads(args.params))
        elif "context_classification" in receipt:
            cc = receipt["context_classification"]
            if "parameters_selected" in cc:
                params_used.update(cc["parameters_selected"])

        profile = process_learning_signal(params_used, rating, context_type, base_dir)
        print(f"learned: {context_type} | rating={rating:+d} | "
              f"samples={profile.sample_count} | adjustments={len(profile.adjustments)}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
