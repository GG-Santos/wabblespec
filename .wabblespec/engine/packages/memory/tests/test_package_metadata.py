from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_extract_extra_installs_document_transformers():
    pyproject = tomllib.loads((ROOT / "packages" / "memory" / "pyproject.toml").read_text())
    extras = pyproject["project"]["optional-dependencies"]
    extract = extras["extract"]

    assert any(dep.lower().startswith("markitdown") for dep in extract)
    assert any(dep.lower().startswith("striprtf") for dep in extract)
