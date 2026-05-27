# Deps — Acceptance Criteria

## BLOCK: absent dependency manifest

Given no recognized package manifest (package.json, requirements.txt, Cargo.toml, go.mod, pom.xml, etc.) is found,
When Deps is invoked,
Then Deps surfaces: "Deps requires a dependency manifest. No recognized manifest found in project root."
Then Deps does not infer dependencies from source code imports alone.
Then no receipt is written.

## Happy path: manifest present, lock file present

Given a package manifest and lock file are present,
When Deps runs,
Then all direct and transitive dependencies are discovered and `deps_scanned` is recorded.
Then each dependency is assessed across four dimensions: vulnerability, age, license, supply chain.
Then an SBOM is written to `.wabblespec/deps/sbom-<timestamp>.json`.
Then a deps receipt is written to `.wabblespec/receipts/deps-receipt-<timestamp>.json`.

## Lock file absent: flag but continue

Given a manifest exists but no lock file is present,
When Deps runs,
Then Deps flags: "No lock file found. Dependency versions are non-deterministic. Commit a lock file before release."
Then Deps continues with the manifest version information.
Then the receipt notes the lock file absence.
Then the run is not blocked.

## Risk tier classification

Given a dependency has a known CVE with CVSS >= 9.0,
Then that dependency is classified as CRITICAL in the risk summary.
Then `receipt.status` is FAIL.

Given a dependency has a CVSS score of 7.0–8.9,
Then that dependency is classified as HIGH.
Then `receipt.status` is PARTIAL.

Given all dependencies have CVSS < 4.0 and no other flags,
Then `receipt.status` is PASS.

## Audit tool unavailable

Given the platform audit tool (npm audit / cargo audit / pip-audit) is not available,
When Deps runs,
Then Deps logs: "Audit tool unavailable — CVE check skipped."
Then the warning is surfaced in the receipt.
Then Deps does not fabricate CVE results.

## Absent rules files: fallback

Given `rules/risk-tiers.md` is missing,
When Deps runs,
Then Deps applies SKILL.md risk tier defaults.
Then the receipt logs: "risk-tiers.md missing — using SKILL.md defaults."

## Receipt fields

Given any successful Deps run,
Then the receipt contains: `deps_scanned`, `risk_summary` (with critical/high/medium/low/unknown counts), `outdated_count`, `license_violations`, `sbom_path`, `supply_chain_flags`.
Then `sbom_path` matches the path of the written SBOM file.
