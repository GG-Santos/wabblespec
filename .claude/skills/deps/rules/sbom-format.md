# SBOM Format

Deps writes a Software Bill of Materials (SBOM) for every scan. The SBOM is the auditable record of what was found.

## Format

SBOM is JSON, written to `.wabblespec/deps/sbom-<timestamp>.json`. Schema: `schemas/sbom.schema.json`.

Top-level structure:

```json
{
  "sbom_version": "1.0",
  "generated": "<ISO-8601 timestamp>",
  "project": "<project name from framework.yaml>",
  "scan_scope": "<directory or manifest path scanned>",
  "total_deps": 0,
  "components": []
}
```

Each entry in `components`:

```json
{
  "name": "package-name",
  "version": "1.2.3",
  "resolved_version": "1.2.3",
  "ecosystem": "npm | pypi | cargo | go | maven | gem | nuget",
  "manifest_path": "package.json",
  "dependency_type": "direct | transitive",
  "depth": 1,
  "license": "MIT",
  "license_tier": "COMPATIBLE | REVIEW_REQUIRED | INCOMPATIBLE | UNKNOWN",
  "currency": "CURRENT | OUTDATED | CRITICAL_OUTDATED | UNKNOWN",
  "security": "CLEAN | ADVISORY | VULNERABLE | CRITICAL",
  "activity": "ACTIVE | SLOW | UNMAINTAINED | ARCHIVED",
  "risk_tier": "LOW | MEDIUM | HIGH | CRITICAL",
  "cves": [],
  "supply_chain_flags": []
}
```

## CVE entry format

```json
{
  "cve_id": "CVE-2024-12345",
  "cvss": 8.1,
  "severity": "HIGH",
  "fixed_in": "1.2.4",
  "description": "one-line summary"
}
```

## Scan scope

Deps scans these manifest files when present:
- `package.json` (npm/yarn/pnpm)
- `requirements.txt`, `pyproject.toml`, `Pipfile.lock` (Python)
- `Cargo.toml`, `Cargo.lock` (Rust)
- `go.mod`, `go.sum` (Go)
- `pom.xml`, `build.gradle` (JVM)
- `Gemfile.lock` (Ruby)
- `*.csproj`, `packages.config` (NuGet)

If no manifest is found: `deps_scanned: 0`, note `SCAN_SCOPE_EMPTY` in receipt.

## Transitive depth

Deps resolves transitive dependencies to depth 3 by default. Beyond depth 3, record existence but do not resolve further (depth explosion risk). Flag any transitive chain exceeding depth 5 as a supply chain concern.
