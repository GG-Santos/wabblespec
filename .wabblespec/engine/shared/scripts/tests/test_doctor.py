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


def test_doctor_reports_all_green_now(run):
    """Regression guard: the whole foundation is currently clean (0 FAIL)."""
    cp = run("wabblespec-doctor.py", "--all", "--format", "json")
    checks = json.loads(cp.stdout)["checks"]
    fails = [c["id"] for c in checks if c["status"] != "PASS"]
    assert not fails, f"doctor reports failures: {fails}"
