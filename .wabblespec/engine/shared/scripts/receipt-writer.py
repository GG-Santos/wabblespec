"""
receipt-writer.py — Schema-enforced receipt serializer.

Claude provides the reasoning-dependent content (check descriptions, summaries,
what was not tested). This script handles structure, required fields, and JSON
serialization — eliminating the per-receipt "which fields does this type need?"
reasoning overhead (~300-1000 tokens per receipt).

Supported receipt types:
    verifier            Verifier gate output
    executor            Executor wave output
    recipe              Recipe intake
    specify             Specify phase output
    decompose           Decompose plan
    delivery            Delivery/Archive output (prefer archive.py for full automation)
    scaffold            Scaffold project-generation output
    package             Package signing and artifact manifest output
    release             Release tag and GitHub Release output
    monitor             Monitor SLO and dashboard output
    deploy              Deploy environment and health check output
    adversary           Adversary challenge analysis output
    grader              Grader verdict and score output
    nexus               Nexus graph query response output
    brainstorm          Brainstorm option set output
    enhance             Enhance input extraction output
    sharpen             Sharpen interpretation resolution output
    audit               Audit compliance report output
    ref-eval            Reference evaluation verdict and scores
    ref-comp            Post-implementation reference audit
    ref-plan            Reference integration plan output
    reviewer            Reviewer budget-gated adversarial review output
    scopeframe          ScopeFrame session boundary declaration output
    propose             Propose option set output
    generic             Generic receipt for any module not covered above
    ground              Ground claim verification output (L0)
    runtime-probe       Runtime capability detection output (L0)
    platform-activation Platform module activation receipt (L3, all 11 platforms)
    gateway-spec        Gateway Phase A spec declaration receipt (L4, all 6 gateways)
    gateway-verdict     Gateway Phase B verdict receipt (L4, all 6 gateways)
    memory-write        Memory drawer write/update/transition receipt (L5)
    memory-search       Memory search query receipt (L5)
    forget              Memory deletion receipt (L5)
    inference-guard     InferenceGuard activation/bypass receipt (L2)
    model-router        ModelRouter capability selection receipt (L2)
    forge               Forge L8 promotion output (L8)
    augment             Augment module file generation output (L8)
    blueprint           Blueprint attestation and plan output (L8)
    benchmark           Benchmark metric evaluation output (L8)
    synth               Synth candidate generation output (L8)
    guard           Guard five-layer pre-wave validation receipt (L2)
    wave            Executor intermediate wave completion receipt
    memory-mine     Memory mine deep pattern scan receipt (L5)
    experiment      L8 experiment conclusion receipt (hypothesis→outcome→learnings)

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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "options_path": args.options_path or "",
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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
        "confidence": args.confidence if args.confidence is not None else 1.0,
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


# ---------------------------------------------------------------------------
# New builders: ground, runtime-probe, platform-activation, gateway-spec,
# gateway-verdict, memory-write, memory-search, forget, inference-guard,
# model-router
# ---------------------------------------------------------------------------

def build_ground(args):
    return {
        "receipt_type": "ground",
        "module": "ground",
        "layer": "L0",
        "phase": "Research",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "task_card_path": args.task_card_path or ".wabblespec/state/plans/task-card.md",
        "claims_total": args.claims_total if args.claims_total is not None else 0,
        "verified": args.verified_claims or [],
        "unverified": args.unverified_claims or [],
        "assumed": args.assumed_claims or [],
        "missing": args.missing_claims or [],
        "block_reason": args.block_reason or None,
        "grounded_at": args.timestamp or NOW,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_runtime_probe(args):
    return {
        "receipt_type": "runtime-probe",
        "module": "runtime-probe",
        "layer": "L0",
        "phase": "Research",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [".wabblespec/runtime/runtime-state.json"],
        "outputs": args.files_written or [".wabblespec/runtime/runtime-state.json"],
        "overrides_applied": args.overrides_applied,
        "capabilities_detected": args.capabilities_detected or [],
        "capabilities_unavailable": args.capabilities_unavailable or [],
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_platform_activation(args):
    return {
        "receipt_type": "platform-activation",
        "module": "platform-{}".format(args.platform_id) if args.platform_id else "platform",
        "layer": "L3",
        "phase": "Research",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "platform_id": args.platform_id or "",
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "spec_templates_loaded": args.spec_templates_loaded or [],
        "security_controls_loaded": args.security_controls_loaded or [],
        "gateway_refs_loaded": args.gateway_refs_loaded or [],
        "language_modules_activated": args.language_modules_activated or [],
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_gateway_spec(args):
    return {
        "receipt_type": "gateway-spec",
        "module": "gateway-{}".format(args.gateway_id) if args.gateway_id else "gateway",
        "layer": "L4",
        "phase": "Research",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "gateway_id": args.gateway_id or "",
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "gates_declared": args.gates_declared or [],
        "blocking_gates": args.blocking_gates or [],
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_gateway_verdict(args):
    return {
        "receipt_type": "gateway-verdict",
        "module": "gateway-{}".format(args.gateway_id) if args.gateway_id else "gateway",
        "layer": "L4",
        "phase": "Execute",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "gateway_id": args.gateway_id or "",
        "checks_run": args.checks_run or [],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "verdict": args.gateway_verdict or "PASS",
        "violations": args.violations or [],
        "attestation_required": args.attestation_required,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_memory_write(args):
    return {
        "receipt_type": "memory-write",
        "module": "memory",
        "layer": "L5",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "drawer_id": args.drawer_id or "",
        "operation": args.memory_operation or "write",
        "topic": args.topic or "",
        "wing": args.wing or "",
        "room": args.room or "",
        "staleness_before": args.staleness_before or None,
        "staleness_after": args.staleness_after or "FRESH",
        "provenance_notified": not args.provenance_not_notified,
        "backend": args.backend or "memory/chromadb",
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_memory_search(args):
    return {
        "receipt_type": "memory-search",
        "module": "memory-search",
        "layer": "L5",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "query": args.summary or "",
        "results_returned": args.results_returned if args.results_returned is not None else 0,
        "max_results": args.max_results if args.max_results is not None else 10,
        "staleness_filters_applied": args.staleness_filters or [],
        "dedup_applied": args.dedup_applied,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_forget(args):
    return {
        "receipt_type": "forget",
        "module": "forget",
        "layer": "L5",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "deletion_type": args.deletion_type or "single",
        "drawer_ids_deleted": args.drawer_ids_deleted or [],
        "drawers_deleted_count": len(args.drawer_ids_deleted or []),
        "provenance_record_path": args.provenance_record_path or "",
        "entity_graph_notified": not args.entity_graph_not_notified,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_inference_guard(args):
    return {
        "receipt_type": "inference-guard",
        "module": "inference-guard",
        "layer": "L2",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "activated": args.activated,
        "tier_applied": args.tier_applied or "light",
        "triggers_detected": args.triggers_detected or [],
        "transforms_applied": args.transforms_applied or [],
        "reason": args.non_activation_reason or None,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_model_router(args):
    return {
        "receipt_type": "model-router",
        "module": "model-router",
        "layer": "L2",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "selected_capability": args.selected_capability or "",
        "task_shape": args.task_shape or "",
        "fallback_capability": args.fallback_capability or None,
        "ensemble_triggered": args.ensemble_triggered,
        "ensemble_trigger_reason": args.ensemble_trigger_reason or None,
        "verification_mode": args.verification_mode or "",
        "inference_guard_eligible": args.inference_guard_eligible,
        "routing_reason": args.summary or "",
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_forge(args):
    promotions = args.promotions_json or []
    return {
        "receipt_type": "forge",
        "module": "forge",
        "layer": "L8",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "attested_by": args.attested_by or "",
        "attestation_statement": args.attestation_statement or "",
        "promotions": promotions,
        "promotions_count": len(promotions),
        "archive_path": args.forge_archive_path or ".wabblespec/experiments/archive/provenance.json",
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.95,
    }


def build_augment(args):
    return {
        "receipt_type": "augment",
        "module": "augment",
        "layer": "L8",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "blueprint_id": args.blueprint_id or "",
        "affected_module": args.affected_module or "",
        "change_type": args.change_type or "AUGMENT",
        "output_path": args.augment_output_path or "",
        "files_written": args.files_written or [],
        "structural_check_passed": not args.structural_check_failed,
        "placeholders_remaining": args.placeholders_remaining if args.placeholders_remaining is not None else 0,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.95,
    }


def build_blueprint(args):
    return {
        "receipt_type": "blueprint",
        "module": "blueprint",
        "layer": "L8",
        "phase": "Plan",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "blueprint_id": args.blueprint_id or "",
        "affected_module": args.affected_module or "",
        "change_type": args.change_type or "AUGMENT",
        "attestation_confirmed": not args.attestation_not_confirmed,
        "attested_by": args.attested_by or "",
        "attested_at": args.attested_at or NOW,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.95,
    }


def build_benchmark(args):
    return {
        "receipt_type": "benchmark",
        "module": "benchmark",
        "layer": "L8",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "blueprint_id": args.blueprint_id or "",
        "metric_name": args.metric_name or "",
        "held_out_cases": args.held_out_cases if args.held_out_cases is not None else 0,
        "held_out_value": args.held_out_value if args.held_out_value is not None else 0.0,
        "threshold": args.threshold if args.threshold is not None else 0.0,
        "verdict": "PASS" if (args.held_out_value or 0.0) >= (args.threshold or 0.0) else "FAIL",
        "fixture_set": args.fixture_set or "",
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.95,
    }


def build_synth(args):
    return {
        "receipt_type": "synth",
        "module": "synth",
        "layer": "L8",
        "phase": "Plan",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "instinct_observation_id": args.instinct_observation_id or "",
        "candidate_id": args.candidate_id or "",
        "candidate_path": args.candidate_path or "",
        "pattern_occurrence_count": args.pattern_occurrence_count if args.pattern_occurrence_count is not None else 0,
        "hypothesis": args.summary or "",
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.85,
    }


def build_guard(args):
    layer_results = args.layer_results_json or {}
    overall = args.overall or (args.status or "PASS")
    return {
        "receipt_type": "guard",
        "module": "guard",
        "layer": "L2",
        "phase": "Execute",
        "wave": args.wave,
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "checks_run": args.checks_run or [
            "layer1-schema-validity", "layer2-scope-constraints",
            "layer3-invariant-compliance", "layer4-authority-ownership",
            "layer5-command-risk"
        ],
        "checks_passed": args.checks_passed or [],
        "evidence": args.evidence or [],
        "overall": overall,
        "layer_results": layer_results,
        "unauthorized_files": args.unauthorized_files or [],
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_wave(args):
    return {
        "receipt_type": "wave",
        "session_id": args.session_id,
        "task_id": args.task_id,
        "wave_number": args.wave,
        "wave_label": args.summary or "",
        "timestamp": args.timestamp or NOW,
        "status": args.status or "COMPLETE",
        "files_modified": args.files_written or [],
        "changes": args.wave_changes or [],
        "verification": {
            "method": args.verification_method or "",
            "command": args.verification_command or "",
            "result": "PASS" if (args.status or "COMPLETE") in ("COMPLETE", "PASS") else "FAIL",
            "unauthorized_files": args.unauthorized_files or [],
        },
        "acceptance_criteria_covered": args.ac_covered or [],
        "confidence": args.confidence if args.confidence is not None else 1.0,
        "not_tested": args.not_tested or [],
    }


def build_memory_mine(args):
    return {
        "receipt_type": "memory-mine",
        "module": "memory-mine",
        "layer": "L5",
        "phase": "Research",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "schema_version_current": args.schema_version if args.schema_version is not None else 1,
        "drawers_analyzed": args.drawers_analyzed if args.drawers_analyzed is not None else 0,
        "drawers_skipped_schema_mismatch": args.drawers_skipped if args.drawers_skipped is not None else 0,
        "gaps_found": args.gaps_found if args.gaps_found is not None else 0,
        "clusters_found": args.clusters_found if args.clusters_found is not None else 0,
        "patterns_found": args.patterns_found if args.patterns_found is not None else 0,
        "dedup_candidates_found": args.dedup_candidates if args.dedup_candidates is not None else 0,
        "staleness_critical": args.staleness_critical if args.staleness_critical is not None else 0,
        "output_dir": args.mine_output_dir or "",
        "dry_run": args.dry_run,
        "status": args.status or "PASS",
        "not_tested": args.not_tested or [],
        "confidence": args.confidence if args.confidence is not None else 0.9,
    }


def build_wave_review(args):
    return {
        "receipt_type": "wave-review",
        "module": "wave-reviewer",
        "layer": "L2",
        "phase": "Verify",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "git_ref": args.target or "HEAD",
        "review_type": getattr(args, "review_type", None) or "standard",
        "verdict": "PASS" if (args.status or "PASS") == "PASS" else "FAIL",
        "status": args.status or "PASS",
        "finding_summary": {
            "total": 0,
            "by_severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        },
        "findings": [],
        "confidence": args.confidence if args.confidence is not None else 0.85,
        "summary": args.summary or "",
    }


def build_experiment(args):
    outcome_raw = (getattr(args, "experiment_outcome", None) or "").upper()
    outcome = outcome_raw if outcome_raw in ("CONFIRMED", "REFUTED", "INCONCLUSIVE") else "INCONCLUSIVE"
    return {
        "receipt_type": "experiment",
        "module": "benchmark-loop",
        "layer": "L8",
        "phase": "Execute",
        "timestamp": args.timestamp or NOW,
        "session_id": args.session_id,
        "task_id": args.task_id,
        "hypothesis": args.experiment_hypothesis or "",
        "variants": args.experiment_variants or [],
        "primary_metric": getattr(args, "experiment_primary_metric", None) or "",
        "winner": getattr(args, "experiment_winner", None) or "",
        "outcome": outcome,
        "learnings": getattr(args, "experiment_learnings", None) or "",
        "status": args.status or "COMPLETE",
        "confidence": args.confidence if args.confidence is not None else 0.8,
        "summary": args.summary or "",
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
    "ground": build_ground,
    "runtime-probe": build_runtime_probe,
    "platform-activation": build_platform_activation,
    "gateway-spec": build_gateway_spec,
    "gateway-verdict": build_gateway_verdict,
    "memory-write": build_memory_write,
    "memory-search": build_memory_search,
    "forget": build_forget,
    "inference-guard": build_inference_guard,
    "model-router": build_model_router,
    "forge": build_forge,
    "augment": build_augment,
    "blueprint": build_blueprint,
    "benchmark": build_benchmark,
    "synth": build_synth,
    "guard": build_guard,
    "wave": build_wave,
    "memory-mine": build_memory_mine,
    "wave-review": build_wave_review,
    "experiment": build_experiment,
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

BASE_REQUIRED = {"status", "not_tested", "confidence"}
VERIFIER_REQUIRED = {"receipt_type", "task_id", "status", "checks", "verified_at"}
EXECUTOR_REQUIRED = {"receipt_type", "task_id", "status", "delta_class", "executed_at"}
# Delivery receipts use a different schema from the base (not_tested_list not not_tested).
# They are validated separately.
DELIVERY_REQUIRED = {"task_id", "status", "version_new", "version_previous"}

VALID_STATUSES = {"PASS", "FAIL", "PARTIAL"}
WAVE_STATUSES = {"PASS", "FAIL", "PARTIAL", "COMPLETE", "BLOCKED"}


def validate_receipt(path, lenient=False):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL: Cannot parse {path}: {e}")
        return False

    rtype = data.get("receipt_type") or data.get("module") or "(unknown)"
    errors = []

    # Delivery/archive: use rtype (receipt_type OR module) — legacy receipts identify via module only.
    # Verifier/executor: use explicit receipt_type only — legacy receipts with module:"verifier" but
    # no receipt_type field must not be promoted to the strict schema they can't satisfy.
    explicit_type = data.get("receipt_type")
    if rtype in ("delivery", "archive"):
        required = DELIVERY_REQUIRED
    elif explicit_type == "verifier":
        required = BASE_REQUIRED | VERIFIER_REQUIRED
    elif explicit_type == "executor":
        required = BASE_REQUIRED | EXECUTOR_REQUIRED
    else:
        required = BASE_REQUIRED.copy()

    for field in sorted(required):
        if field not in data:
            # Back-compat alias: legacy receipts emit 'confidence_score' or 'score'
            # in place of 'confidence'. Accept with a warning rather than reject.
            if field == "confidence" and ("confidence_score" in data or "score" in data):
                legacy_key = "confidence_score" if "confidence_score" in data else "score"
                print(f"WARN [{rtype}] {os.path.basename(path)}: legacy '{legacy_key}' accepted in lieu of 'confidence' (deprecated; rewrite to emit 'confidence')")
                continue
            msg = f"missing required field: '{field}'"
            if lenient and (
                msg.startswith("missing required field: 'not_tested'")
                or msg.startswith("missing required field: 'status'")
            ):
                print(f"WARN [{rtype}] {os.path.basename(path)}: {msg}")
            else:
                errors.append(msg)

    status = data.get("status")
    allowed = WAVE_STATUSES if rtype == "wave" else VALID_STATUSES
    status_msg = f"status '{status}' not in {sorted(allowed)}"
    if status not in allowed:
        if lenient and (status is None or status_msg.startswith("status 'None' not in")):
            print(f"WARN [{rtype}] {os.path.basename(path)}: {status_msg}")
        else:
            errors.append(status_msg)

    if status in ("FAIL", "PARTIAL") and "failure_reason" not in data:
        errors.append("status FAIL/PARTIAL requires 'failure_reason'")

    # Type-specific conditional validation. Gate on each field's key presence independently:
    # new builder receipts always emit revision_guidance/escalation_reason (even as null),
    # so the key exists and we can enforce it. Legacy hand-authored receipts omit the key
    # entirely and pass base schema only.
    if rtype == "grader":
        verdict = data.get("verdict")
        if verdict == "REVISE" and "revision_guidance" in data and not data.get("revision_guidance"):
            errors.append("verdict REVISE requires 'revision_guidance'")
        if verdict == "ESCALATE" and "escalation_reason" in data and not data.get("escalation_reason"):
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
    parser.add_argument("--status", choices=["PASS", "FAIL", "PARTIAL", "COMPLETE", "BLOCKED"])
    parser.add_argument("--wave", type=int, default=1)
    parser.add_argument("--wave-of", type=int)
    parser.add_argument("--not-tested", nargs="*", metavar="ITEM")
    parser.add_argument("--options-path", metavar="PATH", dest="options_path",
                        help="Brainstorm: path to the options-<timestamp>.md file.")
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

    # Ground-specific args
    parser.add_argument("--task-card-path", metavar="PATH", help="Ground: path to task-card.md.")
    parser.add_argument("--claims-total", type=int, metavar="N", help="Ground: total number of claims evaluated.")
    parser.add_argument("--verified-claims", nargs="*", metavar="CLAIM", help="Ground: list of verified claims.")
    parser.add_argument("--unverified-claims", nargs="*", metavar="CLAIM", help="Ground: list of unverified claims.")
    parser.add_argument("--assumed-claims", nargs="*", metavar="CLAIM", help="Ground: list of assumed claims.")
    parser.add_argument("--missing-claims", nargs="*", metavar="CLAIM", help="Ground: list of missing claims.")
    parser.add_argument("--block-reason", metavar="TEXT", help="Ground: reason for BLOCK status.")

    # Runtime-probe-specific args
    parser.add_argument("--overrides-applied", action="store_true", help="Runtime-probe: whether overrides were applied.")
    parser.add_argument("--capabilities-detected", nargs="*", metavar="CAP", help="Runtime-probe: detected capabilities list.")
    parser.add_argument("--capabilities-unavailable", nargs="*", metavar="CAP", help="Runtime-probe: unavailable capabilities list.")

    # Platform-activation-specific args
    parser.add_argument(
        "--platform-id",
        choices=["web", "mobile", "cli", "api-service", "library", "ai-agent", "desktop", "extension", "game", "iot", "data-pipeline"],
        help="Platform-activation: platform identifier.",
    )
    parser.add_argument("--spec-templates-loaded", nargs="*", metavar="TEMPLATE", help="Platform-activation: spec templates loaded.")
    parser.add_argument("--security-controls-loaded", nargs="*", metavar="CONTROL", help="Platform-activation: security controls loaded.")
    parser.add_argument("--gateway-refs-loaded", nargs="*", metavar="REF", help="Platform-activation: gateway references loaded.")
    parser.add_argument("--language-modules-activated", nargs="*", metavar="MODULE", help="Platform-activation: language modules activated.")

    # Gateway-spec and gateway-verdict shared args
    parser.add_argument(
        "--gateway-id",
        choices=["aesthetic", "design", "security", "ai", "engineering", "experience"],
        help="Gateway-spec/verdict: gateway identifier.",
    )
    parser.add_argument("--gates-declared", nargs="*", metavar="GATE", help="Gateway-spec: list of declared gates.")
    parser.add_argument("--blocking-gates", nargs="*", metavar="GATE", help="Gateway-spec: list of blocking gates.")

    # Gateway-verdict-specific args
    parser.add_argument(
        "--gateway-verdict",
        choices=["PASS", "FLAG", "BLOCK"],
        help="Gateway-verdict: verdict (PASS/FLAG/BLOCK). Distinct from --verdict which is for grader/reviewer.",
    )
    parser.add_argument("--violations", nargs="*", metavar="VIOLATION", help="Gateway-verdict: list of violations.")
    parser.add_argument("--attestation-required", action="store_true", help="Gateway-verdict/audit: attestation required flag.")

    # Memory-write-specific args
    parser.add_argument("--drawer-id", metavar="ID", help="Memory-write/forget: drawer identifier.")
    parser.add_argument(
        "--memory-operation",
        choices=["write", "update", "read", "transition"],
        help="Memory-write: operation type.",
    )
    parser.add_argument("--topic", metavar="TEXT", help="Memory-write: topic of the drawer.")
    parser.add_argument("--wing", metavar="TEXT", help="Memory-write: wing of the memory palace.")
    parser.add_argument("--room", metavar="TEXT", help="Memory-write: room within the wing.")
    parser.add_argument("--staleness-before", metavar="STATE", help="Memory-write: staleness state before operation.")
    parser.add_argument("--staleness-after", metavar="STATE", help="Memory-write: staleness state after operation.")
    parser.add_argument("--backend", metavar="TEXT", help="Memory-write: backend identifier (e.g. memory/chromadb).")
    parser.add_argument("--provenance-not-notified", action="store_true", help="Memory-write: provenance was NOT notified (inverts default notified=True).")

    # Memory-search-specific args
    parser.add_argument("--results-returned", type=int, metavar="N", help="Memory-search: number of results returned.")
    parser.add_argument("--max-results", type=int, metavar="N", help="Memory-search: maximum results requested.")
    parser.add_argument("--staleness-filters", nargs="*", metavar="FILTER", help="Memory-search: staleness filters applied.")
    parser.add_argument("--dedup-applied", action="store_true", help="Memory-search: deduplication was applied.")

    # Forget-specific args
    parser.add_argument(
        "--deletion-type",
        choices=["single", "bulk-expired", "compliance"],
        help="Forget: deletion type.",
    )
    parser.add_argument("--drawer-ids-deleted", nargs="*", metavar="ID", help="Forget: list of drawer IDs deleted.")
    parser.add_argument("--provenance-record-path", metavar="PATH", help="Forget: path to provenance deletion record.")
    parser.add_argument("--entity-graph-not-notified", action="store_true", help="Forget: entity graph was NOT notified (inverts default notified=True).")

    # Inference-guard-specific args
    parser.add_argument("--activated", action="store_true", help="Inference-guard: whether inference guard was activated.")
    parser.add_argument(
        "--tier-applied",
        choices=["light", "standard", "heavy"],
        help="Inference-guard: tier applied.",
    )
    parser.add_argument("--triggers-detected", nargs="*", metavar="TRIGGER", help="Inference-guard: list of triggers detected.")
    parser.add_argument("--transforms-applied", nargs="*", metavar="TRANSFORM", help="Inference-guard: list of transforms applied.")
    parser.add_argument("--non-activation-reason", metavar="TEXT", help="Inference-guard: reason for non-activation.")

    # Model-router-specific args
    parser.add_argument("--selected-capability", metavar="TEXT", help="Model-router: selected capability descriptor.")
    parser.add_argument("--task-shape", metavar="TEXT", help="Model-router: task shape classification.")
    parser.add_argument("--fallback-capability", metavar="TEXT", help="Model-router: fallback capability descriptor.")
    parser.add_argument("--ensemble-triggered", action="store_true", help="Model-router: whether ensemble was triggered.")
    parser.add_argument("--ensemble-trigger-reason", metavar="TEXT", help="Model-router: reason ensemble was triggered.")
    parser.add_argument("--verification-mode", metavar="TEXT", help="Model-router: verification mode selected.")
    parser.add_argument("--inference-guard-eligible", action="store_true", help="Model-router: whether task is inference-guard eligible.")

    # Forge/augment/blueprint shared args
    parser.add_argument("--attested-by", metavar="TEXT", help="Forge/blueprint: name of the attesting human.")
    parser.add_argument("--attestation-statement", metavar="TEXT", help="Forge: free-text attestation statement.")
    parser.add_argument(
        "--promotions-json",
        type=json.loads,
        metavar="JSON",
        help="Forge: JSON array of promotion objects.",
    )
    parser.add_argument("--forge-archive-path", metavar="PATH", help="Forge: archive provenance path.")
    parser.add_argument("--blueprint-id", metavar="TEXT", help="Augment/blueprint/benchmark: blueprint identifier.")
    parser.add_argument("--affected-module", metavar="TEXT", help="Augment/blueprint: module being augmented.")
    parser.add_argument(
        "--change-type",
        choices=["AUGMENT", "NEW"],
        help="Augment/blueprint: change classification.",
    )
    parser.add_argument("--augment-output-path", metavar="PATH", help="Augment: output directory path.")
    parser.add_argument("--structural-check-failed", action="store_true", help="Augment: structural check did NOT pass (inverts default passed=True).")
    parser.add_argument("--placeholders-remaining", type=int, metavar="N", help="Augment: number of unfilled placeholders.")

    # Blueprint-specific args
    parser.add_argument("--attestation-not-confirmed", action="store_true", help="Blueprint: attestation was NOT confirmed (inverts default confirmed=True).")
    parser.add_argument("--attested-at", metavar="ISO8601", help="Blueprint: ISO-8601 timestamp of attestation.")

    # Benchmark-specific args
    parser.add_argument("--metric-name", metavar="TEXT", help="Benchmark: metric being measured.")
    parser.add_argument("--held-out-cases", type=int, metavar="N", help="Benchmark: number of held-out test cases.")
    parser.add_argument("--held-out-value", type=float, metavar="FLOAT", help="Benchmark: measured value on held-out set.")
    parser.add_argument("--threshold", type=float, metavar="FLOAT", help="Benchmark: pass/fail threshold.")
    parser.add_argument("--fixture-set", metavar="PATH", help="Benchmark: fixture set directory path.")

    # Experiment-specific args
    parser.add_argument("--experiment-hypothesis", metavar="TEXT", help="Experiment: hypothesis statement (use 'We believe [change] will [metric] because [reasoning]' format).")
    parser.add_argument("--experiment-variants", nargs="*", metavar="VARIANT", help="Experiment: skill versions or paths tested (repeatable).")
    parser.add_argument("--experiment-primary-metric", metavar="TEXT", help="Experiment: primary metric being measured.")
    parser.add_argument("--experiment-winner", metavar="TEXT", help="Experiment: which variant won (or 'inconclusive').")
    parser.add_argument("--experiment-outcome", choices=["CONFIRMED", "REFUTED", "INCONCLUSIVE"], help="Experiment: hypothesis outcome classification.")
    parser.add_argument("--experiment-learnings", metavar="TEXT", help="Experiment: what was learned regardless of outcome.")

    # Synth-specific args
    parser.add_argument("--instinct-observation-id", metavar="TEXT", help="Synth: instinct observation identifier.")
    parser.add_argument("--candidate-id", metavar="TEXT", help="Synth: candidate identifier.")
    parser.add_argument("--candidate-path", metavar="PATH", help="Synth: path to candidate JSON file.")
    parser.add_argument("--pattern-occurrence-count", type=int, metavar="N", help="Synth: number of times the pattern was observed.")

    # Guard-specific args
    parser.add_argument(
        "--overall",
        choices=["PASS", "FAIL"],
        help="Guard: overall gate result.",
    )
    parser.add_argument(
        "--layer-results-json",
        type=json.loads,
        metavar="JSON",
        help="Guard: JSON object of per-layer results e.g. '{\"layer1_schema\": \"PASS\"}'.",
    )
    parser.add_argument("--unauthorized-files", nargs="*", metavar="PATH", help="Guard/wave: list of unauthorized file paths.")

    # Wave-specific args
    parser.add_argument("--wave-changes", nargs="*", metavar="CHANGE", help="Wave: list of changes made in this wave.")
    parser.add_argument("--verification-method", metavar="TEXT", help="Wave: verification method used.")
    parser.add_argument("--verification-command", metavar="TEXT", help="Wave: verification command run.")
    parser.add_argument("--ac-covered", nargs="*", metavar="AC", help="Wave: acceptance criteria covered by this wave.")

    # Memory-mine-specific args
    parser.add_argument("--schema-version", type=int, metavar="N", help="Memory-mine: current schema version.")
    parser.add_argument("--drawers-analyzed", type=int, metavar="N", help="Memory-mine: number of drawers analyzed.")
    parser.add_argument("--drawers-skipped", type=int, metavar="N", help="Memory-mine: number of drawers skipped due to schema mismatch.")
    parser.add_argument("--gaps-found", type=int, metavar="N", help="Memory-mine: number of gaps found.")
    parser.add_argument("--clusters-found", type=int, metavar="N", help="Memory-mine: number of clusters found.")
    parser.add_argument("--patterns-found", type=int, metavar="N", help="Memory-mine: number of patterns found.")
    parser.add_argument("--dedup-candidates", type=int, metavar="N", help="Memory-mine: number of dedup candidates found.")
    parser.add_argument("--staleness-critical", type=int, metavar="N", help="Memory-mine: number of critically stale drawers.")
    parser.add_argument("--mine-output-dir", metavar="PATH", help="Memory-mine: output directory path.")

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
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="Lenient validation: treat missing not_tested/status as warnings, not errors. Use for pre-schema legacy receipts. Only meaningful with --validate.",
    )

    # Normalize argv: --validate --lenient PATH → --validate PATH --lenient
    # argparse refuses to use a --flag as the value for an optional argument,
    # so we pre-process sys.argv to move the path after --lenient.
    argv = sys.argv[1:]
    if "--validate" in argv and "--lenient" in argv:
        vi = argv.index("--validate")
        li = argv.index("--lenient")
        # If --lenient immediately follows --validate (i.e. no path between them),
        # pull the path from right after --lenient and insert it after --validate.
        if li == vi + 1 and li + 1 < len(argv) and not argv[li + 1].startswith("--"):
            path_val = argv[li + 1]
            new_argv = argv[:vi + 1] + [path_val] + argv[li:li + 1] + argv[li + 2:]
            argv = new_argv
    args = parser.parse_args(argv)

    # Validate mode
    if args.validate:
        ok = validate_receipt(args.validate, lenient=getattr(args, 'lenient', False))
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
