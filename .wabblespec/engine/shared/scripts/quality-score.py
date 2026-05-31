"""
WabbleSpec Quality Scorer — Layer 1 static quality score for SKILL.md files.

Produces a continuous quality score (0-100) with dimension breakdown, badge
(Bronze/Silver/Gold/Platinum), and letter grade. Designed for CI integration
via --threshold flag and for identifying lowest-quality skills in the corpus.

This is a standalone Layer 1 static scorer. It does not require wabblespec.yaml
and can be pointed at any skill directory containing a SKILL.md file.

Usage:
  python quality-score.py <skill_dir>
  python quality-score.py <skill_dir> --verbose
  python quality-score.py <skill_dir> --threshold 70
  python quality-score.py <skill_dir> --output json
  python quality-score.py --corpus <plugins_dir> [--top N] [--sort score|name]

Exit codes:
  0 = scored (passes threshold if set)
  1 = scored but below threshold
  2 = input error (skill dir not found, no SKILL.md)

Dimension weights (source: plugin-eval engine.py DIMENSION_WEIGHTS via agents-main ref-adopt 2026-05-31):
  triggering_accuracy (0.25): has "Use when"/trigger phrase + description >= 20 chars
  orchestration_fitness (0.20): has output documentation + code examples
  scope_calibration (0.12): line count in 200-600 sweet spot
  progressive_disclosure (0.10): references/ present if body > 600 lines
  token_efficiency (0.06): MNA count <= 15 (ideally <= 5)
  structural_completeness (0.03): required sections + headings + code blocks
  ecosystem_coherence (0.02): ## See Also / [[cross-ref links]] present
  [excluded] output_quality (0.15): requires LLM judge layer
  [excluded] robustness (0.05): requires Monte Carlo simulation
  [excluded] code_template_quality (0.02): requires LLM judge layer

Anti-pattern penalties (max(0.5, 1.0 - 0.05 * count_triggered)):
  OVER_CONSTRAINED: >15 MUST/NEVER/ALWAYS -> 10% penalty
  MISSING_TRIGGER: no "Use when" phrase in description -> 15% penalty
  BLOATED_SKILL: >800 lines without references/ -> 10% penalty
  ORPHAN_REFERENCE: dead link to references/ file -> 5% penalty
  DEAD_CROSS_REF: [[name]] link not in provided module list -> 5% penalty
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path


# ─── Constants ─────────────────────────────────────────────────────────────────

_MNA_PATTERN = re.compile(r'\b(MUST|NEVER|ALWAYS)\b')
_CROSS_REF_PATTERN = re.compile(r'\[\[([a-z0-9_-]+)\]\]')
_REF_LINK_PATTERN = re.compile(r'\[.*?\]\(references/([^\)#]+)')

DIMENSION_WEIGHTS = {
    "triggering_accuracy": 0.25,
    "orchestration_fitness": 0.20,
    "scope_calibration": 0.12,
    "progressive_disclosure": 0.10,
    "token_efficiency": 0.06,
    "structural_completeness": 0.03,
    "ecosystem_coherence": 0.02,
}

SCORE_BADGES = [(90, "Platinum"), (80, "Gold"), (70, "Silver"), (60, "Bronze")]
SCORE_GRADES = [
    (97, "A+"), (93, "A"), (90, "A-"), (87, "B+"), (83, "B"), (80, "B-"),
    (77, "C+"), (73, "C"), (70, "C-"), (67, "D+"), (63, "D"), (60, "D-"),
]

ANTI_PATTERN_WEIGHTS = {
    "OVER_CONSTRAINED": 0.10,
    "MISSING_TRIGGER": 0.15,
    "BLOATED_SKILL": 0.10,
    "ORPHAN_REFERENCE": 0.05,
    "DEAD_CROSS_REF": 0.05,
}

DIMENSION_DESCRIPTIONS = {
    "triggering_accuracy": "Does the description fire for the right prompts?",
    "orchestration_fitness": "Is it a composable worker with clear output documentation?",
    "scope_calibration": "Is the scope well-sized (200-600 lines sweet spot)?",
    "progressive_disclosure": "Does it use references/ for large content (>600 lines)?",
    "token_efficiency": "Is it concise — low MUST/NEVER/ALWAYS density?",
    "structural_completeness": "Does it have ## What, ## When, code blocks, headings?",
    "ecosystem_coherence": "Does it link to related skills via ## See Also or [[refs]]?",
}


# ─── Parsers ───────────────────────────────────────────────────────────────────

def _score_to_grade(score):
    for threshold, letter in SCORE_GRADES:
        if score >= threshold:
            return letter
    return "F"


def _score_to_badge(score):
    for threshold, name in SCORE_BADGES:
        if score >= threshold:
            return name
    return "No badge"


def _split_frontmatter(content):
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        import yaml
        fm = yaml.safe_load(parts[1]) or {}
    except Exception:
        fm = {}
    body = parts[2]
    return fm, body


# ─── Anti-pattern detection ───────────────────────────────────────────────────

def check_anti_patterns(skill_dir, content, known_module_ids=None):
    """Return dict of flag -> triggered (True = bad)."""
    flags = {}

    fm, body = _split_frontmatter(content)
    desc_text = (fm.get("description") or "").strip()

    # OVER_CONSTRAINED: >15 MUST/NEVER/ALWAYS
    mna_count = len(_MNA_PATTERN.findall(content))
    flags["OVER_CONSTRAINED"] = mna_count > 15

    # MISSING_TRIGGER: no activation phrase in description
    flags["MISSING_TRIGGER"] = not bool(re.search(
        r"(use when|use proactively|trigger|activates? when)", desc_text, re.IGNORECASE
    ))

    # BLOATED_SKILL: >800 lines without references/
    line_count = content.count('\n')
    refs_dir = os.path.join(skill_dir, "references")
    flags["BLOATED_SKILL"] = line_count > 800 and not os.path.isdir(refs_dir)

    # ORPHAN_REFERENCE: dead link to references/ file
    ref_links = _REF_LINK_PATTERN.findall(content)
    if ref_links:
        flags["ORPHAN_REFERENCE"] = any(
            not os.path.isfile(os.path.join(refs_dir, lnk))
            for lnk in ref_links
        )
    else:
        flags["ORPHAN_REFERENCE"] = False

    # DEAD_CROSS_REF: [[name]] to non-existent module
    cross_refs = _CROSS_REF_PATTERN.findall(content)
    if cross_refs and known_module_ids is not None:
        flags["DEAD_CROSS_REF"] = any(ref not in known_module_ids for ref in cross_refs)
    else:
        flags["DEAD_CROSS_REF"] = False

    return flags


# ─── Dimension scoring ────────────────────────────────────────────────────────

def compute_dimensions(skill_dir, content):
    """Compute 0.0-1.0 score for each static-measurable dimension."""
    fm, body = _split_frontmatter(content)
    desc_text = (fm.get("description") or "").strip()

    line_count = content.count('\n')
    refs_dir = os.path.join(skill_dir, "references")
    has_refs = os.path.isdir(refs_dir)
    has_code = bool(re.search(r'^```', content, re.MULTILINE))
    h2_count = len(re.findall(r'^## ', content, re.MULTILINE))

    has_trigger = bool(re.search(
        r"(use when|use proactively|trigger|activates? when)", desc_text, re.IGNORECASE
    ))
    has_desc_len = len(desc_text) >= 20

    has_what = "## What this skill does" in content
    has_when = "## When to use" in content
    output_signals = [
        "## Output contract", "## Outputs", "receipt**", "**receipt",
        "## Output", "## Returns", "writes a receipt",
    ]
    has_output = any(s in content for s in output_signals)

    # triggering_accuracy: trigger phrase (0.7) + description length (0.3)
    ta = (0.7 if has_trigger else 0.0) + (0.3 if has_desc_len else 0.0)

    # orchestration_fitness: output documentation (0.6) + code examples (0.4)
    of = (0.6 if has_output else 0.0) + (0.4 if has_code else 0.0)

    # scope_calibration: sweet spot 200-600 lines
    if 200 <= line_count <= 600:
        sc = 1.0
    elif line_count < 200:
        sc = max(0.0, line_count / 200.0)
    elif line_count <= 800:
        sc = 0.8
    else:
        sc = 0.5

    # progressive_disclosure: refs/ present if body > 600 lines
    pd = 1.0 if (line_count <= 600 or has_refs) else 0.4

    # token_efficiency: MNA density (<=5 excellent, <=15 acceptable, >15 poor)
    mna_count = len(_MNA_PATTERN.findall(content))
    if mna_count <= 5:
        te = 1.0
    elif mna_count <= 15:
        te = max(0.0, 1.0 - (mna_count - 5) / 10.0)
    else:
        te = 0.0

    # structural_completeness: sections + headings + code
    sc_struct = (
        (0.4 if has_what else 0.0) +
        (0.3 if has_when else 0.0) +
        (0.2 if h2_count >= 3 else 0.1 if h2_count >= 1 else 0.0) +
        (0.1 if has_code else 0.0)
    )

    # ecosystem_coherence: ## See Also / Related / [[cross-refs]]
    has_seealso = bool(re.search(r'## (see also|related|reference routing)', content, re.IGNORECASE))
    has_cross = bool(_CROSS_REF_PATTERN.search(content))
    ec = 1.0 if (has_seealso or has_cross) else 0.3

    return {
        "triggering_accuracy": ta,
        "orchestration_fitness": of,
        "scope_calibration": sc,
        "progressive_disclosure": pd,
        "token_efficiency": te,
        "structural_completeness": sc_struct,
        "ecosystem_coherence": ec,
    }


# ─── Score computation ────────────────────────────────────────────────────────

def score_skill(skill_dir, content=None, known_module_ids=None):
    """Compute full quality score for a skill directory.

    Returns a result dict or raises ValueError if SKILL.md not found.
    """
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise ValueError(f"No SKILL.md found in {skill_dir}")

    if content is None:
        with open(skill_md, encoding="utf-8-sig") as f:
            content = f.read()

    fm, body = _split_frontmatter(content)
    name = fm.get("name") or os.path.basename(skill_dir)

    dim_scores = compute_dimensions(skill_dir, content)
    anti_flags = check_anti_patterns(skill_dir, content, known_module_ids)

    # Renormalized composite
    total_weight = sum(DIMENSION_WEIGHTS[d] for d in dim_scores)
    raw = sum(DIMENSION_WEIGHTS[d] / total_weight * s for d, s in dim_scores.items())

    # Anti-pattern penalty: max(0.5, 1.0 - 0.05 * count_triggered)
    triggered = [f for f, v in anti_flags.items() if v]
    penalty = max(0.5, 1.0 - 0.05 * len(triggered))

    final = min(100.0, max(0.0, raw * 100.0 * penalty))
    badge = _score_to_badge(final)
    grade = _score_to_grade(final)

    line_count = content.count('\n')
    mna_count = len(_MNA_PATTERN.findall(content))

    return {
        "name": name,
        "path": str(skill_dir),
        "score": round(final, 1),
        "badge": badge,
        "grade": grade,
        "raw_score": round(raw * 100.0, 1),
        "penalty": round(penalty, 2),
        "triggered_anti_patterns": triggered,
        "dimensions": {d: round(s, 3) for d, s in dim_scores.items()},
        "meta": {
            "line_count": line_count,
            "mna_count": mna_count,
            "has_references_dir": os.path.isdir(os.path.join(skill_dir, "references")),
        },
    }


# ─── Output formatters ────────────────────────────────────────────────────────

def format_markdown(result):
    lines = [
        f"# Quality Score Report",
        f"",
        f"**Skill:** `{result['name']}`",
        f"**Path:** `{result['path']}`",
        f"",
        f"## Overall Score",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Score | **{result['score']}/100** |",
        f"| Badge | {result['badge']} |",
        f"| Grade | {result['grade']} |",
        f"| Confidence | Estimated (static only) |",
        f"",
        f"## Dimension Scores",
        f"",
        f"| Dimension | Weight | Score | Description |",
        f"|-----------|--------|-------|-------------|",
    ]
    for dim, weight in DIMENSION_WEIGHTS.items():
        score = result["dimensions"].get(dim, 0.0)
        grade = _score_to_grade(score * 100.0)
        desc = DIMENSION_DESCRIPTIONS.get(dim, "")
        lines.append(f"| {dim} | {int(weight*100)}% | {score:.3f} ({grade}) | {desc} |")

    lines += [
        f"",
        f"## Anti-Pattern Analysis",
        f"",
    ]
    if result["triggered_anti_patterns"]:
        lines.append(f"Penalty: {result['penalty']} ({len(result['triggered_anti_patterns'])} flags triggered)\n")
        for flag in result["triggered_anti_patterns"]:
            pct = int(ANTI_PATTERN_WEIGHTS.get(flag, 0.05) * 100)
            lines.append(f"- **{flag}** (-{pct}%)")
    else:
        lines.append("No anti-patterns detected.")

    lines += [
        f"",
        f"## Metadata",
        f"",
        f"| Field | Value |",
        f"|-------|-------|",
        f"| Line count | {result['meta']['line_count']} |",
        f"| MNA count | {result['meta']['mna_count']} |",
        f"| Has references/ dir | {result['meta']['has_references_dir']} |",
        f"| Raw score (pre-penalty) | {result['raw_score']}/100 |",
    ]
    return "\n".join(lines)


def format_corpus_table(results):
    """Format a ranked corpus table for --corpus mode."""
    sorted_results = sorted(results, key=lambda r: r["score"], reverse=True)
    lines = [
        "# Quality Score Corpus Report",
        "",
        f"**Skills scored:** {len(results)}",
        f"**Average score:** {sum(r['score'] for r in results) / len(results):.1f}",
        f"**Badge distribution:** "
        + ", ".join(
            f"{name}: {sum(1 for r in results if r['badge'] == name)}"
            for _, name in SCORE_BADGES
        )
        + f", No badge: {sum(1 for r in results if r['badge'] == 'No badge')}",
        "",
        "| Rank | Skill | Score | Badge | Grade | Anti-patterns |",
        "|------|-------|-------|-------|-------|---------------|",
    ]
    for i, r in enumerate(sorted_results, 1):
        ap = ", ".join(r["triggered_anti_patterns"]) or "—"
        lines.append(f"| {i} | {r['name']} | {r['score']} | {r['badge']} | {r['grade']} | {ap} |")
    return "\n".join(lines)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WabbleSpec static quality scorer for SKILL.md files"
    )
    parser.add_argument("skill_dir", nargs="?",
                        help="Path to skill directory containing SKILL.md")
    parser.add_argument("--corpus", metavar="DIR",
                        help="Score all SKILL.md files under DIR (corpus mode)")
    parser.add_argument("--top", type=int, default=0,
                        help="In corpus mode: show only top N results")
    parser.add_argument("--sort", choices=["score", "name"], default="score",
                        help="Corpus sort order (default: score)")
    parser.add_argument("--output", choices=["markdown", "json"], default="markdown",
                        help="Output format (default: markdown)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show full dimension details")
    parser.add_argument("--threshold", type=float, default=0,
                        help="Exit 1 if score below this threshold (CI gate)")
    args = parser.parse_args()

    if args.corpus:
        # Corpus mode: score all SKILL.md files found under directory
        corpus_dir = Path(args.corpus)
        if not corpus_dir.is_dir():
            print(f"ERROR: corpus directory not found: {args.corpus}", file=sys.stderr)
            sys.exit(2)

        skill_dirs = sorted(
            p.parent for p in corpus_dir.rglob("SKILL.md")
        )
        if not skill_dirs:
            print(f"ERROR: no SKILL.md files found under {args.corpus}", file=sys.stderr)
            sys.exit(2)

        results = []
        for sd in skill_dirs:
            try:
                results.append(score_skill(str(sd)))
            except Exception as e:
                print(f"  WARN: skipped {sd}: {e}", file=sys.stderr)

        if not results:
            print("ERROR: no skills could be scored", file=sys.stderr)
            sys.exit(2)

        if args.sort == "name":
            results.sort(key=lambda r: r["name"])
        else:
            results.sort(key=lambda r: r["score"], reverse=True)

        if args.top > 0:
            results = results[:args.top]

        if args.output == "json":
            print(json.dumps(results, indent=2))
        else:
            print(format_corpus_table(results))
        sys.exit(0)

    # Single skill mode
    if not args.skill_dir:
        parser.print_help()
        sys.exit(2)

    skill_dir = args.skill_dir
    if not os.path.isdir(skill_dir):
        print(f"ERROR: skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(2)

    try:
        result = score_skill(skill_dir)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_markdown(result))
        if args.verbose:
            print("\n## Verbose Dimension Detail")
            for dim, score in result["dimensions"].items():
                grade = _score_to_grade(score * 100.0)
                print(f"  {dim}: {score:.3f} ({grade})")

    if args.threshold > 0 and result["score"] < args.threshold:
        print(f"\nFAIL: score {result['score']} is below threshold {args.threshold}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
