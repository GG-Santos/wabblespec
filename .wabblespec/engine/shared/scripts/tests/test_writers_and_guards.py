"""Regression tests for archive.py (C3), task-card-writer.py (H3), guard-check.py,
and the L5 daemon path fix (#30)."""
from __future__ import annotations

import json


def test_c3_archive_wabble_sound_path(scripts_dir):
    """C3: archive.py must not contain the broken `_shared` path; must reference wabble-sound.py."""
    src = (scripts_dir / "archive.py").read_text(encoding="utf-8")
    assert '"_shared", "scripts", "wabble-sound.py"' not in src, "broken _shared path still present"
    assert "wabble-sound.py" in src, "wabble-sound.py reference was removed"
    assert (scripts_dir / "wabble-sound.py").exists(), "wabble-sound.py target missing"


def _task_card(run, *flags):
    return run("task-card-writer.py", "--session-id", "s", "--goal", "g.",
               "--target", "Framework", "--complexity", "Low",
               "--non-goal", "ng", "--assumption", "a",
               "--criterion", "AC1|x|g|w|t", "--out", "-", "--dry-run", *flags)


def test_h3_delta_class_flag_works(run):
    """H3: --delta-class is accepted and emits change_class."""
    cp = _task_card(run, "--delta-class", "ADDITIVE")
    assert cp.returncode == 0, cp.stderr
    assert "change_class" in cp.stdout and "ADDITIVE" in cp.stdout


def test_h3_change_class_flag_removed(run):
    """H3 (user's clean break): --change-class is no longer accepted."""
    cp = _task_card(run, "--change-class", "ADDITIVE")
    assert cp.returncode != 0, "--change-class should be rejected after the clean break"


def test_guard_authority_owned_vs_unowned(run):
    """guard-check authority: executor owns its wave receipts, not CLAUDE.md."""
    owned = run("guard-check.py", "authority", "--module", "executor",
                "--files", ".wabblespec/state/receipts/wave-1-receipt.json")
    assert "PASS" in owned.stdout and "FAIL" not in owned.stdout, owned.stdout

    unowned = run("guard-check.py", "authority", "--module", "executor",
                  "--files", "CLAUDE.md")
    assert "FAIL" in unowned.stdout, unowned.stdout


def test_finding30_entity_graph_finds_drawers(run):
    """#30: entity-graph.py reads state/memory/wings (not the legacy .wabblespec/memory path)."""
    cp = run("../../modules/l5/entity-graph/scripts/entity-graph.py", "--dry-run")
    out = cp.stdout + cp.stderr
    assert "No wings directory found" not in out, "entity-graph still using legacy memory path"
    assert "drawers processed" in out or "drawers" in out
