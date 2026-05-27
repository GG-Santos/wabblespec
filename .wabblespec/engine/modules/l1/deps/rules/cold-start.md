# Cold-Start Behavior — Deps

Defines what Deps does when its dependency manifests or SBOM artifacts are absent.

## Absent: dependency manifest

Condition: No package.json, requirements.txt, Cargo.toml, go.mod, pom.xml, or equivalent found.
Detection: Manifest scan returns no recognized file.
Action: Surface: "Deps requires a dependency manifest. No recognized manifest found in project root."
Do NOT: Infer dependencies from source code imports alone.

## Absent: lock file

Condition: Manifest exists but no lock file (package-lock.json, yarn.lock, Cargo.lock, poetry.lock, go.sum).
Detection: Lock file absent.
Action: FLAG: "No lock file found. Dependency versions are non-deterministic. Commit a lock file before release."
Do NOT: Block Deps run. Continue with manifest; note lock file absence in receipt.

## Absent: sbom-format.md

Condition: `rules/sbom-format.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md SBOM rules. Log: "sbom-format.md missing — using SKILL.md defaults."

## Absent: risk-tiers.md

Condition: `rules/risk-tiers.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md risk tier defaults. Log: "risk-tiers.md missing — using SKILL.md defaults."

## Absent: prior Deps receipt (for drift detection)

Condition: No prior `deps-receipt-<timestamp>.json`.
Detection: Receipt absent.
Action: Treat as first run. No prior SBOM to diff against. Flag any HIGH/CRITICAL CVEs found.

## Absent: audit tool

Condition: `npm audit` / `cargo audit` / `pip-audit` not available in environment.
Detection: Tool invocation returns command-not-found.
Action: Log: "Audit tool unavailable — CVE check skipped." Surface warning in receipt.
Do NOT: Fabricate CVE results. Report tool unavailability clearly.

## Default state on cold start

| Field | Default |
|---|---|
| `lock_file_present` | false — checked on run |
| `sbom_written` | false — written on first complete run |
| `critical_cve_count` | 0 (assumed; actual from audit) |
| `high_cve_count` | 0 (assumed; actual from audit) |
| `block_on` | CRITICAL CVEs — no deploy until resolved or waived |
| `flag_on` | HIGH CVEs — flagged with remediation timeline required |
