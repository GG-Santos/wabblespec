# Acceptance Tests — Proofread (L6)

## AT-PROOF-01: Three checks performed

**Given** a Proofread invocation on a content artifact
**When** execution runs
**Then** all three checks are performed:
- Readability (Flesch-Kincaid score computed)
- Factual accuracy (claims verified against declared fact sources)
- Consistency (terminology and style consistency across the artifact)

---

## AT-PROOF-02: FAIL verdict only on FAIL-severity findings

**Given** a Proofread run with WARN-severity findings and no FAIL-severity findings
**When** the verdict is determined
**Then** the verdict is `PASS` or `WARN`, not `FAIL`

**Given** at least one FAIL-severity finding
**When** the verdict is determined
**Then** the verdict is `FAIL`

---

## AT-PROOF-03: Missing content type triggers ask-before-proceeding

**Given** a Proofread invocation with no declared content type
**When** Proofread begins
**Then** it asks for content type before proceeding — it does not proceed with assumptions

---

## AT-PROOF-04: Receipt contains required fields

**Given** a completed Proofread run
**Then** the receipt at `.wabblespec/state/receipts/proofread-{timestamp}.json` contains:
- `artifact_path`
- `content_type`
- `readability_score`
- `findings`
- `verdict`
