# Jurisdiction Defaults

Rules for jurisdiction selection and template application.

## Default jurisdiction

When no jurisdiction is declared: apply GDPR. GDPR is the most comprehensive and is generally a compliant baseline for other jurisdictions.

## Jurisdiction selection logic

| Declared jurisdiction | Templates applied | Notes |
|---|---|---|
| `gdpr` | GDPR privacy policy, GDPR data processing agreement | EU/EEA focused |
| `ccpa` | CCPA privacy notice, Do Not Sell/Share disclosure | California residents |
| `pipeda` | PIPEDA privacy policy | Canada focused |
| `multi` | All three jurisdictions, layered | Most comprehensive; recommended for global products |

## GDPR (General Data Protection Regulation)

Applies to: any product processing personal data of EU/EEA residents, regardless of where the business is located.

Required documents: Privacy Policy, Cookies Policy (if cookies used), Data Processing Agreement (if third-party processors exist).

Required clauses: legal basis for processing, data subject rights (access, deletion, portability, objection, restriction), data retention periods, international transfer safeguards, DPO contact (if applicable).

## CCPA (California Consumer Privacy Act)

Applies to: for-profit businesses meeting any of: gross revenue > $25M/year; annual purchase/sale of ≥100,000 consumer records; ≥50% revenue from selling personal information.

Required clauses: categories of personal information collected, purposes of use, third-party disclosures, Do Not Sell/Share My Personal Information right, 12-month lookback for access requests.

## PIPEDA (Personal Information Protection and Electronic Documents Act)

Applies to: private-sector organizations in Canada collecting personal information in commercial activities.

Required clauses: accountability (named privacy officer), identified purposes, consent (express or implied), limiting collection, safeguards, openness, individual access, challenging compliance.

## Conflict resolution for multi-jurisdiction

When GDPR and CCPA conflict (e.g., legal basis for processing vs consent model): apply the stricter requirement. Note the conflict with a `[REVIEW REQUIRED: jurisdiction conflict]` marker.

When adding a new jurisdiction overlay: never remove a clause from a prior jurisdiction. Only add. If clauses are mutually exclusive: flag for human resolution.
