"""Structured logging helpers with secret redaction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.utils import redact_secrets


def write_redacted_json_log(log_dir: Path | None, filename: str, payload: dict[str, Any]) -> Path | None:
    """Write a JSON log after redacting known secret patterns."""
    if log_dir is None:
        return None

    log_dir.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, indent=2, sort_keys=True)
    redacted = redact_secrets(raw)
    enriched = {
        **payload,
        "redaction_applied": redacted != raw,
    }
    final_raw = json.dumps(enriched, indent=2, sort_keys=True)
    final_redacted = redact_secrets(final_raw)

    path = log_dir / filename
    path.write_text(final_redacted, encoding="utf-8")
    return path


def write_redacted_json_artifact(log_dir: Path | None, filename: str, payload: Any) -> Path | None:
    """Write any JSON-serializable artifact after secret redaction."""
    if log_dir is None:
        return None

    log_dir.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, indent=2, sort_keys=True)
    path = log_dir / filename
    path.write_text(redact_secrets(raw), encoding="utf-8")
    return path
