"""
WabbleSpec Quality Ranker — Elo-based relative ranking across skill corpus.

Uses quality-score.py static scores as initial Elo seeds, then allows pairwise
head-to-head comparisons to update ratings. Identifies lowest-quality skills
for L8 improvement targeting.

Usage:
  python quality-rank.py init <corpus_dir> [--ratings-file PATH]
      Build initial Elo corpus from all SKILL.md files under corpus_dir.
      Each skill gets an initial rating of 1500. Scores are computed via
      quality-score.py logic and used to seed initial pairings.

  python quality-rank.py rank [--ratings-file PATH] [--top N] [--bottom N]
      Show current Elo rankings.

  python quality-rank.py compare <skill_a_dir> <skill_b_dir> [--ratings-file PATH]
      Run head-to-head: quality score determines the winner, Elo ratings update.

  python quality-rank.py report [--ratings-file PATH] [--output markdown|json]
      Full ranked report with scores, Elo ratings, and improvement recommendations.

Elo parameters (source: plugin-eval elo.py via agents-main ref-adopt 2026-05-31):
  Initial rating: 1500
  K-factor: 32
  E(A) = 1 / (1 + 10^((Rb - Ra) / 400))
  Bootstrap CI: 500 resamples (sampling with replacement from match history)

Exit codes:
  0 = success
  1 = comparison: skill_a has lower rating than skill_b after update
  2 = input error
"""

import sys
import os
import re
import json
import math
import argparse
import random
from pathlib import Path
from datetime import datetime, timezone


# ─── Constants ─────────────────────────────────────────────────────────────────

ELO_INITIAL = 1500.0
ELO_K = 32.0
BOOTSTRAP_RESAMPLES = 500

DEFAULT_RATINGS_FILE = ".wabblespec/state/memory/quality-rankings.json"


# ─── Elo math ─────────────────────────────────────────────────────────────────

def expected(ra, rb):
    """Expected score for A against B. E(A) = 1 / (1 + 10^((Rb-Ra)/400))"""
    return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))


def update_elo(ra, rb, score_a):
    """Update Elo ratings. score_a: 1.0=A wins, 0.5=draw, 0.0=B wins."""
    ea = expected(ra, rb)
    new_ra = ra + ELO_K * (score_a - ea)
    new_rb = rb + ELO_K * ((1.0 - score_a) - (1.0 - ea))
    return new_ra, new_rb


def bootstrap_ci(ratings_history, n_resamples=BOOTSTRAP_RESAMPLES, confidence=0.95):
    """Compute bootstrap confidence interval for a list of rating values."""
    if len(ratings_history) < 2:
        return None, None
    means = []
    for _ in range(n_resamples):
        sample = [random.choice(ratings_history) for _ in ratings_history]
        means.append(sum(sample) / len(sample))
    means.sort()
    lo_idx = int((1.0 - confidence) / 2.0 * n_resamples)
    hi_idx = int((1.0 + confidence) / 2.0 * n_resamples) - 1
    return round(means[lo_idx], 1), round(means[hi_idx], 1)


# ─── Scoring bridge (mirrors quality-score.py logic) ─────────────────────────

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


def _quick_score(skill_dir):
    """Compute quality score for a skill directory. Returns 0-100 float."""
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None
    try:
        with open(skill_md, encoding="utf-8-sig") as f:
            content = f.read()
    except OSError:
        return None

    # Import the full scorer from quality-score.py if available
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _qs_path = os.path.join(_this_dir, "quality-score.py")
    if os.path.isfile(_qs_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("quality_score", _qs_path)
        qs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(qs)
        try:
            result = qs.score_skill(skill_dir, content)
            return result["score"]
        except Exception:
            pass

    # Fallback: minimal inline score
    parts = content.split("---", 2)
    fm_text = parts[1] if len(parts) >= 3 else ""
    desc_match = re.search(r"^description:\s*(.+)$", fm_text, re.MULTILINE)
    desc = desc_match.group(1).strip() if desc_match else ""
    has_trigger = bool(re.search(r"use when|use proactively", desc, re.IGNORECASE))
    has_code = bool(re.search(r'^```', content, re.MULTILINE))
    line_count = content.count('\n')
    mna_count = len(_MNA_PATTERN.findall(content))
    score_raw = (
        (50.0 if has_trigger else 0.0) +
        (20.0 if has_code else 0.0) +
        (20.0 if 200 <= line_count <= 600 else 10.0) +
        (10.0 if mna_count <= 15 else 0.0)
    )
    if mna_count > 15:
        score_raw *= 0.9
    return round(min(100.0, score_raw), 1)


# ─── Ratings store ─────────────────────────────────────────────────────────────

def _load_ratings(ratings_file):
    if os.path.isfile(ratings_file):
        with open(ratings_file, encoding="utf-8") as f:
            return json.load(f)
    return {"skills": {}, "matches": [], "created_at": datetime.now(timezone.utc).isoformat()}


def _save_ratings(ratings, ratings_file):
    os.makedirs(os.path.dirname(os.path.abspath(ratings_file)), exist_ok=True)
    with open(ratings_file, "w", encoding="utf-8") as f:
        json.dump(ratings, f, indent=2)


def _skill_key(skill_dir):
    return os.path.basename(os.path.normpath(skill_dir))


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_init(corpus_dir, ratings_file, verbose=False):
    """Build initial Elo corpus from quality scores."""
    corpus_path = Path(corpus_dir)
    if not corpus_path.is_dir():
        print(f"ERROR: corpus directory not found: {corpus_dir}", file=sys.stderr)
        return 2

    skill_dirs = sorted(p.parent for p in corpus_path.rglob("SKILL.md"))
    if not skill_dirs:
        print(f"ERROR: no SKILL.md files found under {corpus_dir}", file=sys.stderr)
        return 2

    ratings = _load_ratings(ratings_file)

    scored = []
    for sd in skill_dirs:
        key = _skill_key(str(sd))
        score = _quick_score(str(sd))
        if score is None:
            if verbose:
                print(f"  SKIP: {key} (could not score)")
            continue
        scored.append((key, str(sd), score))
        if verbose:
            print(f"  {key}: {score}/100")

    if not scored:
        print("ERROR: no skills could be scored", file=sys.stderr)
        return 2

    # Seed Elo ratings: use score rank to adjust initial rating
    # Top skill gets 1500 + 200, bottom gets 1500 - 200, scaled linearly
    scored.sort(key=lambda x: x[2], reverse=True)
    n = len(scored)
    for i, (key, path, score) in enumerate(scored):
        if key not in ratings["skills"]:
            # Map rank 0..n-1 to rating range 1700..1300
            seeded_rating = ELO_INITIAL + 200.0 - (400.0 * i / max(1, n - 1))
            ratings["skills"][key] = {
                "path": path,
                "elo": round(seeded_rating, 1),
                "quality_score": score,
                "match_count": 0,
                "rating_history": [round(seeded_rating, 1)],
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
        else:
            # Update quality score without resetting Elo
            ratings["skills"][key]["quality_score"] = score
            ratings["skills"][key]["path"] = path

    ratings["corpus_dir"] = str(corpus_dir)
    ratings["skill_count"] = len(scored)
    ratings["last_updated"] = datetime.now(timezone.utc).isoformat()

    _save_ratings(ratings, ratings_file)
    print(f"Initialized corpus: {len(scored)} skills rated")
    print(f"Ratings stored at:  {ratings_file}")
    return 0


def cmd_rank(ratings_file, top=0, bottom=0, output="table"):
    """Display current Elo rankings."""
    ratings = _load_ratings(ratings_file)
    skills = ratings.get("skills", {})
    if not skills:
        print("No skills rated yet. Run: python quality-rank.py init <corpus_dir>")
        return 0

    ranked = sorted(skills.items(), key=lambda x: x[1]["elo"], reverse=True)

    if top > 0:
        ranked = ranked[:top]
    elif bottom > 0:
        ranked = ranked[-bottom:][::-1]

    print(f"{'Rank':<5} {'Skill':<35} {'Elo':>6} {'Score':>6} {'Matches':>8}")
    print("-" * 65)
    for i, (key, data) in enumerate(ranked, 1):
        elo = data["elo"]
        score = data.get("quality_score", "?")
        matches = data.get("match_count", 0)
        print(f"{i:<5} {key:<35} {elo:>6.0f} {str(score)+'/100':>9} {matches:>7}")
    return 0


def cmd_compare(skill_a_dir, skill_b_dir, ratings_file):
    """Head-to-head comparison. Quality score determines winner; Elo updates."""
    ratings = _load_ratings(ratings_file)
    key_a = _skill_key(skill_a_dir)
    key_b = _skill_key(skill_b_dir)

    score_a = _quick_score(skill_a_dir)
    score_b = _quick_score(skill_b_dir)

    if score_a is None or score_b is None:
        print("ERROR: could not score one or both skills", file=sys.stderr)
        return 2

    # Determine winner from quality scores
    if score_a > score_b:
        outcome_a = 1.0  # A wins
    elif score_b > score_a:
        outcome_a = 0.0  # B wins
    else:
        outcome_a = 0.5  # Draw

    # Get or initialize Elo ratings
    def _get_or_init(key, path, score):
        if key not in ratings["skills"]:
            ratings["skills"][key] = {
                "path": path,
                "elo": ELO_INITIAL,
                "quality_score": score,
                "match_count": 0,
                "rating_history": [ELO_INITIAL],
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
        return ratings["skills"][key]["elo"]

    ra = _get_or_init(key_a, skill_a_dir, score_a)
    rb = _get_or_init(key_b, skill_b_dir, score_b)

    new_ra, new_rb = update_elo(ra, rb, outcome_a)

    for key, old_r, new_r, score in [(key_a, ra, new_ra, score_a), (key_b, rb, new_rb, score_b)]:
        ratings["skills"][key]["elo"] = round(new_r, 1)
        ratings["skills"][key]["quality_score"] = score
        ratings["skills"][key]["match_count"] = ratings["skills"][key].get("match_count", 0) + 1
        ratings["skills"][key].setdefault("rating_history", [old_r]).append(round(new_r, 1))
        ratings["skills"][key]["last_updated"] = datetime.now(timezone.utc).isoformat()

    ratings["matches"].append({
        "skill_a": key_a, "skill_b": key_b,
        "score_a": score_a, "score_b": score_b,
        "outcome_a": outcome_a,
        "elo_a_before": round(ra, 1), "elo_b_before": round(rb, 1),
        "elo_a_after": round(new_ra, 1), "elo_b_after": round(new_rb, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    ratings["last_updated"] = datetime.now(timezone.utc).isoformat()

    _save_ratings(ratings, ratings_file)

    winner = key_a if outcome_a == 1.0 else (key_b if outcome_a == 0.0 else "Draw")
    print(f"{key_a} ({score_a}/100) vs {key_b} ({score_b}/100)")
    print(f"Winner: {winner}")
    print(f"  {key_a}: {ra:.0f} -> {new_ra:.0f} ({new_ra - ra:+.0f})")
    print(f"  {key_b}: {rb:.0f} -> {new_rb:.0f} ({new_rb - rb:+.0f})")

    return 0 if new_ra >= new_rb else 1


def cmd_report(ratings_file, output="markdown"):
    """Full ranked report."""
    ratings = _load_ratings(ratings_file)
    skills = ratings.get("skills", {})
    if not skills:
        print("No skills rated yet.")
        return 0

    ranked = sorted(skills.items(), key=lambda x: x[1]["elo"], reverse=True)
    total = len(ranked)
    avg_elo = sum(d["elo"] for _, d in ranked) / total
    avg_score = sum(d.get("quality_score", 0) for _, d in ranked) / total

    if output == "json":
        out = {
            "total_skills": total,
            "avg_elo": round(avg_elo, 1),
            "avg_quality_score": round(avg_score, 1),
            "match_count": len(ratings.get("matches", [])),
            "ranked": [
                {
                    "rank": i + 1,
                    "name": key,
                    "elo": d["elo"],
                    "quality_score": d.get("quality_score"),
                    "match_count": d.get("match_count", 0),
                }
                for i, (key, d) in enumerate(ranked)
            ],
        }
        print(json.dumps(out, indent=2))
        return 0

    # Markdown
    print("# Quality Rank Report")
    print()
    print(f"**Skills:** {total} | **Avg Elo:** {avg_elo:.0f} | **Avg Score:** {avg_score:.1f}/100 | **Matches:** {len(ratings.get('matches', []))}")
    print()

    # Top 10
    print("## Top 10")
    print()
    print("| Rank | Skill | Elo | Score | Matches |")
    print("|------|-------|-----|-------|---------|")
    for i, (key, d) in enumerate(ranked[:10], 1):
        ci_lo, ci_hi = bootstrap_ci(d.get("rating_history", [d["elo"]]))
        ci_str = f" [{ci_lo}–{ci_hi}]" if ci_lo else ""
        print(f"| {i} | {key} | {d['elo']:.0f}{ci_str} | {d.get('quality_score', '?')}/100 | {d.get('match_count', 0)} |")

    # Bottom 10 (improvement targets)
    print()
    print("## Bottom 10 (Improvement Targets)")
    print()
    print("| Rank | Skill | Elo | Score | Anti-patterns |")
    print("|------|-------|-----|-------|---------------|")
    for i, (key, d) in enumerate(ranked[-10:][::-1], 1):
        rank = total - i + 1
        ap_note = "—"
        print(f"| {rank} | {key} | {d['elo']:.0f} | {d.get('quality_score', '?')}/100 | {ap_note} |")

    return 0


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="WabbleSpec Elo-based skill quality ranking"
    )
    parser.add_argument("command", choices=["init", "rank", "compare", "report"],
                        help="Command to run")
    parser.add_argument("args", nargs="*",
                        help="Positional arguments for the command")
    parser.add_argument("--ratings-file", default=DEFAULT_RATINGS_FILE,
                        help=f"Path to ratings JSON store (default: {DEFAULT_RATINGS_FILE})")
    parser.add_argument("--top", type=int, default=0,
                        help="Show top N skills (rank command)")
    parser.add_argument("--bottom", type=int, default=0,
                        help="Show bottom N skills (rank command)")
    parser.add_argument("--output", choices=["markdown", "json", "table"], default="table",
                        help="Output format")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.command == "init":
        if not args.args:
            print("ERROR: init requires <corpus_dir>", file=sys.stderr)
            sys.exit(2)
        sys.exit(cmd_init(args.args[0], args.ratings_file, args.verbose))

    elif args.command == "rank":
        sys.exit(cmd_rank(args.ratings_file, args.top, args.bottom, args.output))

    elif args.command == "compare":
        if len(args.args) < 2:
            print("ERROR: compare requires <skill_a_dir> <skill_b_dir>", file=sys.stderr)
            sys.exit(2)
        sys.exit(cmd_compare(args.args[0], args.args[1], args.ratings_file))

    elif args.command == "report":
        sys.exit(cmd_report(args.ratings_file, args.output))


if __name__ == "__main__":
    main()
