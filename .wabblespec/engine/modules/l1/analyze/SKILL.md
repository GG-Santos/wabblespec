---
name: analyze
description: Root cause investigation using structured analysis methods. 5-whys, fishbone, fault-tree. Knowledge-graph-leveraged when Nexus is available. On-demand.
---

# Analyze

Symptoms are not causes. You find root causes. You use structured methods — not intuition — and you leverage Memory and Nexus to surface whether this problem has been seen before.

## What this skill does

Receives a problem statement. Selects appropriate RCA method. Works through it systematically. Produces a root cause hypothesis with confidence score. Writes RCA report and receipt.

## When to use

- Bug or incident where the cause is unknown
- Repeated failures in the same area (pattern suggests systemic cause)
- Explicit `/analyze` command
- Triage escalates an issue requiring root cause investigation

## Inputs

- Problem statement (symptom description)
- Evidence sources (logs, receipts, test output, user reports)
- Optional: Nexus query result (cross-session context)

## How to do it

### Step 1 — Select method

| Method | When to use |
|---|---|
| 5-whys | Linear cause chain, single failure mode, well-understood system |
| Fishbone (Ishikawa) | Multiple contributing factors across different categories |
| Fault tree | Safety-critical or complex multi-path failure scenarios |
| Timeline | Unknown sequence of events — reconstruct what happened when |

Record method selection rationale in receipt.

### Step 2 — Query Nexus (if available)

Before analysis: query Nexus with the problem domain. Has this failure been seen before? What modules are involved? Record `nexus_queried: boolean`.

### Step 3 — Apply method

Work through the selected method. Do not stop at the first "because" — for 5-whys, reach the system-level root (usually 3–5 levels deep). For fishbone, populate all applicable categories (People, Process, Technology, Environment, Data, External). For fault tree, trace all failure paths to basic events.

### Step 4 — State root cause with confidence

Root cause is confident (≥ 0.7) when: it is verifiable (can be confirmed via test, log, or reproduction), it is at the system level (not a symptom), and fixing it would prevent recurrence.

Root cause is probable (0.4–0.69) when: evidence suggests it but reproduction is not confirmed.

Root cause is speculative (< 0.4): note as hypothesis requiring verification, do not treat as confirmed.

### Step 5 — Write RCA report and receipt

Write to `.wabblespec/analysis/rca-<timestamp>.md`. Write receipt.

## Reference Routing

| Situation | Reference |
|---|---|
| Analyze receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` for the base, then `--extra-json` for the module-specific fields defined in `schemas/analyze-receipt.schema.json` |

## Output contract

**analyze-receipt.json** (`.wabblespec/state/receipts/analyze-receipt-<timestamp>.json`):

```json
{
  "method_used": "5-whys | fishbone | fault-tree | timeline",
  "root_cause_identified": "boolean",
  "root_cause_confidence": "number 0.0–1.0",
  "root_cause_summary": "string",
  "contributing_factors_count": "integer",
  "evidence_sources": ["array of paths or drawer IDs consulted"],
  "rca_report_path": ".wabblespec/analysis/rca-<timestamp>.md",
  "nexus_queried": "boolean"
}
```
