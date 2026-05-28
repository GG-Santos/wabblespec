"""Regression tests for receipt-writer.py — locks in the foundation-hardening fixes (H1, H4)."""
from __future__ import annotations

import json
import tempfile

import pytest

# Every receipt type exposed via --type. Used to assert H1 (confidence) holds for all.
ALL_TYPES = [
    "verifier", "executor", "recipe", "specify", "decompose", "scaffold",
    "package", "release", "monitor", "deploy", "adversary", "grader", "nexus",
    "brainstorm", "enhance", "sharpen", "audit", "ref-eval", "ref-comp", "ref-plan",
    "propose", "reviewer", "scopeframe", "guard",
]


def _emit(run, rtype, *extra):
    cp = run("receipt-writer.py", "--type", rtype, "--task-id", "t",
             "--session-id", "s", "--status", "PASS", "--confidence", "0.9",
             "--out", "-", *extra)
    assert cp.returncode == 0, f"{rtype} failed: {cp.stderr}"
    return json.loads(cp.stdout)


@pytest.mark.parametrize("rtype", ALL_TYPES)
def test_every_builder_emits_confidence(run, rtype):
    """H1: every builder emits a top-level numeric confidence in [0,1]."""
    d = _emit(run, rtype)
    c = d.get("confidence")
    assert isinstance(c, (int, float)), f"{rtype} confidence not numeric: {c!r}"
    assert 0.0 <= c <= 1.0, f"{rtype} confidence out of range: {c}"


def test_h4_missing_builders_are_registered(run):
    """H4: propose/reviewer/scopeframe/guard are CLI-accessible."""
    for rtype in ("propose", "reviewer", "scopeframe", "guard"):
        d = _emit(run, rtype)
        assert (d.get("receipt_type") or d.get("module")), f"{rtype} produced no identity field"


def test_h4_brainstorm_options_path_flag(run):
    """H4: --options-path populates brainstorm options_path."""
    d = _emit(run, "brainstorm", "--options-path", "X.md")
    assert d.get("options_path") == "X.md"
    # And it must not leak into unrelated builders.
    r = _emit(run, "recipe")
    assert "options_path" not in r


def _validate(run, payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(payload, f)
        path = f.name
    return run("receipt-writer.py", "--validate", path)


def test_h1_validate_requires_confidence(run):
    """H1: a receipt with no confidence and no legacy alias FAILS validation."""
    cp = _validate(run, {"receipt_type": "t", "module": "t", "status": "PASS", "not_tested": []})
    assert cp.returncode != 0
    assert "confidence" in (cp.stdout + cp.stderr).lower()


def test_h1_validate_accepts_legacy_confidence_score(run):
    """H1 back-compat: legacy confidence_score is accepted (with a warning)."""
    cp = _validate(run, {"receipt_type": "t", "module": "t", "status": "PASS",
                         "not_tested": [], "confidence_score": 0.9})
    assert cp.returncode == 0
    assert "PASS" in cp.stdout
