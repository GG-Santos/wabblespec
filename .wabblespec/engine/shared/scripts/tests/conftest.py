"""Shared fixtures/helpers for shared-scripts tests.

These scripts are CLI delegation tools, so tests invoke them as subprocesses
(testing the real user-facing contract) rather than importing the hyphenated
module names.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

# tests/ -> scripts/ -> shared/ -> engine/ -> .wabblespec/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[5]


def run_script(name: str, *args: str) -> subprocess.CompletedProcess:
    """Run a shared script as a subprocess from the repo root. Returns CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / name), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )


@pytest.fixture
def run():
    return run_script


@pytest.fixture
def scripts_dir():
    return SCRIPTS_DIR


@pytest.fixture
def repo_root():
    return REPO_ROOT
