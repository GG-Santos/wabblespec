#!/usr/bin/env python3
"""Lint prompts and skill files for cross-provider compatibility.

Checks for:
- Vendor-specific language that should be parameterized
- XML tag usage (cross-model compatibility)
- Token efficiency (filler word detection)
- Schema validation for JSON artifacts
- Hard-coded model identifiers
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from scripts.validation import (
        validate_phase1_skill_content,
        validate_phase2_skill_content,
        validate_phase3_skill_content,
    )
except ModuleNotFoundError:  # Allows `python scripts/lint_prompts.py ...`.
    from validation import (
        validate_phase1_skill_content,
        validate_phase2_skill_content,
        validate_phase3_skill_content,
    )

# ---------------------------------------------------------------------------
# Lint Rules
# ---------------------------------------------------------------------------

class LintResult:
    def __init__(self, level: str, rule: str, message: str, file: str, line: int = 0):
        self.level = level  # ERROR, WARNING, INFO
        self.rule = rule
        self.message = message
        self.file = file
        self.line = line

    def __str__(self):
        loc = f":{self.line}" if self.line else ""
        return f"[{self.level}] {self.file}{loc} - {self.rule}: {self.message}"


def _normalized_path(filepath: str) -> str:
    return filepath.replace("\\", "/")


EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".omc",
    ".omx",
    ".planning",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".svn",
    ".vscode",
    ".venv",
    "skill_benchmarks",
    "venv",
}


def should_skip_path(filepath: Path, root: Path) -> bool:
    """Skip local project artifacts that are not shipped skill content."""
    try:
        rel = filepath.relative_to(root)
    except ValueError:
        rel = filepath
    return any(part in EXCLUDED_DIRS for part in rel.parts)


def should_skip_rule(filepath: str, rule: str) -> bool:
    """Skip contexts where matches are rule examples, fixtures, or platform docs."""
    path = _normalized_path(filepath)
    if path.startswith("tests/"):
        return True
    if path.startswith("evaluations/live_provider_raw/"):
        return True
    if path.startswith("evaluations/live_provider_repair_prompts/"):
        return True
    if path == "scripts/lint_prompts.py":
        return True
    # Regression files intentionally embed bad prompt phrases as fixtures.
    # Linting the repo root should report shippable prompt problems, not the
    # test strings that prove the linter catches those problems.
    if re.fullmatch(r"scripts/phase\d+_[^/]+_regression\.py", path) and rule in {
        "all-caps-shouting",
        "scope-creep",
        "abstract-rules",
        "vendor-specific",
        "hardcoded-model",
    }:
        return True
    if rule in {"vendor-specific", "hardcoded-model"} and path.startswith("references/"):
        return True
    if rule in {"vendor-specific", "hardcoded-model"} and path.startswith("scripts/providers/"):
        return True
    if rule == "vendor-specific" and path in {"SKILL.md", "scripts/prompt_builder.py", "scripts/utils.py"}:
        return True
    # The grader, comparator, and analyzer enumerate the exact strings they
    # scan for in produced skills (vendor names, hardcoded model IDs, CLIs).
    # Naming the scan targets is the rubric's job, not coupling.
    if rule in {"vendor-specific", "hardcoded-model"} and path in {
        "agents/grader.md",
        "agents/comparator.md",
        "agents/analyzer.md",
    }:
        return True
    # v4 rules: anti-pattern documentation literally quotes the violations
    # to teach what to avoid. Quarantine those reference files. SKILL.md is
    # also teaching the anti-pattern (Theory-of-mind framing section).
    if rule in {"all-caps-shouting", "scope-creep", "abstract-rules"} and path in {
        "SKILL.md",
        "references/output-quality.md",
        "references/adversarial-corpus.md",
        "references/workshop-mode.md",
        "references/production-mode.md",
        "references/vibe-mode.md",
        "agents/grader.md",
        "agents/comparator.md",
        "agents/analyzer.md",
    }:
        return True
    # Adversarial corpus stores literal injection patterns - secret regex
    # examples are part of the curriculum, not real leakage
    if rule == "secret-patterns" and path == "references/adversarial-corpus.md":
        return True
    return False


def lint_vendor_specific(content: str, filepath: str) -> list[LintResult]:
    """Detect vendor-specific language that should be parameterized."""
    if should_skip_rule(filepath, "vendor-specific"):
        return []
    results = []
    patterns = [
        (r'\b[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?\s+(?:Code|Studio|Agents?)\b', "Runtime-branded environment reference"),
        (r'\b[a-z][a-z0-9_-]*\s+-p\b', "Hard-coded vendor CLI call"),
        (r'\b[A-Z0-9_]*(?:API_KEY|TOKEN|CODE)\b', "Provider-specific env var reference"),
    ]

    for i, line in enumerate(content.split("\n"), 1):
        if line.lstrip("﻿").startswith("#"):
            continue
        for pattern, message in patterns:
            if re.search(pattern, line):
                results.append(LintResult("WARNING", "vendor-specific", message, filepath, i))

    return results


def lint_xml_tags(content: str, filepath: str) -> list[LintResult]:
    """Detect XML tag usage that may not work across all providers."""
    if should_skip_rule(filepath, "xml-tags"):
        return []
    results = []
    # Skip markdown code blocks
    in_code_block = False
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        xml_tags = re.findall(r'</?(\w+)>', line)
        for tag in xml_tags:
            # Skip HTML tags
            html_tags = {"html", "body", "head", "div", "span", "p", "br", "hr",
                         "h1", "h2", "h3", "h4", "h5", "h6", "a", "img", "ul",
                         "ol", "li", "table", "tr", "td", "th", "pre", "code",
                         "meta", "link", "script", "style", "strong", "em"}
            if tag.lower() not in html_tags:
                results.append(LintResult(
                    "INFO", "xml-tags",
                    f"XML tag <{tag}> - consider bracket delimiters [{tag}] for cross-provider compat",
                    filepath, i
                ))

    return results


def lint_filler(content: str, filepath: str) -> list[LintResult]:
    """Detect conversational filler that wastes tokens."""
    if should_skip_rule(filepath, "filler"):
        return []
    results = []
    patterns = [
        (r'\bCool\?\s*Cool\.', "Conversational filler 'Cool? Cool.'"),
        (r'\bAlright[,!]', "Conversational filler 'Alright'"),
        (r'\bOkay,\s+so\b', "Conversational filler 'Okay, so'"),
        (r'\bLet me explain\b', "Filler phrase 'Let me explain'"),
        (r'\bAs I mentioned\b', "Redundant backreference 'As I mentioned'"),
        (r'\bBTW\b', "Informal abbreviation 'BTW'"),
        (r'\bloooo+ng\b', "Informal elongation"),
    ]

    for i, line in enumerate(content.split("\n"), 1):
        for pattern, message in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                results.append(LintResult("INFO", "filler", message, filepath, i))

    return results


def lint_hardcoded_models(content: str, filepath: str) -> list[LintResult]:
    """Detect hard-coded model identifiers."""
    if should_skip_rule(filepath, "hardcoded-model"):
        return []
    results = []
    model_context = re.compile(
        r"(?i)\b(?:model|default_model|--model)\b"
        r"(?:\s*[:=]\s*|\s+)"
        r"[\"']?([a-z][a-z0-9]*(?:[-.][a-z0-9]+){1,})[\"']?"
    )

    for i, line in enumerate(content.split("\n"), 1):
        # Skip YAML config files and code examples
        if filepath.endswith((".yaml", ".yml")):
            continue
        match = model_context.search(line)
        if match and "-" in match.group(1):
            results.append(LintResult(
                "WARNING", "hardcoded-model",
                f"Hard-coded model ID '{match.group(1)}' - use variable or config",
                filepath, i
            ))

    return results


def lint_json_schema(filepath: str) -> list[LintResult]:
    """Validate JSON files against expected structures."""
    results = []
    try:
        content = Path(filepath).read_text()
        data = json.loads(content)

        # Check skill-rules.json
        if "skill_name" in data and "activation_patterns" in data:
            if "version" not in data:
                results.append(LintResult("ERROR", "schema", "Missing 'version' field", filepath))
            for i, pattern in enumerate(data.get("activation_patterns", [])):
                if "weight" not in pattern:
                    results.append(LintResult("ERROR", "schema", f"Pattern {i} missing 'weight'", filepath))
                if "context" not in pattern:
                    results.append(LintResult("WARNING", "schema", f"Pattern {i} missing 'context'", filepath))
                # Validate regex
                try:
                    re.compile(pattern.get("pattern", ""))
                except re.error as e:
                    results.append(LintResult("ERROR", "schema", f"Pattern {i} invalid regex: {e}", filepath))

    except json.JSONDecodeError as e:
        results.append(LintResult("ERROR", "json-parse", f"Invalid JSON: {e}", filepath))
    except Exception as e:
        results.append(LintResult("ERROR", "read-error", f"Cannot read file: {e}", filepath))

    return results


def lint_provider_names(content: str, filepath: str) -> list[LintResult]:
    """Detect bare AI provider/product names in framework files.

    WabbleSpec is vendor-neutral. Framework files must not name specific
    providers or products — use capability descriptors instead.
    Only applies to files under a .wabblespec/ framework tree or framework
    module files. Skipped for spec-reference/, learnings/, and skill-factory
    internal files.
    """
    if should_skip_rule(filepath, "hardcoded-model"):
        return []
    path = _normalized_path(filepath)
    # Only enforce on framework module files, not on spec docs or references
    skip_paths = (
        "spec-reference/",
        "learnings",
        "references/",
        "scripts/",
        "agents/grader",
        "agents/comparator",
        "agents/analyzer",
        "agents/navigator",
    )
    if any(path.startswith(p) or p in path for p in skip_paths):
        return []
    results = []
    provider_pattern = re.compile(
        r"(?<![`\[*_])\b(Claude|Codex|Gemini|GPT-?[0-9]|OpenAI|Anthropic|Mistral|Llama)\b(?![`\]*_])"
    )
    for i, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        if re.search(r"```", stripped):
            continue
        match = provider_pattern.search(line)
        if match:
            results.append(LintResult(
                "WARNING", "provider-name",
                f"Provider name '{match.group(1)}' in framework file — use capability descriptor instead",
                filepath, i
            ))
    return results


def lint_all_caps_shouting(content: str, filepath: str) -> list[LintResult]:
    """Detect ALWAYS/NEVER/MUST shouting (Pattern 2: theory-of-mind framing).

    The lint flags occurrences but doesn't block - there are legitimate
    uses (in code as constants, in tables, etc.). Each flag is a place
    to look and ask: is this rule grounded with rationale?
    """
    if should_skip_rule(filepath, "all-caps-shouting"):
        return []
    results = []
    # Match standalone all-caps directive words (word boundary on both sides)
    # Skip when adjacent to a colon (label) or inside code spans.
    shouting_pattern = re.compile(r"\b(ALWAYS|NEVER|MUST|DO NOT|DON'T)\b")
    in_code_block = False
    for i, line in enumerate(content.split("\n"), 1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        # Skip lines that are clearly table headers or code-as-prose
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        for m in shouting_pattern.finditer(line):
            word = m.group(1)
            results.append(LintResult(
                "WARNING", "all-caps-shouting",
                f"'{word}' - Pattern 2 (theory-of-mind framing). Consider explaining *why* instead of shouting.",
                filepath, i
            ))
    return results


def lint_scope_creep(content: str, filepath: str) -> list[LintResult]:
    """Detect scope-creep / marketing prose (Pattern 5: token-density).

    Phrases like 'designed to provide comprehensive assistance' carry
    zero invocation-time signal and inflate token cost.
    """
    if should_skip_rule(filepath, "scope-creep"):
        return []
    results = []
    patterns = [
        (r"\bdesigned to provide\b", "scope-creep phrase 'designed to provide'"),
        (r"\bcomprehensive (assistance|support|solution|coverage)\b", "scope-creep phrase 'comprehensive ...'"),
        (r"\bwide range of\b", "scope-creep phrase 'wide range of'"),
        (r"\bvarious aspects of\b", "scope-creep phrase 'various aspects of'"),
        (r"\ba variety of\b", "scope-creep phrase 'a variety of'"),
        (r"\bseamlessly\b", "marketing-style adverb 'seamlessly'"),
        (r"\brobustly\b", "marketing-style adverb 'robustly'"),
        (r"\bleverage(s|d|ing)?\b", "marketing-style verb 'leverage' - use 'use'"),
    ]
    for i, line in enumerate(content.split("\n"), 1):
        for pattern, message in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                results.append(LintResult(
                    "WARNING", "scope-creep",
                    f"{message} - Pattern 5 (token density). Tightens to actual instruction.",
                    filepath, i
                ))
    return results


def lint_abstract_rules(content: str, filepath: str) -> list[LintResult]:
    """Detect abstract rule phrases not anchored to examples (Pattern 1).

    'Use best practices', 'be thorough', etc. without a worked example
    nearby is a signal the rule will generalize poorly at invocation time.
    """
    if should_skip_rule(filepath, "abstract-rules"):
        return []
    results = []
    abstract_phrases = [
        (r"\bbest practices?\b", "abstract phrase 'best practices'"),
        (r"\bas appropriate\b", "abstract phrase 'as appropriate'"),
        (r"\bwhere relevant\b", "abstract phrase 'where relevant'"),
        (r"\bwhere applicable\b", "abstract phrase 'where applicable'"),
        (r"\bbe thorough\b", "abstract phrase 'be thorough'"),
        (r"\bbe careful\b", "abstract phrase 'be careful'"),
        (r"\bhandle (this|it) appropriately\b", "abstract phrase 'handle appropriately'"),
        (r"\buse good judgment\b", "abstract phrase 'use good judgment'"),
    ]
    for i, line in enumerate(content.split("\n"), 1):
        for pattern, message in abstract_phrases:
            if re.search(pattern, line, re.IGNORECASE):
                results.append(LintResult(
                    "INFO", "abstract-rules",
                    f"{message} - Pattern 1 (concrete examples). Anchor with a worked example or name the specific practice.",
                    filepath, i
                ))
    return results


def lint_secret_patterns(content: str, filepath: str) -> list[LintResult]:
    """Detect potential secrets in skill content.

    These patterns flag near-certain secrets. False positives are
    possible; review each. Test fixtures, eval files, and config
    examples are common offenders.
    """
    if should_skip_rule(filepath, "secret-patterns"):
        return []
    results = []
    patterns = [
        (r"\bgh[pso]_[A-Za-z0-9]{16,}\b", "GitHub token pattern"),
        (r"\bxox[bpars]-[A-Za-z0-9-]{10,}\b", "Slack token pattern"),
        (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key pattern"),
        (r"\bsk-[A-Za-z0-9]{20,}\b", "sk-prefixed API key pattern"),
        (r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private key pattern"),
    ]
    for i, line in enumerate(content.split("\n"), 1):
        for pattern, message in patterns:
            if re.search(pattern, line):
                results.append(LintResult(
                    "ERROR", "secret-patterns",
                    f"Likely secret: {message}. Remove before shipping.",
                    filepath, i
                ))
    return results


def lint_phase1_safety(content: str, filepath: str) -> list[LintResult]:
    """Detect missing Phase 1 safety/factuality gates in SKILL.md files."""
    if Path(filepath).name != "SKILL.md":
        return []
    results = []
    for finding in validate_phase1_skill_content(content):
        level = "ERROR" if finding["severity"] == "error" else "WARNING"
        results.append(LintResult(
            level,
            finding["code"],
            f"{finding['message']} Repair: {finding['repair']}",
            filepath,
        ))
    return results


def lint_phase2_template(content: str, filepath: str) -> list[LintResult]:
    """Detect generic or weak generated skill structure."""
    if Path(filepath).name != "SKILL.md":
        return []
    results = []
    for finding in validate_phase2_skill_content(content):
        level = "ERROR" if finding["severity"] == "error" else "WARNING"
        results.append(LintResult(
            level,
            finding["code"],
            f"{finding['message']} Repair: {finding['repair']}",
            filepath,
        ))
    return results


def lint_phase3_quality(content: str, filepath: str) -> list[LintResult]:
    """Detect Phase 3 quality/scoring validator findings."""
    if Path(filepath).name != "SKILL.md":
        return []
    results = []
    for item in validate_phase3_skill_content(content):
        level = "ERROR" if item["severity"] == "error" else "WARNING"
        results.append(LintResult(
            level,
            item["code"],
            f"{item['message']} Repair: {item['repair']}",
            filepath,
        ))
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def lint_directory(directory: Path, verbose: bool = False) -> list[LintResult]:
    """Lint all files in a skill directory."""
    all_results = []

    for filepath in sorted(directory.rglob("*")):
        if filepath.is_dir():
            continue
        if should_skip_path(filepath, directory):
            continue
        if filepath.suffix in (".pyc", ".pyo"):
            continue
        if "__pycache__" in str(filepath):
            continue

        rel_path = str(filepath.relative_to(directory))
        content = ""

        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Run text-based lints on markdown and Python files
        if filepath.suffix in (".md", ".py", ".txt"):
            all_results.extend(lint_vendor_specific(content, rel_path))
            all_results.extend(lint_xml_tags(content, rel_path))
            all_results.extend(lint_filler(content, rel_path))
            all_results.extend(lint_hardcoded_models(content, rel_path))
            all_results.extend(lint_provider_names(content, rel_path))
            all_results.extend(lint_all_caps_shouting(content, rel_path))
            all_results.extend(lint_scope_creep(content, rel_path))
            all_results.extend(lint_abstract_rules(content, rel_path))
            all_results.extend(lint_secret_patterns(content, rel_path))
            all_results.extend(lint_phase1_safety(content, rel_path))
            all_results.extend(lint_phase2_template(content, rel_path))
            all_results.extend(lint_phase3_quality(content, rel_path))

        # Run JSON schema validation
        if filepath.suffix == ".json":
            all_results.extend(lint_json_schema(str(filepath)))
            all_results.extend(lint_hardcoded_models(content, rel_path))
            all_results.extend(lint_secret_patterns(content, rel_path))

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Lint skill files for cross-provider compatibility")
    parser.add_argument("path", type=Path, help="Directory or file to lint")
    parser.add_argument("--level", choices=["ERROR", "WARNING", "INFO"], default="INFO",
                        help="Minimum severity level to report")
    parser.add_argument("--rule", action="append", default=None,
                        help="Only report one rule name; can be passed multiple times")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    level_order = {"ERROR": 3, "WARNING": 2, "INFO": 1}
    min_level = level_order[args.level]

    if args.path.is_dir():
        results = lint_directory(args.path, verbose=args.verbose)
    else:
        content = args.path.read_text(encoding="utf-8")
        rel = args.path.name
        results = (
            lint_vendor_specific(content, rel) +
            lint_xml_tags(content, rel) +
            lint_filler(content, rel) +
            lint_hardcoded_models(content, rel) +
            lint_all_caps_shouting(content, rel) +
            lint_scope_creep(content, rel) +
            lint_abstract_rules(content, rel) +
            lint_secret_patterns(content, rel) +
            lint_phase1_safety(content, rel) +
            lint_phase2_template(content, rel) +
            lint_phase3_quality(content, rel)
        )
        if args.path.suffix == ".json":
            results.extend(lint_json_schema(str(args.path)))

    # Filter by rule and level
    if args.rule:
        wanted = set(args.rule)
        results = [r for r in results if r.rule in wanted]
    results = [r for r in results if level_order.get(r.level, 0) >= min_level]

    if args.json:
        output = [{
            "level": r.level,
            "rule": r.rule,
            "message": r.message,
            "file": r.file,
            "line": r.line,
        } for r in results]
        print(json.dumps(output, indent=2))
    else:
        errors = [r for r in results if r.level == "ERROR"]
        warnings = [r for r in results if r.level == "WARNING"]
        info = [r for r in results if r.level == "INFO"]

        for r in results:
            print(str(r))

        print(f"\n{'='*50}")
        print(f"Total: {len(results)} issues ({len(errors)} errors, {len(warnings)} warnings, {len(info)} info)")

        if errors:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

