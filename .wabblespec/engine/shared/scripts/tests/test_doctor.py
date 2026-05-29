"""Tests for wabblespec-doctor.py — the read-only drift detector."""
from __future__ import annotations

import json


def test_doctor_all_runs_and_enumerates(run):
    """--all exits 0 and enumerates the full check set (>= 28)."""
    cp = run("wabblespec-doctor.py", "--all", "--format", "json")
    assert cp.returncode == 0, cp.stderr
    checks = json.loads(cp.stdout)["checks"]
    assert len(checks) >= 28, f"expected >=28 checks, got {len(checks)}"
    # Every check carries the required fields.
    for c in checks:
        assert {"id", "severity", "status"} <= set(c), c


def test_doctor_self_test_passes(run):
    """--self-test discriminates good vs malformed fixtures."""
    cp = run("wabblespec-doctor.py", "--self-test")
    assert cp.returncode == 0, cp.stdout + cp.stderr


def test_doctor_critical_gate_clean(run):
    """Post-hardening, all critical checks pass (gate exits 0)."""
    cp = run("wabblespec-doctor.py", "--severity", "critical")
    assert cp.returncode == 0, cp.stdout


def test_doctor_no_critical_or_high_failures(run):
    """The foundation's hard guarantees hold: no critical/high check FAILs.
    (D1 receipt-write delegation is a tracked medium-tier gap being driven down.)"""
    cp = run("wabblespec-doctor.py", "--all", "--format", "json")
    checks = json.loads(cp.stdout)["checks"]
    bad = [c["id"] for c in checks if c["status"] != "PASS" and c["severity"] in ("critical", "high")]
    assert not bad, f"critical/high failures: {bad}"


def test_doctor_delegation_check_present(run):
    """D1 delegation check is registered (tracks the receipt-writer adoption gap)."""
    cp = run("wabblespec-doctor.py", "--all", "--format", "json")
    by_id = {c["id"]: c for c in json.loads(cp.stdout)["checks"]}
    assert "D1" in by_id, "D1 delegation check missing"
    assert by_id["D1"]["severity"] == "medium"
