# Health Dimensions

Deps evaluates dependencies across five health dimensions. Every dependency in scope gets a health score on each.

## Dimension 1 — Currency

Is the dependency at or near its latest release?

| State | Condition |
|---|---|
| CURRENT | Within 2 minor versions of latest release |
| OUTDATED | 3–9 minor versions behind, OR 1 major version behind |
| CRITICAL_OUTDATED | 2+ major versions behind, OR past end-of-life date |
| UNKNOWN | Cannot determine latest version (private registry, no metadata) |

Record `outdated_count` in receipt for OUTDATED + CRITICAL_OUTDATED combined.

---

## Dimension 2 — Security

Does the dependency have known CVEs?

| State | Condition |
|---|---|
| CLEAN | No CVEs in NIST NVD or OSV for installed version |
| ADVISORY | CVE exists but CVSS < 7.0 (medium/low severity) |
| VULNERABLE | CVSS 7.0–8.9 (high severity) |
| CRITICAL | CVSS ≥ 9.0 or actively exploited |

Feed into `risk_summary` fields in receipt: `critical`, `high`, `medium`, `low`, `unknown`.

---

## Dimension 3 — License

Is the dependency's license compatible with the project's license?

| State | Condition |
|---|---|
| COMPATIBLE | Permissive (MIT, Apache, BSD, ISC) or same license family |
| REVIEW_REQUIRED | Weak copyleft (LGPL, MPL) — compatible in most cases, review needed |
| INCOMPATIBLE | Strong copyleft (GPL, AGPL) in a closed-source project |
| UNKNOWN | No license declared |

Record `license_violations: N` for INCOMPATIBLE count.

---

## Dimension 4 — Activity

Is the dependency actively maintained?

| State | Condition |
|---|---|
| ACTIVE | Commit or release in last 6 months |
| SLOW | Last activity 6–18 months ago |
| UNMAINTAINED | Last activity > 18 months ago, no stated maintenance mode |
| ARCHIVED | Explicitly archived or deprecated by maintainer |

ARCHIVED and UNMAINTAINED dependencies are supply chain risk regardless of current vulnerability status.

---

## Dimension 5 — Supply chain integrity

Does the dependency show signs of compromise or typosquatting?

Flags raised when:
- Package name is a close variant of a popular package (typosquatting pattern)
- Maintainer account changed recently before a release
- Published version differs from repository source
- Dependency tree depth > 5 levels (transitive dependency explosion)

Record flagged packages in `supply_chain_flags` array with reason.
