#!/usr/bin/env python3
"""
Instinct — WabbleSpec L8 passive receipt observer.
Reads receipts, entity graph, and dream gap-map to detect recurring patterns.
Read-only except for instinct-observations.md.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

GATE_RECEIPT_MIN = 100
RECEIPTS_DIR = Path(".wabblespec/receipts")
ENTITY_GRAPH_PATH = Path(".wabblespec/memory/entity-graph.json")
GAP_MAP_PATH = Path(".wabblespec/memory/gap-map.md")
OBSERVATIONS_PATH = Path(".wabblespec/memory/instinct-observations.md")
EXECUTOR_PID_PATH = Path(".wabblespec/memory/.executor.pid")

# Minimum distinct receipts/waves backing a pattern before it is eligible
# for emission. Per-detector thresholds may be stricter; none may be lower.
# Sourced from sourcebook confidence floor: surface only findings with >= 3
# data points to suppress single-receipt anomalies.
MIN_EVIDENCE_COUNT = 3

FAILURE_RATE_THRESHOLD = 0.20
FAILURE_MIN_RECEIPTS = 5         # > MIN_EVIDENCE_COUNT; stricter by design for failure patterns
CO_OCCURRENCE_MIN = 3            # = MIN_EVIDENCE_COUNT
GAP_TOPIC_MIN_SESSIONS = 3       # = MIN_EVIDENCE_COUNT

# Positive-pattern thresholds
MODULE_FREQUENCY_MIN = 10        # > MIN_EVIDENCE_COUNT; receipts for "high activation" pattern
COMPLEXITY_SKEW_THRESHOLD = 0.70 # fraction of sessions at one level → skew
PHASE_EXPECTED = {"recipe", "specify", "decompose", "executor", "verifier"}  # phases that should appear


def count_receipts():
    if not RECEIPTS_DIR.exists():
        return 0
    return len(list(RECEIPTS_DIR.glob("*.json")))


def load_receipts():
    receipts = []
    if not RECEIPTS_DIR.exists():
        return receipts
    for path in RECEIPTS_DIR.glob("*.json"):
        try:
            with open(path) as f:
                data = json.load(f)
                data["_path"] = str(path)
                receipts.append(data)
        except (json.JSONDecodeError, OSError):
            pass
    return receipts


def load_entity_graph():
    if not ENTITY_GRAPH_PATH.exists():
        return None
    try:
        with open(ENTITY_GRAPH_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def parse_gap_map():
    """Extract recurring topics from Dream's gap-map.md."""
    if not GAP_MAP_PATH.exists():
        return []
    topics = []
    with open(GAP_MAP_PATH) as f:
        content = f.read()
    # Count session mentions per section heading
    for block in content.split("###")[1:]:
        lines = block.strip().split("\n")
        if not lines:
            continue
        topic = lines[0].strip()
        session_count = content.lower().count(topic.lower().split(":")[0].lower())
        if session_count >= GAP_TOPIC_MIN_SESSIONS:
            topics.append({"topic": topic, "sessions": session_count})
    return topics


def detect_high_frequency_failures(receipts):
    module_total = defaultdict(int)
    module_failures = defaultdict(set)
    for r in receipts:
        module = r.get("module", "unknown")
        module_total[module] += 1
        verdict = r.get("status", "")
        if verdict in ("FAIL", "PARTIAL"):
            module_failures[module].add(r["_path"])
    patterns = []
    for module, total in module_total.items():
        failures = module_failures[module]
        if total == 0:
            continue
        rate = len(failures) / total
        if rate >= FAILURE_RATE_THRESHOLD and len(failures) >= FAILURE_MIN_RECEIPTS:
            patterns.append({
                "type": "high-frequency-failure",
                "name": f"High-frequency failure: {module}",
                "module": module,
                "failure_rate": round(rate, 3),
                "distinct_receipts": len(failures),
                "total_receipts": total,
                "evidence": sorted(failures)[:5],
                "confidence": "high" if len(failures) >= 10 else "medium",
                "description": (
                    f"Module `{module}` produced FAIL/PARTIAL in {rate:.0%} of its "
                    f"{total} receipts ({len(failures)} distinct receipts). "
                    f"Threshold: 20% across 5+ receipts. Indicates systematic weakness."
                ),
            })
    return patterns


def detect_co_occurrence_clusters(receipts):
    wave_failures = defaultdict(set)
    for r in receipts:
        wave = r.get("wave", 0)
        module = r.get("module", "unknown")
        if r.get("status") in ("FAIL", "PARTIAL"):
            wave_failures[wave].add(module)
    pair_count = defaultdict(int)
    for modules in wave_failures.values():
        modules = sorted(modules)
        for i in range(len(modules)):
            for j in range(i + 1, len(modules)):
                pair_count[(modules[i], modules[j])] += 1
    patterns = []
    for (m1, m2), count in pair_count.items():
        if count >= CO_OCCURRENCE_MIN:
            patterns.append({
                "type": "co-occurrence-cluster",
                "name": f"Co-occurrence cluster: {m1} + {m2}",
                "modules": [m1, m2],
                "co_occurrence_count": count,
                "confidence": "high" if count >= 6 else "medium",
                "evidence": f"{m1} and {m2} co-failed in {count} distinct execution waves",
                "description": (
                    f"Modules `{m1}` and `{m2}` fail in the same execution wave "
                    f"{count} times — above chance for their individual failure rates. "
                    f"Indicates unanticipated coupling between these modules."
                ),
            })
    return patterns


def detect_high_frequency_modules(receipts):
    """Report modules activated in MODULE_FREQUENCY_MIN or more receipts.

    A corpus of all-pass receipts still reveals which modules are the core
    workhorses and which are rarely exercised. High-frequency modules are
    candidates for deeper optimisation; low-frequency modules may be
    under-tested or incorrectly scoped.
    """
    module_total = defaultdict(int)
    for r in receipts:
        raw = r.get("module") or r.get("receipt_type") or "unknown"
        # Normalise: strip -receipt suffix (archive.py emits "delivery-receipt",
        # receipt-writer.py emits "delivery"; treat as the same module).
        module = raw.removesuffix("-receipt") if raw != "unknown" else raw
        if module != "unknown":
            module_total[module] += 1

    patterns = []
    total_receipts = len(receipts)
    if total_receipts == 0:
        return patterns

    for module, count in sorted(module_total.items(), key=lambda x: -x[1]):
        if count >= MODULE_FREQUENCY_MIN:
            pct = count / total_receipts
            patterns.append({
                "type": "high-frequency-activation",
                "name": f"High-frequency module: {module}",
                "module": module,
                "activation_count": count,
                "activation_pct": round(pct, 3),
                "confidence": "high" if count >= 20 else "medium",
                "evidence": f"{count} receipts in corpus of {total_receipts}",
                "description": (
                    f"Module `{module}` appears in {count} receipts ({pct:.0%} of corpus). "
                    f"High-activation modules are core execution workhorses. "
                    f"Review for optimisation opportunities (token economy, parallelism)."
                ),
            })
    return patterns


def detect_complexity_skew(receipts):
    """Flag if ≥COMPLEXITY_SKEW_THRESHOLD of sessions share one complexity level.

    A heavily skewed complexity distribution means the framework is being used
    almost exclusively at one tier. If Low dominates, Medium/High paths are
    under-exercised and may contain latent defects.
    """
    complexity_counts = defaultdict(int)
    for r in receipts:
        c = r.get("complexity")
        if c in ("Low", "Medium", "High"):
            complexity_counts[c] += 1

    total = sum(complexity_counts.values())
    if total < 5:
        return []

    patterns = []
    for level, count in complexity_counts.items():
        frac = count / total
        if frac >= COMPLEXITY_SKEW_THRESHOLD:
            others = [f"{k}={v}" for k, v in complexity_counts.items() if k != level]
            patterns.append({
                "type": "complexity-skew",
                "name": f"Complexity skew: {level} dominates",
                "dominant_level": level,
                "dominant_count": count,
                "dominant_pct": round(frac, 3),
                "other_counts": others,
                "confidence": "medium",
                "evidence": f"{count}/{total} complexity-tagged receipts are {level}",
                "description": (
                    f"{frac:.0%} of complexity-tagged sessions run at {level} complexity. "
                    f"Other levels: {', '.join(others) if others else 'none observed'}. "
                    f"Under-exercised tiers may have latent defects in branching logic."
                ),
            })
    return patterns


def detect_phase_gaps(receipts):
    """Flag expected pipeline phases with zero receipts in the corpus.

    If a standard phase (recipe, specify, decompose, executor, verifier) never
    appears in the corpus, either those phases are always collapsed or the
    receipt-writing convention is inconsistent.
    """
    observed_phases = set()
    for r in receipts:
        phase = r.get("module") or r.get("receipt_type") or ""
        observed_phases.add(phase.lower())

    patterns = []
    for phase in sorted(PHASE_EXPECTED):
        if phase not in observed_phases:
            patterns.append({
                "type": "phase-gap",
                "name": f"Phase gap: {phase} never observed",
                "phase": phase,
                "confidence": "medium",
                "evidence": f"0 receipts with module={phase!r} across {len(receipts)} total receipts",
                "description": (
                    f"No receipt with module='{phase}' found in the corpus. "
                    f"Either this phase is always collapsed (check collapse_eligible gates) "
                    f"or receipts are not being written consistently."
                ),
            })
    return patterns


def detect_recurring_gaps(gap_topics):
    patterns = []
    for topic in gap_topics:
        patterns.append({
            "type": "recurring-gap",
            "name": f"Recurring gap: {topic['topic']}",
            "topic": topic["topic"],
            "session_count": topic["sessions"],
            "confidence": "medium",
            "evidence": f"Appeared in Dream gap-map across {topic['sessions']} sessions",
            "description": (
                f"Topic '{topic['topic']}' recurs in Dream's gap-map across "
                f"{topic['sessions']} distinct sessions with confidence remaining low. "
                f"Current modules consistently fail to populate this knowledge area."
            ),
        })
    return patterns


def format_observations(patterns, receipt_count, receipts):
    timestamps = sorted(r.get("timestamp", "") for r in receipts if r.get("timestamp"))
    first_date = timestamps[0] if timestamps else "N/A"
    last_date = timestamps[-1] if timestamps else "N/A"

    lines = [
        "# Instinct Observations",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Receipt corpus size: {receipt_count}",
        f"Observation window: {first_date} — {last_date}",
        "",
        "## Observed Patterns",
        "",
    ]

    if not patterns:
        lines.append("No patterns detected above threshold.")
        return "\n".join(lines)

    for i, p in enumerate(patterns, 1):
        ptype = p["type"]
        evidence = p.get("evidence", "")
        if isinstance(evidence, list):
            evidence = ", ".join(evidence)
        if ptype == "high-frequency-failure":
            occurrences = f"{p['distinct_receipts']} across {p['total_receipts']} receipts"
        elif ptype == "high-frequency-activation":
            occurrences = f"{p['activation_count']} receipts ({p['activation_pct']:.0%})"
        elif ptype == "complexity-skew":
            occurrences = f"{p['dominant_count']} of {p['dominant_count'] + sum(int(s.split('=')[1]) for s in p['other_counts'])} tagged receipts"
        else:
            occurrences = f"{p.get('co_occurrence_count', p.get('session_count', 'N/A'))} occurrences"
        lines += [
            f"### Pattern {i}: {p['name']}",
            "",
            f"Type: {ptype}",
            f"Confidence: {p['confidence']}",
            f"Evidence: {evidence}",
            f"Occurrences: {occurrences}",
            "Human-validated: false",
            "",
            p["description"],
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def check_gate(receipt_count, entity_graph):
    issues = []
    if receipt_count < GATE_RECEIPT_MIN:
        issues.append(f"Receipt count {receipt_count} < {GATE_RECEIPT_MIN} required")
    if entity_graph is None:
        issues.append(f"entity-graph.json not found at {ENTITY_GRAPH_PATH}")
    if EXECUTOR_PID_PATH.exists():
        issues.append("Executor PID lock active — do not run Instinct during active execution")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Instinct — WabbleSpec L8 pattern observer")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--activate", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--status", action="store_true")
    args = parser.parse_args()

    receipt_count = count_receipts()
    entity_graph = load_entity_graph()

    if args.status:
        print(f"Receipt count: {receipt_count}/{GATE_RECEIPT_MIN} required")
        print(f"Entity graph: {'found' if entity_graph is not None else 'NOT FOUND'}")
        issues = check_gate(receipt_count, entity_graph)
        if issues:
            print("Gate: NOT MET")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("Gate: MET — ready for --activate")
        sys.exit(0)

    gate_issues = check_gate(receipt_count, entity_graph)
    if gate_issues:
        print("GATE_NOT_MET")
        for issue in gate_issues:
            print(f"  {issue}")
        sys.exit(1)

    receipts = load_receipts()
    gap_topics = parse_gap_map()

    all_patterns = (
        detect_high_frequency_failures(receipts)
        + detect_co_occurrence_clusters(receipts)
        + detect_recurring_gaps(gap_topics)
        + detect_high_frequency_modules(receipts)
        + detect_complexity_skew(receipts)
        + detect_phase_gaps(receipts)
    )

    if args.dry_run:
        print(f"Dry run — {len(all_patterns)} pattern(s) detected (not written)")
        for p in all_patterns:
            print(f"  [{p['type']}] {p['name']} confidence={p['confidence']}")
        sys.exit(0)

    content = format_observations(all_patterns, receipt_count, receipts)
    OBSERVATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OBSERVATIONS_PATH, "w") as f:
        f.write(content)

    print(f"Written: {OBSERVATIONS_PATH}")
    print(f"Patterns detected: {len(all_patterns)}")
    print("Human validation required before any pattern can be submitted to Synth.")


if __name__ == "__main__":
    main()
