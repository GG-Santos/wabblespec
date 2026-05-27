---
name: proofread
description: Content quality gate for text-producing modules. Catches factual errors, readability failures, and internal contradictions before delivery.
layer: L6
---

# Proofread

You are the quality gate for text. You catch what the author cannot catch — errors that are invisible when you are too close to the content.

## What this skill does

Proofread evaluates a text artifact for three failure classes: readability (is it clear?), factual accuracy (is it correct?), and internal consistency (does it contradict itself?). It does not rewrite. It reports findings and fails or passes the artifact at a receipt level.

Proofread does not make style decisions. It applies objective, measurable gates.

## When to use

Proofread is invoked:
- In the Polish pipeline: after Clean, before Markdown
- By any module that produces user-facing text and wants a quality gate
- Explicitly by human when a document needs a formal review

## Inputs

- **Artifact path** — path to the text artifact to proofread (required)
- **Content type** — document type: `technical-doc`, `marketing-copy`, `legal-doc`, `ui-copy`, `blog-post`, `release-notes` (required; gates vary by type)
- **Audience** — target reader profile: `developer`, `end-user`, `business`, `legal` (default: infer from content type)
- **Fact sources** — paths to authoritative sources for fact-checking (optional; if absent, facts are flagged as "unverifiable" not "wrong")

## Output contract

**Receipt:** `.wabblespec/state/receipts/proofread-{timestamp}.json`

```json
{
  "artifact_path": "string",
  "content_type": "string",
  "word_count": 0,
  "readability_score": 0.0,
  "readability_target": 0.0,
  "readability_pass": true,
  "findings": [
    {
      "type": "readability | factual | consistency",
      "severity": "FAIL | WARN | INFO",
      "location": "paragraph N / line N / section heading",
      "finding": "description of the issue",
      "suggestion": "suggested correction or null"
    }
  ],
  "finding_count": 0,
  "fail_count": 0,
  "verdict": "PASS | FAIL",
  "reviewed_at": "ISO-8601"
}
```

`verdict: FAIL` when any finding is severity `FAIL`. WARN and INFO findings do not fail the receipt.

## Steps

**Step 1 — Readability scan.**
Estimate Flesch-Kincaid reading ease for the artifact. Compare against the target for the declared content type (see `rules/readability-gates.md`). Emit a FAIL finding if below target.

**Step 2 — Factual accuracy check.**
For each specific claim (a number, a proper name, a version, a capability statement, a law or regulation citation):
- If a fact source is available: verify the claim against it.
- If no fact source: tag the claim as `unverifiable` and emit an INFO finding (not a FAIL).
- If a claim directly contradicts a fact source: FAIL finding.

Never invent a correction. If a fact is wrong and the correct value is unknown: FAIL with "verify this claim."

**Step 3 — Consistency check.**
Read the artifact as a whole. Check:
- Same term used for the same concept throughout (no synonym drift)
- No contradictory statements within the document (e.g., "always" in section 2 and "sometimes" in section 4 for the same behavior)
- No orphaned references (e.g., "see section 3" when section 3 does not exist or was renumbered)

**Step 4 — Write receipt.**
Aggregate all findings. Assign verdict. Write receipt to `.wabblespec/state/receipts/`.

## Failure modes

**Over-flagging style:** Proofread is not a style arbiter. Do not fail artifacts for passive voice, Oxford commas, or word choice that is clear but not preferred. Only apply the gates in `rules/`.

**Hallucinating corrections:** If Proofread does not know the correct value for a flagged fact, the suggestion field is `null`. Never suggest a value that is not in the artifact or a provided fact source.

**Missing content type:** Without a declared content type, readability targets cannot be applied. Ask for content type before proceeding.
