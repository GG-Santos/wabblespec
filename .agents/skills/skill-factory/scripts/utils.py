"""Shared utilities for skill-factory scripts."""

import re
from pathlib import Path


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content


def find_project_root() -> Path:
    """Find the nearest runtime project root, falling back to cwd.

    Runtime adapters may use this to place temporary command files or resolve
    workspace-relative paths. The generic fallback is the current directory.
    """
    current = Path.cwd()
    markers = (".git", "AGENTS.md", "SKILL.md", "pyproject.toml")
    for parent in [current, *current.parents]:
        if any((parent / marker).exists() for marker in markers):
            return parent
    return current


# Patterns that look like API keys / secrets.
# Mirrors lint_prompts' secret-patterns rule so the lint scanner and the
# log redactor agree on what counts as a secret. False positives are
# acceptable here (they cost a [REDACTED] in a log); false negatives
# cost real secret leakage and are not.
_SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),              # sk-prefixed API keys
    re.compile(r"sk-ant-[a-zA-Z0-9_-]{20,}"),        # vendor-specific sk-ant keys
    re.compile(r"AIza[a-zA-Z0-9_-]{30,}"),           # cloud API keys
    re.compile(r"key-[a-zA-Z0-9]{20,}"),             # generic "key-" prefixed
    re.compile(r"\bgh[pso]_[A-Za-z0-9]{16,}\b"),     # GitHub (ghp_, gho_, ghs_)
    re.compile(r"\bxox[bpars]-[A-Za-z0-9-]{10,}\b"), # Slack
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),             # AWS access key ID
    re.compile(r"\baws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?"),  # AWS secret
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),  # PEM private keys
    re.compile(r"\bsk_live_[A-Za-z0-9]{24,}\b"),     # Stripe live secret
    re.compile(r"\brk_live_[A-Za-z0-9]{24,}\b"),     # Stripe restricted live
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+"),  # JWT
    # Generic high-entropy assignment: capture obvious "FOO_TOKEN = <40-char base64ish>"
    re.compile(r"(?i)\b(api[-_]?key|access[-_]?token|secret[-_]?(?:key|token)|auth[-_]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_+/=-]{24,}['\"]?"),
]


def redact_secrets(text: str) -> str:
    """Replace API key patterns in text with [REDACTED].

    Used to sanitize log output before writing to disk.
    """
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text
