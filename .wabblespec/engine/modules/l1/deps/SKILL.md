---
name: deps
description: Dependency health audit. Scans for vulnerabilities, outdated packages, license issues, and supply chain risk. Produces SBOM. On-demand or pre-deployment gate.
---

# Deps

Dependencies are trusted code you did not write. Their security posture is your security posture. You scan every dependency, classify risk, flag violations, and produce a software bill of materials.

## What this skill does

Scans all project dependencies. Classifies risk per dimension (vulnerability, age, license, supply chain). Produces SBOM. Writes deps receipt.

## When to use

- Pre-deployment gate (any task touching dependencies)
- Explicit `/deps` command
- Security gateway routes dependency concern here
- Scheduled health audit

## Inputs

- Package manifests (package.json, requirements.txt, Cargo.toml, go.mod, pubspec.yaml, etc.)
- Lock files (preferred — exact version pinning)

## How to do it

### Step 1 — Discover all dependencies

Parse all package manifests and lock files. Count total dependencies (direct + transitive). Record `deps_scanned`.

### Step 2 — Assess each dimension

See rules/health-dimensions.md. For each dependency, check:

- **Vulnerability:** Known CVEs or advisories. Cross-reference against advisory databases if available.
- **Age:** How old is the version? Is a newer version available? Is the package maintained?
- **License:** Is the license compatible with this project's license? See rules/risk-tiers.md.
- **Supply chain:** Is the package still maintained? Published by a verified author? No recent ownership transfer?

### Step 3 — Classify risk per dependency

Per rules/risk-tiers.md:
- `CRITICAL`: Known vulnerability with CVSS ≥ 9.0, or license incompatibility that blocks distribution
- `HIGH`: CVSS 7.0–8.9, or abandoned package (no releases in 2+ years)
- `MEDIUM`: CVSS 4.0–6.9, or significantly outdated (major version behind)
- `LOW`: Minor version behind, low-severity advisory
- `UNKNOWN`: Unable to determine risk (private registry, no metadata)

### Step 4 — Produce SBOM

Write SBOM to `.wabblespec/deps/sbom-<timestamp>.json`. Format per rules/sbom-format.md (SPDX-compatible subset).

### Step 5 — Write receipt

## Output contract

**deps-receipt.json** (`.wabblespec/state/receipts/deps-receipt-<timestamp>.json`):

```json
{
  "deps_scanned": "integer",
  "risk_summary": {
    "critical": "integer",
    "high": "integer",
    "medium": "integer",
    "low": "integer",
    "unknown": "integer"
  },
  "outdated_count": "integer",
  "license_violations": "integer",
  "sbom_path": ".wabblespec/deps/sbom-<timestamp>.json",
  "supply_chain_flags": ["array of {package, reason} objects"]
}
```

Receipt status = FAIL if `risk_summary.critical > 0`. PARTIAL if `risk_summary.high > 0`. PASS otherwise.
