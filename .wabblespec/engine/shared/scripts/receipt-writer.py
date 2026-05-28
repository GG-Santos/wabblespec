"""
receipt-writer.py — Schema-enforced receipt serializer.

Claude provides the reasoning-dependent content (check descriptions, summaries,
what was not tested). This script handles structure, required fields, and JSON
serialization — eliminating the per-receipt "which fields does this type need?"
reasoning overhead (~300-1000 tokens per receipt).

Supported receipt types:
    verifier    Verifier gate output
    executor    Executor wave output
    recipe      Recipe intake
    specify     Specify phase output
    decompose   Decompose plan
    delivery    Delivery/Archive output (prefer archive.py for full automation)
    scaffold    Scaffold project-generation output
    package     Package signing and artifact manifest output
    release     Release tag and GitHub Release output
    monitor     Monitor SLO and dashboard output
    deploy      Deploy environment and health check output
    adversary   Adversary challenge analysis output
    grader      Grader verdict and score output
    nexus       Nexus graph query response output
    brainstorm  Brainstorm option set output
    enhance     Enhance input extraction output
    sharpen     Sharpen interpretation resolution output
    audit       Audit compliance report output
    ref-eval    Reference evaluation verdict and scores
    ref-comp    Post-implementation reference audit
    ref-plan    Reference integration plan output
    reviewer    Reviewer gate receipt (triggered or not)
    scopeframe  ScopeFrame session scope receipt
    propose     Propose option set receipt
    generic     Generic base-schema receipt for any module (use with --extra-json)
    reviewer    Reviewer budget-gated adversarial review output
    scopeframe  ScopeFrame session boundary declaration output
    propose     Propose option set output
    generic     Generic receipt for any module not covered above

Usage:
    # Verifier receipt:
    python .wabblespec/engine/shared/scripts/receipt-writer.py \\
        --type verifier \\
        --task-id seed-run-20260525xx \\
        --session-id seed-pipeline-xx \\
        --status PASS \\
        --wave 1 --wave-of 1 \\
        --check "V-01:PASS:File exists and parses" \\
        --check "V-02:PASS:All required sections present" \\
        --verified-at 2026-05-25T14:00:00Z \\
        --out .wabblespec/state/receipts/verifier-receipt-seed-run-20260525xx.json

    # Executor receipt:
    python .wabblespec/engine/shared/scripts/receipt-writer.py \\
        --type executor \\
        --task-id seed-run-20260525xx \\
        --session-id seed-pipeline-xx \\
        --status PASS \\
        --wave 1 --wave-of 1 \\
        --modules-activated l4/engineering l7/archive \\
        --files-written ".wabblespec/engine/shared/references/foo.md" \\
        --delta-class ADDITIVE \\
        --summary "Wrote foo.md and bar.md" \\
        --out .wabblespec/state/receipts/executor-receipt-seed-run-20260525xx.json

    # Recipe receipt:
    python .wabblespec/engine/shared/scripts/receipt-writer.py \\
        --type recipe \\
        --task-id seed-run-20260525xx \\
        --session-id seed-pipeline-xx \\
        --target Framework --platform CLI \\
        --complexity Low --confidence 0.97 \\
        --detection-method explicit-instruction \\
        --out .wabblespec/state/receipts/recipe-receipt-seed-run-20260525xx.json

    # Print to stdout instead of writing:
    python .wabblespec/engine/shared/scripts/receipt-writer.py --type verifier ... --out -

    # Validate a receipt against the base schema:
    python .wabblespec/engine/shared/scripts/receipt-writer.py --validate path/to/receipt.json

Exit codes:
    0  success (or validation pass)
    1  bad arguments or schema validation failure
    2  output path not writable; schema file missing
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone


NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Check parsing: "V-01:PASS:description text here"
# ---------------------------------------------------------------------------

def parse_check(raw):
    """Parse 'ID:RESULT:detail' into dict. Result defaults to PASS if omitted."""
    parts = raw.split(":", 2)
    if len(parts) == 1:
        return {"id": parts[0], "result": "PASS", "description": "", "detail": ""}
    if len(parts) == 2:
        return {"id": parts[0], "result": parts[1], "description": parts[1], "detail": ""}
    return {
        "id": parts[0],
        "result": parts[1],
        "description": parts[2][:80] if parts[2] else "",
        "detail": parts[2],
    }


# ---------------------------------------------------------------------------
# Receipt builders per type
# ---------------------------------------------------------------------------

def build_verifier(args):
    checks = [parse_check(c) for c in (args.check or [])]
    check_ids = [c["id"] for c in checks]
    all_pass = all(c["result"] == "PASS" for c in checks)
    return {
        "receipt_type": "verifier",
        "task_id": args.task_id,
        "session_id": args.session_id,
        "status": args.status if args.status else ("PASS" if all_pass else "FAIL"),
        "wave": args.wave,
        "wave_of": args.wave_of or args.wave,
        "checks": checks,
        "not_tested": args.not_tested or [],
        "verified_at": args.verified_at or NOW,
    }


def build_executor(args):
    return {
        "receipt_type": "executor",
        "task_id": args.task_id,
        "session_id": args.session_id,
        "status": args.status or "PASS",
        "wave": args.wave,
        "wave_of": args.wave_of or args.wave,
        "modules_activated": args.modules_activated or [],
        "files_written": args.files_written or [],
        "summary": args.summary or "",
        "not_tested": args.not_tested or [],
        "delta_class": args.delta_class or "ADDITIVE",
        "executed_at": args.executed_at or NOW,
    }


def build_recipe(args):
    return {
        "module": "recipe",
        "layer": "L0",
        "phase": "Intake",
        "wave": 0,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "target": args.target or "",
        "platform": args.platform or "CLI",
        "detection_method": args.detection_method or "explicit-instruction",
        "confidence": args.confidence if args.confidence is not None else 0.97,
        "complexity": args.complexity or "Low",
        "secondary_targets": args.secondary_targets or [],
        "collapse_eligible": args.collapse_eligible or False,
        "input_quality": {
            "vague": False,
            "broad": False,
            "enhanced": False,
            "sharpened": False,
        },
        "checks_run": ["target-detection", "complexity-score", "input-quality"],
        "checks_passed": ["target-detection", "complexity-score", "input-quality"],
        "status": args.status or "PASS",
        "confidence_score": args.confidence if args.confidence is not None else 0.97,
        "outputs": ["recipe.json"],
        "not_tested": args.not_tested or [],
    }


def build_specify(args):
    return {
        "module": "specify",
        "layer": "L1",
        "phase": "Specify",
        "wave": 0,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "checks_run": [
            "requirements-complete",
            "success-criteria-measurable",
            "failure-modes-declared",
            "no-pia-fields",
        ],
        "checks_passed": [
            "requirements-complete",
            "success-criteria-measurable",
            "failure-modes-declared",
            "no-pia-fields",
        ],
        "status": args.status or "PASS",
        "confidence_score": args.confidence if args.confidence is not None else 0.95,
        "requirements": args.requirements or [],
        "success_criteria": args.success_criteria or [],
        "failure_modes": args.failure_modes or [],
        "outputs": args.files_written or [],
        "not_tested": args.not_tested or [],
    }


def build_decompose(args):
    return {
        "module": "decompose",
        "layer": "L1",
        "phase": "Plan",
        "wave": 0,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "checks_run": [
            "wave-plan-complete",
            "dependencies-declared",
            "checkpoints-defined",
            "rollback-defined",
        ],
        "checks_passed": [
            "wave-plan-complete",
            "dependencies-declared",
            "checkpoints-defined",
            "rollback-defined",
        ],
        "status": args.status or "PASS",
        "confidence_score": args.confidence if args.confidence is not None else 0.95,
        "waves": args.waves_json or [],
        "total_waves": args.wave_of or 1,
        "outputs": ["task-card.md"],
        "not_tested": args.not_tested or [],
    }


def build_scaffold(args):
    return {
        "receipt_type": "scaffold",
        "module": "scaffold",
        "layer": "L7",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "platform": args.platform or "",
        "target": args.target or "",
        "files_generated": args.files_written or [],
        "project_map_written": True,
        "not_tested": args.not_tested or [],
    }


def build_package(args):
    return {
        "receipt_type": "package",
        "module": "package",
        "layer": "L7",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "version": args.target or "",
        "artifacts_packaged": len(args.files_written or []),
        "artifacts": args.files_written or [],
        "all_signed": True,
        "manifest_path": "",
        "signing_method": "",
        "not_tested": args.not_tested or [],
    }


def build_release(args):
    return {
        "receipt_type": "release",
        "module": "release",
        "layer": "L7",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "version": args.target or "",
        "tag_name": f"v{args.target}" if args.target else "",
        "github_release_url": "",
        "release_notes_source": ".wabblespec/CHANGELOG.md",
        "not_tested": args.not_tested or [],
    }


def build_monitor(args):
    return {
        "receipt_type": "monitor",
        "module": "monitor",
        "layer": "L7",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "slos_checked": len(args.success_criteria or []),
        "slo_definitions": args.success_criteria or [],
        "dashboard_path": "",
        "alert_rules_count": 0,
        "health_status": "HEALTHY",
        "not_tested": args.not_tested or [],
    }


def build_deploy(args):
    return {
        "receipt_type": "deploy",
        "module": "deploy",
        "layer": "L7",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "environment": args.target or "",
        "deployment_status": "DEPLOYED" if (args.status or "PASS") == "PASS" else "FAILED",
        "health_check_passed": (args.status or "PASS") == "PASS",
        "rollback_available": True,
        "artifacts_deployed": args.files_written or [],
        "not_tested": args.not_tested or [],
    }


def build_adversary(args):
    return {
        "receipt_type": "adversary",
        "module": "adversary",
        "layer": "L2",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "challenger_mode": args.target or "open",
        "challenge_scope": args.challenge_scope or "",
        "spec_artifact_path": args.spec_artifact_path or "",
        "cycle": args.cycle if args.cycle is not None else 0,
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "challenges_produced": len(args.failure_modes or []),
        "challenge_domains_covered": args.failure_modes or [],
        "findings_raw": args.findings_raw or [],
        "major_count": args.major_count if args.major_count is not None else 0,
        "minor_count": args.minor_count if args.minor_count is not None else 0,
        "anchoring_prevention_applied": True,
        "strong_output_acknowledged": False,
        "counter_analysis": args.summary or "",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.0,
    }


def build_grader(args):
    # --verdict takes precedence; fall back to status-derived only if not supplied
    if args.verdict:
        verdict = args.verdict
    else:
        verdict = "ACCEPT" if (args.status or "PASS") == "PASS" else "REVISE"
    return {
        "receipt_type": "grader",
        "module": "grader",
        "layer": "L2",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "cycle": args.cycle if args.cycle is not None else 0,
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "verdict": verdict,
        "score": args.confidence if args.confidence is not None else 0.85,
        "score_rationale": args.summary or "",
        "grader_reasoning": args.grader_reasoning or "",
        "spec_artifact_path": args.spec_artifact_path or "",
        "adversary_receipt_path": args.adversary_receipt_path_single or "",
        "revision_guidance": args.revision_guidance or None,
        "escalation_reason": args.escalation_reason or None,
        "adversary_concerns_assessed": args.adversary_concerns_assessed if args.adversary_concerns_assessed is not None else 0,
        "adversary_concerns_within_scope": args.adversary_concerns_within_scope if args.adversary_concerns_within_scope is not None else 0,
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.85,
    }


def build_nexus(args):
    return {
        "receipt_type": "nexus",
        "module": "nexus",
        "layer": "L5",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "query": args.summary or "",
        "nodes_traversed": 0,
        "edges_followed": 0,
        "response_path": "",
        "not_tested": args.not_tested or [],
    }


def build_brainstorm(args):
    return {
        "receipt_type": "brainstorm",
        "module": "brainstorm",
        "layer": "L1",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "options_generated": len(args.requirements or []),
        "options_passed_filter": len(args.requirements or []),
        "options_path": "",
        "not_tested": args.not_tested or [],
    }


def build_enhance(args):
    return {
        "receipt_type": "enhance",
        "module": "enhance",
        "layer": "L1",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "dimensions_extracted": 0,
        "questions_asked": 0,
        "enhanced_input_path": "",
        "not_tested": args.not_tested or [],
    }


def build_sharpen(args):
    return {
        "receipt_type": "sharpen",
        "module": "sharpen",
        "layer": "L1",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "interpretations_resolved": 0,
        "interpretation_selected": args.summary or "",
        "not_tested": args.not_tested or [],
    }


def build_ref_eval(args):
    return {
        "receipt_type": "ref-eval",
        "module": "ref-eval",
        "layer": "L2",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "reference_path": "",
        "reference_slug": args.target or "",
        "reference_type": "",
        "project_context_loaded": True,
        "reference_load_drawer_id": "",
        "verdict": args.summary or "supporting-reference",
        "integration_scores": {
            "concept_fit": 0,
            "architecture_fit": 0,
            "implementation_fit": 0,
            "maintenance_fit": 0,
            "risk_level": 0,
            "overall_usefulness": 0,
        },
        "benefits_identified": 0,
        "risks_identified": 0,
        "adapt_items": 0,
        "avoid_items": 0,
        "report_path": "",
        "drawers_written": 0,
        "depth": "deep",
        "dedup_hit": False,
        "confidence": args.confidence if args.confidence is not None else 0.0,
        "not_tested": args.not_tested or [],
    }


def build_ref_comp(args):
    return {
        "receipt_type": "ref-comp",
        "module": "ref-comp",
        "layer": "L2",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "reference": "",
        "reference_slug": args.target or "",
        "scope": "full",
        "ref_plan_available": False,
        "ref_eval_available": False,
        "dedup_hit": False,
        "coverage_rate": args.confidence if args.confidence is not None else 0.0,
        "execution_gaps": {"critical": 0, "major": 0, "minor": 0},
        "improvements_beyond_plan": 0,
        "execution_classification": args.summary or "substantially-complete",
        "report_path": "",
        "drawers_written": 0,
        "confidence": args.confidence if args.confidence is not None else 0.0,
        "not_tested": args.not_tested or [],
    }


def build_ref_plan(args):
    return {
        "receipt_type": "ref-plan",
        "module": "ref-plan",
        "layer": "L2",
        "phase": "Plan",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "reference_slug": args.target or "",
        "ref_eval_verdict": args.summary or "supporting-reference",
        "integration_goal": "",
        "risk_appetite": "balanced",
        "signal_items_found": len(args.requirements or []),
        "items_excluded": 0,
        "backlog_size": len(args.requirements or []),
        "phase_1_items": 0,
        "phase_2_items": 0,
        "phase_3_items": 0,
        "phase_4_items": 0,
        "plan_path": "",
        "not_tested": args.not_tested or [],
    }


def build_audit(args):
    return {
        "receipt_type": "audit",
        "module": "audit",
        "layer": "L2",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "status": args.status or "PASS",
        "violations_found": 0,
        "violations_critical": 0,
        "violations_high": 0,
        "attestation_required": False,
        "report_path": "",
        "not_tested": args.not_tested or [],
    }


# ---------------------------------------------------------------------------
# finding_summary helper — must be defined before build_reviewer
# ---------------------------------------------------------------------------

def _compute_finding_summary(findings):
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    pi_flags = 0
    gen_excluded = 0
    for f in findings:
        sev = f.get("severity", "INFO")
        if sev in sev_counts:
            sev_counts[sev] += 1
        if f.get("prompt_injection_risk"):
            pi_flags += 1
        if f.get("generated_file_excluded"):
            gen_excluded += 1
    return {
        "total": len(findings),
        "by_severity": sev_counts,
        "prompt_injection_flags": pi_flags,
        "generated_files_excluded": gen_excluded,
    }


def build_reviewer(args):
    findings = args.findings_json or []
    return {
        "receipt_type": "reviewer",
        "module": "reviewer",
        "layer": "L2",
        "phase": "Plan",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "inputs": args.inputs_json or [],
        "triggered": args.triggered,
        "trigger_condition": args.trigger_condition or "NOT_TRIGGERED",
        "revise_cycles": args.revise_cycles if args.revise_cycles is not None else 0,
        "verdict": args.verdict or "NOT_TRIGGERED",
        "grader_score": args.grader_score if args.grader_score is not None else 0.0,
        "escalated": args.escalated,
        "escalation_reason": args.escalation_reason or None,
        "findings": findings,
        "finding_summary": _compute_finding_summary(findings),
        "adversary_receipt_path": args.adversary_receipt_paths or [],
        "grader_receipt_path": args.grader_receipt_path or None,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.0,
    }


def build_scopeframe(args):
    return {
        "receipt_type": "scopeframe",
        "module": "scope-frame",
        "layer": "L1",
        "phase": "Research",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "checks_run": args.checks_run or ["scope-boundaries-declared", "in-scope-nonempty", "out-of-scope-nonempty", "assumptions-declared"],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "outputs": args.files_written or [],
        "in_scope_count": args.in_scope_count if args.in_scope_count is not None else 0,
        "out_of_scope_count": args.out_of_scope_count if args.out_of_scope_count is not None else 0,
        "assumptions_count": args.assumptions_count if args.assumptions_count is not None else 0,
        "user_confirmed": not args.not_user_confirmed,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_propose(args):
    return {
        "receipt_type": "propose",
        "module": "propose",
        "layer": "L1",
        "phase": "Plan",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "inputs": args.inputs_json or [],
        "outputs": args.files_written or [],
        "options_count": len(args.requirements or []),
        "options": args.requirements or [],
        "recommendation": args.summary or "",
        "impact": args.impact or "MEDIUM",
        "reviewer_required_at_plan": args.reviewer_required,
        "selection_deferred": True,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_generic(args):
    return {
        "receipt_type": args.module or "generic",
        "module": args.module or "generic",
        "layer": args.layer_override or "L1",
        "phase": args.phase_override or "Execute",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "outputs": args.files_written or [],
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


BUILDERS = {
    "verifier": build_verifier,
    "executor": build_executor,
    "recipe": build_recipe,
    "specify": build_specify,
    "decompose": build_decompose,
    "scaffold": build_scaffold,
    "package": build_package,
    "release": build_release,
    "monitor": build_monitor,
    "deploy": build_deploy,
    "adversary": build_adversary,
    "grader": build_grader,
    "nexus": build_nexus,
    "brainstorm": build_brainstorm,
    "enhance": build_enhance,
    "sharpen": build_sharpen,
    "audit": build_audit,
    "ref-eval": build_ref_eval,
    "ref-comp": build_ref_comp,
    "ref-plan": build_ref_plan,
    "reviewer": build_reviewer,
    "scopeframe": build_scopeframe,
    "propose": build_propose,
    "generic": build_generic,
}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _upsert_to_db(data, out_path):
    """Upsert receipt into DuckDB store if receipts.duckdb exists. Auto-detects DB. Silent-fail."""
    try:
        import duckdb as _duckdb
    except ImportError:
        return  # duckdb not installed — skip silently

    # Find DB alongside the receipts directory
    receipts_dir = os.path.dirname(os.path.abspath(out_path))
    db_path = os.path.join(receipts_dir, "receipts.duckdb")
    if not os.path.isfile(db_path):
        return  # DB not initialized — skip silently (no error; DB is optional)

    receipt_id = os.path.splitext(os.path.basename(out_path))[0]
    try:
        con = _duckdb.connect(db_path)
        con.execute(
            """
            INSERT OR REPLACE INTO receipts
                (receipt_id, session_id, module, status, timestamp, wave, delta_class, receipt_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                receipt_id,
                data.get("session_id") or data.get("task_id"),
                data.get("module") or data.get("receipt_type"),
                data.get("status"),
                data.get("timestamp") or data.get("written_at"),
                data.get("wave"),
                data.get("delta_class"),
                json.dumps(data),
            ],
        )
        con.close()
    except Exception:
        pass  # Silent-fail — DuckDB write never blocks receipt JSON write


def write_receipt(data, out_path, dry_run=False, also_db=True):
    """Write receipt JSON. also_db=True (default): auto-upsert into DuckDB if DB exists."""
    text = json.dumps(data, indent=2) + "\n"
    if out_path == "-" or dry_run:
        if dry_run:
            print("--- DRY RUN ---")
        print(text)
        return
    tmp = out_path + ".tmp"
    try:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, out_path)
    except OSError as e:
        print(f"ERROR: Cannot write to {out_path}: {e}", file=sys.stderr)
        sys.exit(2)
    print(f"Wrote {out_path}")
    if also_db:
        _upsert_to_db(data, out_path)


# ---------------------------------------------------------------------------
# Validation (structural only — checks required fields from base schema)
# ---------------------------------------------------------------------------

BASE_REQUIRED = {"status", "not_tested"}
VERIFIER_REQUIRED = {"receipt_type", "task_id", "status", "checks", "verified_at"}
EXECUTOR_REQUIRED = {"receipt_type", "task_id", "status", "delta_class", "executed_at"}
# Delivery receipts use a different schema from the base (not_tested_list not not_tested).
# They are validated separately.
DELIVERY_REQUIRED = {"receipt_type", "task_id", "status", "version_new", "version_previous"}


def validate_receipt(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot parse {path}: {e}")
        return False

    rtype = data.get("receipt_type") or data.get("module") or "(unknown)"
    errors = []

    # Delivery receipts follow a distinct schema (not the base schema)
    if data.get("receipt_type") in ("delivery", "archive"):
        required = DELIVERY_REQUIRED
    elif data.get("receipt_type") == "verifier":
        required = BASE_REQUIRED | VERIFIER_REQUIRED
    elif data.get("receipt_type") == "executor":
        required = BASE_REQUIRED | EXECUTOR_REQUIRED
    else:
        required = BASE_REQUIRED.copy()

    for field in sorted(required):
        if field not in data:
            errors.append(f"missing required field: '{field}'")

    status = data.get("status")
    if status not in ("PASS", "FAIL", "PARTIAL"):
        errors.append(f"status '{status}' not in PASS/FAIL/PARTIAL")

    if status in ("FAIL", "PARTIAL") and "failure_reason" not in data:
        errors.append("status FAIL/PARTIAL requires 'failure_reason'")

    # Type-specific conditional validation (only when receipt declares the key,
    # indicating it was produced by the new builder; legacy hand-authored receipts
    # that omit the key entirely are accepted by base schema only)
    if rtype == "grader" and "escalation_reason" in data:
        verdict = data.get("verdict")
        if verdict == "REVISE" and not data.get("revision_guidance"):
            errors.append("verdict REVISE requires 'revision_guidance'")
        if verdict == "ESCALATE" and not data.get("escalation_reason"):
            errors.append("verdict ESCALATE requires 'escalation_reason'")

    if errors:
        print(f"FAIL [{rtype}] {os.path.basename(path)}:")
        for e in errors:
            print(f"  - {e}")
        return False

    print(f"PASS [{rtype}] {os.path.basename(path)}")
    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Write a schema-valid receipt JSON without reading existing files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--type",
        choices=list(BUILDERS.keys()),
        dest="receipt_type",
        help="Receipt type to generate.",
    )
    parser.add_argument("--task-id", metavar="ID")
    parser.add_argument("--session-id", metavar="ID")
    parser.add_argument("--status", choices=["PASS", "FAIL", "PARTIAL"])
    parser.add_argument("--wave", type=int, default=1)
    parser.add_argument("--wave-of", type=int)
    parser.add_argument("--not-tested", nargs="*", metavar="ITEM")
    parser.add_argument(
        "--check",
        action="append",
        metavar="ID:RESULT:detail",
        help="Verifier check in 'ID:RESULT:detail' format. Repeat for each check.",
    )
    parser.add_argument("--verified-at", metavar="ISO8601")
    parser.add_argument("--executed-at", metavar="ISO8601")
    parser.add_argument("--timestamp", metavar="ISO8601")
    parser.add_argument("--modules-activated", nargs="*", metavar="MODULE")
    parser.add_argument("--files-written", nargs="*", metavar="PATH")
    parser.add_argument("--summary", metavar="TEXT")
    parser.add_argument("--delta-class", choices=["BREAKING", "ADDITIVE", "COSMETIC"])
    parser.add_argument("--target", metavar="TEXT", help="Recipe: target type.")
    parser.add_argument("--platform", metavar="TEXT", help="Recipe: platform.")
    parser.add_argument("--complexity", choices=["Low", "Medium", "High"])
    parser.add_argument("--confidence", type=float, metavar="0.0-1.0")
    parser.add_argument("--detection-method", metavar="TEXT")
    parser.add_argument("--secondary-targets", nargs="*", metavar="TARGET")
    parser.add_argument("--collapse-eligible", action="store_true")
    parser.add_argument(
        "--requirements",
        nargs="*",
        metavar="REQ",
        help="Specify: requirement strings.",
    )
    parser.add_argument("--success-criteria", nargs="*", metavar="CRITERION")
    parser.add_argument("--failure-modes", nargs="*", metavar="MODE")
    parser.add_argument(
        "--waves-json",
        metavar="JSON",
        type=json.loads,
        help='Decompose: JSON array of wave objects e.g. \'[{"wave":1,"name":"..."}]\'',
    )

    # Global args available to all builders
    parser.add_argument("--checks-run", nargs="*", metavar="CHECK", help="Generic checks_run list.")
    parser.add_argument("--checks-passed", nargs="*", metavar="CHECK", help="Generic checks_passed list.")
    parser.add_argument("--evidence", nargs="*", metavar="PATH", help="Evidence file paths.")
    parser.add_argument("--cycle", type=int, metavar="N", help="Revision/review cycle number.")
    parser.add_argument(
        "--verdict",
        choices=["ACCEPT", "REVISE", "ESCALATE", "NOT_TRIGGERED"],
        help="Explicit verdict (grader, reviewer).",
    )
    parser.add_argument(
        "--extra-json",
        type=json.loads,
        metavar="JSON",
        help="Arbitrary JSON dict merged into the receipt last (escape hatch for any field no named arg covers).",
    )

    # Adversary-specific args
    parser.add_argument("--challenge-scope", metavar="TEXT", help="Adversary: challenge scope.")
    parser.add_argument("--spec-artifact-path", metavar="PATH", help="Adversary/grader: spec artifact path.")
    parser.add_argument("--findings-raw", nargs="*", metavar="FINDING", help="Adversary: raw findings list.")
    parser.add_argument("--major-count", type=int, metavar="N", help="Adversary: major finding count.")
    parser.add_argument("--minor-count", type=int, metavar="N", help="Adversary: minor finding count.")

    # Grader-specific args
    parser.add_argument("--grader-reasoning", metavar="TEXT", help="Grader: reasoning text.")
    parser.add_argument("--adversary-receipt-path-single", metavar="PATH", help="Grader: single adversary receipt path.")
    parser.add_argument("--revision-guidance", metavar="TEXT", help="Grader: guidance for REVISE verdict.")
    parser.add_argument("--escalation-reason", metavar="TEXT", help="Grader/reviewer: reason for ESCALATE verdict.")
    parser.add_argument("--adversary-concerns-assessed", type=int, metavar="N", help="Grader: number of adversary concerns assessed.")
    parser.add_argument("--adversary-concerns-within-scope", type=int, metavar="N", help="Grader: number of adversary concerns within scope.")

    # Reviewer-specific args
    parser.add_argument("--triggered", action="store_true", help="Reviewer: whether reviewer was triggered.")
    parser.add_argument("--trigger-condition", metavar="TEXT", help="Reviewer: trigger condition string.")
    parser.add_argument("--revise-cycles", type=int, metavar="N", help="Reviewer: number of revise cycles.")
    parser.add_argument("--grader-score", type=float, metavar="0.0-1.0", help="Reviewer: grader score.")
    parser.add_argument("--escalated", action="store_true", help="Reviewer: whether escalated.")
    parser.add_argument(
        "--findings-json",
        type=json.loads,
        metavar="JSON",
        help="Reviewer: JSON array of finding objects.",
    )
    parser.add_argument(
        "--inputs-json",
        type=json.loads,
        metavar="JSON",
        help="Reviewer/propose: JSON array of input objects.",
    )
    parser.add_argument("--adversary-receipt-paths", nargs="*", metavar="PATH", help="Reviewer: array of adversary receipt paths.")
    parser.add_argument("--grader-receipt-path", metavar="PATH", help="Reviewer: grader receipt path.")

    # ScopeFrame-specific args
    parser.add_argument("--in-scope-count", type=int, metavar="N", help="ScopeFrame: number of in-scope items.")
    parser.add_argument("--out-of-scope-count", type=int, metavar="N", help="ScopeFrame: number of out-of-scope items.")
    parser.add_argument("--assumptions-count", type=int, metavar="N", help="ScopeFrame: number of assumptions.")
    parser.add_argument("--not-user-confirmed", action="store_true", help="ScopeFrame: scope was NOT user-confirmed (inverts default confirmed=True).")

    # Propose-specific args
    parser.add_argument("--impact", choices=["LOW", "MEDIUM", "HIGH"], help="Propose: impact level.")
    parser.add_argument("--reviewer-required", action="store_true", help="Propose: reviewer required at plan phase.")

    # Generic builder args
    parser.add_argument("--module", metavar="TEXT", help="Generic: module name (sets receipt_type and module fields).")
    parser.add_argument("--layer-override", metavar="TEXT", help="Generic: layer override (e.g. L1, L2).")
    parser.add_argument("--phase-override", metavar="TEXT", help="Generic: phase override (e.g. Research, Plan, Execute).")

    parser.add_argument(
        "--out",
        metavar="PATH",
        default="-",
        help="Output path. Use '-' for stdout (default).",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--no-db", action="store_false", dest="also_db",
        help="Skip DuckDB upsert even if receipts.duckdb exists.",
    )
    parser.set_defaults(also_db=True)
    parser.add_argument(
        "--validate",
        metavar="PATH",
        help="Validate an existing receipt JSON instead of writing a new one.",
    )

    args = parser.parse_args()

    # Validate mode
    if args.validate:
        ok = validate_receipt(args.validate)
        sys.exit(0 if ok else 1)

    if not args.receipt_type:
        parser.error("--type is required.")
    if not args.task_id:
        parser.error("--task-id is required.")

    builder = BUILDERS[args.receipt_type]
    data = builder(args)

    if getattr(args, 'extra_json', None):
        data.update(args.extra_json)

    write_receipt(data, args.out, dry_run=args.dry_run, also_db=getattr(args, "also_db", False))
    sys.exit(0)


if __name__ == "__main__":
    main()
