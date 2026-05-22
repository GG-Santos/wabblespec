"""Shared helpers for generators (no upward deps to avoid circular imports)."""

from __future__ import annotations

import re


def _short_description(description: str, max_length: int = 180) -> str:
    """Return a compact single-line description for manifests."""
    compact = " ".join(description.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."

def _python_identifier(skill_name: str) -> str:
    """Convert a kebab-case skill name to a valid Python identifier."""
    identifier = skill_name.replace("-", "_")
    if identifier[0].isdigit():
        identifier = f"skill_{identifier}"
    return identifier
