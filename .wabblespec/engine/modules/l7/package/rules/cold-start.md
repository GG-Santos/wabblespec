# Cold-Start Behavior — Package

Defines what Package does when its build outputs or signing configuration are absent.

## Absent: build output

Condition: Package invoked but no build artifact exists.
Detection: Expected build output directory (dist/, build/, target/, out/) is absent or empty.
Action: BLOCK Package. Surface: "Package requires a successful build output. Run build step first."
Do NOT: Package source files instead of build output.

## Absent: signing configuration

Condition: Package is for a distributed artifact (desktop app, binary release) but no signing key or certificate is configured.
Detection: `rules/signing-policy.md` check or signing tool config absent.
Action: FLAG (for development builds) or BLOCK (for release builds). Surface: "Release package without signing configuration. Configure code signing before distributing."

## Absent: signing-policy.md

Condition: `rules/signing-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md signing rules. Log: "signing-policy.md missing — using SKILL.md defaults."

## Absent: package manifest

Condition: No `package.json`, `Cargo.toml`, `pyproject.toml`, or equivalent.
Detection: Manifest file absent.
Action: BLOCK Package. Surface: "No package manifest found. Package requires a manifest declaring name, version, and dependencies."

## Absent: version declaration

Condition: Manifest exists but version field is absent or `0.0.0`.
Detection: Version read returns null, absent, or `0.0.0`.
Action: FLAG: "Package version not declared or is placeholder (0.0.0). Declare version before publishing."

## Default state on cold start

| Field | Default |
|---|---|
| `signing` | Required for release packages; optional for development packages |
| `output_format` | Detected from manifest type (npm / crate / wheel / binary) |
| `version_source` | Manifest file preferred; VERSION file fallback |
| `publish_gate` | Manual — do not auto-publish without explicit user confirmation |
| `checksum` | SHA-256 generated for all release packages |
