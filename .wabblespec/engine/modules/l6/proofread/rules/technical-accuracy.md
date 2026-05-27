# Technical Accuracy

Rules for fact-checking content during Proofread. Applied in Step 2.

## What counts as a checkable fact

A claim is checkable when it is:
- A specific number, measurement, or percentage
- A proper name (product name, company name, person name)
- A version number or release identifier
- A capability statement ("supports X", "requires Y", "does not work with Z")
- A law or regulation citation (GDPR Article N, CCPA §N)
- A quote attributed to a person or organization

Generic qualitative statements ("fast", "easy to use", "popular") are not checkable facts.

## Verification process

**When fact sources are provided:**
1. For each checkable claim, locate the corresponding item in a fact source
2. If found and matching: mark verified
3. If found but contradicting: FAIL finding with exact contradiction
4. If not found in any source: mark "unverifiable" — emit INFO finding

**When no fact sources are provided:**
All checkable claims are marked "unverifiable." Emit one INFO finding per claim. Do not fail the document for unverifiable claims — only for contradicted claims.

## Severity rules

| Situation | Severity |
|---|---|
| Claim contradicts a provided fact source | FAIL |
| Claim is unverifiable (no source available) | INFO |
| Regulation cited with wrong article number | FAIL |
| Version number inconsistent within the document | WARN |
| Proper name inconsistently spelled within the document | WARN |

## Correction policy

When a claim is wrong: the finding states the detected value vs. the source value. The suggestion field provides the correct value from the source.

When a claim is unverifiable: the suggestion field is `null`. Never invent a correction.
