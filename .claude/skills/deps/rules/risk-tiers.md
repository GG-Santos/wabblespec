# Risk Tiers

Deps maps each dependency to one of four risk tiers. The tier determines the action required.

## Tier: CRITICAL

**Conditions (any one):**
- CVSS ≥ 9.0 CVE in installed version
- Dependency is ARCHIVED and used in a security-sensitive code path
- Supply chain flag: maintainer compromise or published version differs from source
- License INCOMPATIBLE in a production dependency

**Required action:** Block. Do not proceed with this dependency version in production code. Escalate to human immediately. Record in `risk_summary.critical`.

---

## Tier: HIGH

**Conditions (any one):**
- CVSS 7.0–8.9 CVE in installed version
- CRITICAL_OUTDATED (2+ major versions behind)
- UNMAINTAINED dependency in a critical code path (auth, crypto, parsing)
- Supply chain flag: typosquatting pattern

**Required action:** Flag in receipt. Recommend upgrade or replacement. Do not block execution but note that proceeding adds known risk. Record in `risk_summary.high`.

---

## Tier: MEDIUM

**Conditions (any one):**
- CVSS < 7.0 CVE (advisory)
- OUTDATED (3–9 minor versions behind)
- License REVIEW_REQUIRED
- SLOW maintenance (6–18 months inactive)

**Required action:** Note in SBOM. Recommend addressing before next release. Record in `risk_summary.medium`.

---

## Tier: LOW

**Conditions:**
- CURRENT version, CLEAN CVE status, COMPATIBLE license, ACTIVE maintenance
- Minor issues only (within 2 minor versions of latest, no CVEs)

**Required action:** Record in SBOM only. No action required. Record in `risk_summary.low`.

---

## Aggregation rule

A dependency's overall tier is its worst dimension. A dependency that is CURRENT and CLEAN but has an INCOMPATIBLE license is CRITICAL (license dimension).

Never average tiers. Worst wins.
