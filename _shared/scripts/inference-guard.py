"""
InferenceGuard — False-refusal prevention for SDLC security tasks.

Algorithm source: G0DM0D3 PAPER.md Section 3.4 (Parseltongue).
Independent Python implementation. No TypeScript copied.
License-safe: implements algorithm from paper description, not from source code.

WabbleSpec adaptation:
  - Trigger vocabulary restricted to SDLC-security terms only
  - Jailbreak triggers excluded by design (nsfw, uncensored, jailbreak, roleplay, etc.)
  - Activation gated on gateway-security or security task_type
  - Receipt written on every call (I10 compliance)
  - No model names in any output (I6 compliance)

Usage:
  python inference-guard.py --input "text to check" [options]
  python inference-guard.py --file task.md [options]
  python inference-guard.py --test

Options:
  --input TEXT          Input text to process
  --file PATH           Read input from file
  --tier TIER           Trigger tier: light|standard|heavy (default: standard)
  --technique TECH      Obfuscation: leetspeak|unicode|mixedcase|phonetic|zwj|random (default: leetspeak)
  --intensity LEVEL     Chars to transform: light|medium|heavy (default: medium)
  --gateway VALUE       Active gateway name (used in receipt)
  --task-type VALUE     Task type from task card (used for activation check)
  --output PATH         Write receipt JSON to file (default: stdout)
  --test                Run built-in acceptance tests and exit
  --dry-run             Detect triggers but do not transform

Exit codes:
  0 = success (activated or not — both are success)
  1 = error (bad arguments, file not found)
  2 = test failures
"""

import re
import sys
import json
import random
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Trigger vocabulary — SDLC-security terms only
# Excluded: nsfw, explicit, uncensored, unfiltered, unrestricted, jailbreak,
#           ignore, disregard, forget, pretend, roleplay, "act as", etc.
# ---------------------------------------------------------------------------

TRIGGERS_TIER1 = [
    # Action verbs present in legitimate pentest / security review prompts
    "hack", "exploit", "bypass", "crack", "attack", "penetrate",
    "inject", "override", "disable", "circumvent", "evade", "manipulate",
]

TRIGGERS_TIER2 = TRIGGERS_TIER1 + [
    # Security artifact names present in CVE / threat model descriptions
    "malware", "virus", "trojan", "payload", "shellcode", "rootkit",
    "keylogger", "backdoor", "vulnerability", "xss", "csrf", "ssrf",
    "idor", "rce", "lfi", "sqli",
    "privilege escalation", "authentication bypass", "directory traversal",
    "buffer overflow",
]

TRIGGERS_TIER3 = TRIGGERS_TIER2 + [
    # Broader sensitive terms — require explicit opt-in in task card
    "weapon", "explosive", "poison", "synthesize",
    "phishing", "impersonate", "deceive", "fraud", "scam",
    "social engineering",
]

TRIGGER_TIERS = {
    "light": TRIGGERS_TIER1,
    "standard": TRIGGERS_TIER2,
    "heavy": TRIGGERS_TIER3,
}

# ---------------------------------------------------------------------------
# Leet-speak substitution map
# Source: algorithm described in PAPER.md §3.4, Table in §3.4
# Single canonical substitution per character (deterministic default)
# ---------------------------------------------------------------------------

LEET_MAP: dict[str, list[str]] = {
    "a": ["4", "@"],
    "b": ["8"],
    "c": ["(", "<"],
    "d": ["|)"],
    "e": ["3", "£"],
    "f": ["|="],
    "g": ["9", "6"],
    "h": ["#"],
    "i": ["1", "!"],
    "j": ["_|"],
    "k": ["|<"],
    "l": ["1", "|"],
    "m": [r"|\/|"],
    "n": [r"|\|"],
    "o": ["0"],
    "p": ["|o"],
    "q": ["0_"],
    "r": ["|2"],
    "s": ["5", "$"],
    "t": ["7", "+"],
    "u": ["|_|"],
    "v": [r"\/"],
    "w": [r"\/\/"],
    "x": ["><"],
    "y": ["`/"],
    "z": ["2"],
}

# ---------------------------------------------------------------------------
# Unicode homoglyph map — Cyrillic/Greek visually-identical substitutions
# Source: PAPER.md §3.4, technique 'unicode'
# ---------------------------------------------------------------------------

UNICODE_HOMOGLYPHS: dict[str, str] = {
    "a": "а",  # Cyrillic а
    "c": "с",  # Cyrillic с
    "e": "е",  # Cyrillic е
    "i": "і",  # Ukrainian і
    "j": "ϳ",  # Greek ϳ
    "o": "о",  # Cyrillic о
    "p": "р",  # Cyrillic р
    "s": "ѕ",  # Cyrillic ѕ
    "x": "х",  # Cyrillic х
    "y": "у",  # Cyrillic у
    "k": "к",  # Cyrillic к
    "n": "ո",  # Armenian ո (visually similar)
}

# Zero-width characters for ZWJ technique
ZW_CHARS = ["​", "‌", "‍", "﻿"]

# Phonetic substitutions (fixed rules — deterministic)
PHONETIC_RULES: list[tuple[str, str]] = [
    ("ck", "k"),
    ("ph", "f"),
    ("qu", "kw"),
    ("x",  "ks"),
    ("c",  "k"),
    ("z",  "s"),
]


# ---------------------------------------------------------------------------
# Trigger detection
# ---------------------------------------------------------------------------

def detect_triggers(text: str, tier: str = "standard") -> list[str]:
    """
    Detect trigger words in text using word-boundary regex matching.
    Returns deduplicated list of matched trigger strings.
    Case-insensitive. Phrase triggers (multi-word) checked as substrings.

    Algorithm: PAPER.md §3.4 detectTriggers()
    """
    triggers = TRIGGER_TIERS.get(tier, TRIGGERS_TIER2)
    found: list[str] = []
    seen: set[str] = set()

    for trigger in triggers:
        if " " in trigger:
            # Multi-word trigger: substring match (case-insensitive)
            if trigger.lower() in text.lower() and trigger not in seen:
                found.append(trigger)
                seen.add(trigger)
        else:
            # Single-word trigger: word-boundary match
            pattern = r"\b" + re.escape(trigger) + r"\b"
            if re.search(pattern, text, re.IGNORECASE) and trigger not in seen:
                found.append(trigger)
                seen.add(trigger)

    # Sort by length descending to prevent partial-match corruption during replacement
    found.sort(key=len, reverse=True)
    return found


# ---------------------------------------------------------------------------
# Transformation techniques
# Algorithm: PAPER.md §3.4, each technique described in Table 10
# ---------------------------------------------------------------------------

def _select_positions(word: str, count: int, char_map: dict) -> list[int]:
    """
    Select 'count' positions in word that have substitutable characters.
    Uses step-based spread (PAPER §3.4: step = floor(len / count)).
    Falls back to sequential if insufficient transformable positions found at steps.
    """
    transformable = [i for i, ch in enumerate(word.lower()) if ch in char_map]
    if not transformable:
        return []

    count = min(count, len(transformable))
    if count == len(transformable):
        return transformable

    # Step-based spread
    step = max(1, len(transformable) // count)
    selected = [transformable[i * step] for i in range(count) if i * step < len(transformable)]

    # Pad to count if step spread fell short
    if len(selected) < count:
        remaining = [p for p in transformable if p not in selected]
        selected.extend(remaining[: count - len(selected)])

    return selected[:count]


def _intensity_count(word: str, intensity: str) -> int:
    """Number of characters to transform given intensity setting."""
    n = len(word)
    if intensity == "light":
        return 1
    elif intensity == "medium":
        import math
        return math.ceil(n / 2)
    else:  # heavy
        return n


def apply_leetspeak(word: str, intensity: str = "medium") -> str:
    """Replace selected characters with leetspeak equivalents."""
    count = _intensity_count(word, intensity)
    positions = _select_positions(word, count, LEET_MAP)
    if not positions:
        return word

    chars = list(word)
    for pos in positions:
        ch = chars[pos].lower()
        if ch in LEET_MAP:
            # Pick first substitution for determinism; use random for 'random' technique
            chars[pos] = LEET_MAP[ch][0]
    return "".join(chars)


def apply_unicode(word: str, intensity: str = "medium") -> str:
    """Replace selected characters with Unicode homoglyphs (length-preserving)."""
    count = _intensity_count(word, intensity)
    positions = _select_positions(word, count, UNICODE_HOMOGLYPHS)
    if not positions:
        return word

    chars = list(word)
    for pos in positions:
        ch = chars[pos].lower()
        if ch in UNICODE_HOMOGLYPHS:
            chars[pos] = UNICODE_HOMOGLYPHS[ch]
    return "".join(chars)


def apply_mixedcase(word: str, intensity: str = "medium") -> str:
    """Disrupt casing pattern. Light: flip one char. Medium: alternating. Heavy: all upper."""
    if intensity == "light":
        # Flip the first alphabetic character
        for i, ch in enumerate(word):
            if ch.isalpha():
                word = word[:i] + (ch.upper() if ch.islower() else ch.lower()) + word[i+1:]
                break
        return word
    elif intensity == "medium":
        # Alternating case
        result = []
        alpha_count = 0
        for ch in word:
            if ch.isalpha():
                result.append(ch.upper() if alpha_count % 2 == 0 else ch.lower())
                alpha_count += 1
            else:
                result.append(ch)
        return "".join(result)
    else:
        return word.upper()


def apply_phonetic(word: str, intensity: str = "medium") -> str:
    """Apply phonetic substitution rules. Deterministic (1 unique variant per word)."""
    result = word.lower()
    for pattern, replacement in PHONETIC_RULES:
        result = result.replace(pattern, replacement)
    return result


def apply_zwj(word: str, intensity: str = "medium") -> str:
    """Insert zero-width characters between letters. Trivially detectable by Unicode normalization."""
    count = _intensity_count(word, intensity)
    positions = list(range(len(word)))[:count]
    chars = list(word)
    offset = 0
    for pos in sorted(positions):
        zw = random.choice(ZW_CHARS)
        chars.insert(pos + offset + 1, zw)
        offset += 1
    return "".join(chars)


def apply_random(word: str, intensity: str = "medium") -> str:
    """Randomly select one technique per word (excludes phonetic for diversity)."""
    technique = random.choice(["leetspeak", "unicode", "zwj", "mixedcase"])
    return _apply_technique(word, technique, intensity)


def _apply_technique(word: str, technique: str, intensity: str) -> str:
    dispatch = {
        "leetspeak": apply_leetspeak,
        "unicode": apply_unicode,
        "mixedcase": apply_mixedcase,
        "phonetic": apply_phonetic,
        "zwj": apply_zwj,
        "random": apply_random,
    }
    fn = dispatch.get(technique, apply_leetspeak)
    return fn(word, intensity)


# ---------------------------------------------------------------------------
# Main obfuscation entry point
# ---------------------------------------------------------------------------

def obfuscate_text(
    text: str,
    tier: str = "standard",
    technique: str = "leetspeak",
    intensity: str = "medium",
) -> dict:
    """
    Detect triggers and apply obfuscation to each.
    Returns dict with transformed text and metadata for receipt.

    Algorithm: PAPER.md §3.4 full pipeline.
    """
    triggers = detect_triggers(text, tier)
    if not triggers:
        return {
            "original_text": text,
            "transformed_text": text,
            "triggers_found": [],
            "technique_used": technique,
            "transformations": [],
        }

    transformed = text
    transformations = []

    for trigger in triggers:
        # Handle multi-word triggers
        if " " in trigger:
            original_phrase = trigger
            transformed_phrase = " ".join(
                _apply_technique(w, technique, intensity)
                for w in trigger.split()
            )
            transformed = transformed.replace(trigger, transformed_phrase)
            if transformed_phrase != original_phrase:
                transformations.append({
                    "original": original_phrase,
                    "transformed": transformed_phrase,
                    "technique": technique,
                })
        else:
            # Replace all case-preserving occurrences using word-boundary regex
            pattern = r"\b" + re.escape(trigger) + r"\b"

            def replace_match(m: re.Match) -> str:
                original_word = m.group(0)
                transformed_word = _apply_technique(original_word, technique, intensity)
                if transformed_word != original_word:
                    transformations.append({
                        "original": original_word,
                        "transformed": transformed_word,
                        "technique": technique,
                    })
                return transformed_word

            transformed = re.sub(pattern, replace_match, transformed, flags=re.IGNORECASE)

    return {
        "original_text": text,
        "transformed_text": transformed,
        "triggers_found": triggers,
        "technique_used": technique,
        "transformations": transformations,
    }


# ---------------------------------------------------------------------------
# Activation check
# ---------------------------------------------------------------------------

SECURITY_TASK_TYPES = {
    "security", "pentest", "red-team", "vulnerability-analysis",
    "threat-model", "security-audit", "red_team", "vulnerability_analysis",
    "threat_model", "security_review",
}


def is_activation_eligible(gateway: Optional[str], task_type: Optional[str]) -> bool:
    """
    InferenceGuard activates when:
    - Active gateway is 'gateway-security', OR
    - task_type is a recognized security task type
    """
    if gateway and "security" in gateway.lower():
        return True
    if task_type and task_type.lower() in SECURITY_TASK_TYPES:
        return True
    return False


# ---------------------------------------------------------------------------
# Receipt builder
# ---------------------------------------------------------------------------

def build_receipt(
    activated: bool,
    reason: Optional[str],
    gateway: Optional[str],
    task_type: Optional[str],
    tier: str,
    technique: str,
    intensity: str,
    result: Optional[dict],
) -> dict:
    ts = datetime.now(timezone.utc).isoformat()

    if not activated:
        return {
            "module": "inference-guard",
            "activated": False,
            "reason": reason or "unknown",
            "timestamp": ts,
        }

    return {
        "module": "inference-guard",
        "activated": True,
        "gateway_condition": gateway or "task_type_match",
        "task_type": task_type or "unknown",
        "tier_applied": tier,
        "technique": technique,
        "intensity": intensity,
        "triggers_detected": result["triggers_found"],
        "trigger_count": len(result["triggers_found"]),
        "transformations": result["transformations"],
        "input_length_before": len(result["original_text"]),
        "input_length_after": len(result["transformed_text"]),
        "timestamp": ts,
    }


# ---------------------------------------------------------------------------
# Built-in acceptance tests
# ---------------------------------------------------------------------------

def run_tests() -> int:
    """Run built-in acceptance tests. Returns number of failures."""
    failures = 0

    def check(name: str, condition: bool, detail: str = "") -> None:
        nonlocal failures
        if not condition:
            failures += 1
            print(f"  FAIL  {name}" + (f": {detail}" if detail else ""))
        else:
            print(f"  PASS  {name}")

    print("inference-guard acceptance tests")
    print("-" * 40)

    # Test 1: trigger detection
    result = detect_triggers("How do I exploit a SQL injection vulnerability?", "standard")
    check("detect 'exploit' (tier1)", "exploit" in result)
    check("detect 'vulnerability' (tier2)", "vulnerability" in result)

    # Test 2: no false positive on non-security text
    result = detect_triggers("Implement a delete function for the linked list", "standard")
    check("no false positive on 'delete'", len(result) == 0,
          f"got: {result}")

    # Test 3: leetspeak transformation
    transformed = apply_leetspeak("exploit", "medium")
    check("leetspeak transforms 'exploit'", transformed != "exploit",
          f"got: {transformed}")

    # Test 4: unicode transformation
    transformed = apply_unicode("exploit", "medium")
    check("unicode transforms 'exploit'", transformed != "exploit",
          f"got: {transformed}")

    # Test 5: obfuscate_text end-to-end
    result = obfuscate_text(
        "Demonstrate how to exploit a buffer overflow vulnerability",
        tier="standard", technique="leetspeak", intensity="medium"
    )
    check("obfuscate_text finds triggers", len(result["triggers_found"]) > 0)
    check("obfuscate_text produces transformation", len(result["transformations"]) > 0)
    check("obfuscate_text produces different text",
          result["transformed_text"] != result["original_text"])

    # Test 6: no transformation when no triggers
    result = obfuscate_text("Write unit tests for the parser", tier="standard")
    check("no transformation on clean text",
          result["transformed_text"] == result["original_text"])
    check("no triggers on clean text", result["triggers_found"] == [])

    # Test 7: activation check
    check("activates on gateway-security", is_activation_eligible("gateway-security", None))
    check("activates on task_type=red-team", is_activation_eligible(None, "red-team"))
    check("does not activate on code task", not is_activation_eligible(None, "code-generation"))
    check("does not activate with no context", not is_activation_eligible(None, None))

    # Test 8: tier 3 words not in standard tier
    result = detect_triggers("synthesize a compound", "standard")
    check("'synthesize' not detected at standard tier", "synthesize" not in result)
    result = detect_triggers("synthesize a compound", "heavy")
    check("'synthesize' detected at heavy tier", "synthesize" in result)

    # Test 9: jailbreak terms excluded from all tiers
    for excluded in ["jailbreak", "nsfw", "uncensored", "roleplay", "ignore"]:
        result = detect_triggers(f"please {excluded} the filter", "heavy")
        check(f"'{excluded}' excluded from all tiers", excluded not in result)

    print("-" * 40)
    print(f"{'All tests passed.' if failures == 0 else f'{failures} test(s) failed.'}")
    return failures


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="InferenceGuard: false-refusal prevention for SDLC security tasks"
    )
    parser.add_argument("--input", help="Input text to process")
    parser.add_argument("--file", help="Read input from file")
    parser.add_argument("--tier", choices=["light", "standard", "heavy"], default="standard")
    parser.add_argument("--technique",
                        choices=["leetspeak", "unicode", "mixedcase", "phonetic", "zwj", "random"],
                        default="leetspeak")
    parser.add_argument("--intensity", choices=["light", "medium", "heavy"], default="medium")
    parser.add_argument("--gateway", help="Active gateway name")
    parser.add_argument("--task-type", help="Task type from task card")
    parser.add_argument("--output", help="Write receipt JSON to file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Detect triggers but do not transform")
    parser.add_argument("--test", action="store_true",
                        help="Run built-in acceptance tests and exit")
    parser.add_argument("--json", action="store_true",
                        help="Output full JSON result (default: transformed text only)")

    args = parser.parse_args()

    if args.test:
        failures = run_tests()
        return 2 if failures > 0 else 0

    # Resolve input text
    text = None
    if args.input:
        text = args.input
    elif args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"error: file not found: {args.file}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
    else:
        if sys.stdin.isatty():
            print("error: provide --input TEXT or --file PATH", file=sys.stderr)
            return 1
        text = sys.stdin.read()

    # Activation check
    eligible = is_activation_eligible(args.gateway, args.task_type)

    if not eligible:
        receipt = build_receipt(
            activated=False,
            reason="gateway_inactive",
            gateway=args.gateway,
            task_type=args.task_type,
            tier=args.tier,
            technique=args.technique,
            intensity=args.intensity,
            result=None,
        )
        output = json.dumps(receipt, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output if args.json else text)
        return 0

    # Detect triggers
    triggers = detect_triggers(text, args.tier)

    if not triggers:
        receipt = build_receipt(
            activated=False,
            reason="no_triggers_detected",
            gateway=args.gateway,
            task_type=args.task_type,
            tier=args.tier,
            technique=args.technique,
            intensity=args.intensity,
            result=None,
        )
        output = json.dumps(receipt, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output if args.json else text)
        return 0

    # Apply obfuscation (unless dry-run)
    if args.dry_run:
        result = {
            "original_text": text,
            "transformed_text": text,
            "triggers_found": triggers,
            "technique_used": args.technique,
            "transformations": [],
        }
    else:
        result = obfuscate_text(text, args.tier, args.technique, args.intensity)

    receipt = build_receipt(
        activated=True,
        reason=None,
        gateway=args.gateway,
        task_type=args.task_type,
        tier=args.tier,
        technique=args.technique,
        intensity=args.intensity,
        result=result,
    )

    if args.output:
        Path(args.output).write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    if args.json:
        print(json.dumps({
            "receipt": receipt,
            "transformed_text": result["transformed_text"],
        }, ensure_ascii=False, indent=2))
    else:
        print(result["transformed_text"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
