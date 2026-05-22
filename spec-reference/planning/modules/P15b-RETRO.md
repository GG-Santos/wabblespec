# Module Plan — Retro (L8)

**Tier:** 3 — SUPPORTING
**Layer:** L8 Evolution
**v5.3 origin:** Retro module — structured retrospective after release cycle

---

## Purpose

Structured retrospective after each release cycle. Reads Instinct patterns, all cycle receipts, Verifier not-tested lists, and open decisions to produce a human-collaborative retro artifact. Framework drafts; human reviews and confirms. "What changes" section produces concrete Synth proposals (framework improvement) or Triage records (product improvement). Retro is the explicit reflection step that converts accumulated execution observations into directed next actions.

---

## Activation

`skill-rules.json` triggers:
- Release receipt written (always triggers Retro for that release cycle)
- Explicit `/retro` command
- Autopilot L3+ after major milestone completion

---

## Retro Artifact Structure

```markdown
# Retrospective — v<version> — <date>

**release_ref:** release receipt ID
**cycle_start:** timestamp (date of previous retro or project start)
**cycle_end:** timestamp (release date)
**generated_at:** timestamp

## What Worked

<patterns from Instinct with positive confidence trend>
<verifier gates that consistently passed>
<waves that completed without REVISE cycles>

## What Didn't

<patterns from Instinct with negative trend or high recurrence>
<verifier gates that consistently failed>
<Reviewer budget gates that triggered frequently>
<waves that required max REVISE cycles>
<items from not-tested compilation>

## Open Decisions Unresolved at Ship

<open decisions from module plans that were not resolved this cycle>

## What Changes

### Framework improvements → Synth

| Observation | Proposed direction |
|---|---|
| <pattern> | <high-level direction> |

### Product improvements → Triage

| Issue | Severity | Suggested type |
|---|---|---|
| <issue> | high/medium/low | bug/feature/debt |

## Human Review Section

**status:** DRAFT (human review required before routing)
**reviewer:** <assigned or unassigned>
**notes:** <human adds notes here>
```

---

## Workflow

```
1. Read Release receipt (cycle boundary)

2. Read Instinct tracker.json (pattern confidence trends for the cycle)

3. Read all receipts from cycle (Verifier, Reviewer, Executor waves)

4. Read not-tested compilation from Archive

5. Read open decisions from all module plans (unresolved flags)

6. Draft retro artifact:
   -> What Worked: positive patterns, clean gates
   -> What Didn't: negative patterns, failing gates, revise cycles
   -> Open Decisions: unresolved items
   -> What Changes: Synth proposals + Triage records (DRAFT)

7. Write retro to .wabblespec/plans/retro-v<version>.md
   -> Status: DRAFT — requires human review before routing

8. Write Retro receipt

9. After human confirms: route "What Changes" items:
   -> Synth proposals → Synth module
   -> Product issues → Triage module
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — post-Release |
| `templates/retro.md` | Template | Retro artifact structure |
| `rules/draft-first.md` | Rules | Retro always DRAFT — human confirms before routing |
| `rules/no-auto-routing.md` | Rules | No Synth or Triage routed without human confirmation |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Release | Release triggers Retro; Retro reads Release receipt for cycle boundary |
| Instinct | Retro reads tracker.json for pattern confidence analysis |
| Archive | Retro reads not-tested compilation from Archive |
| Synth | Retro routes confirmed framework improvement proposals to Synth |
| Triage | Retro routes confirmed product issues to Triage |
| Memory | Retro written to Memory as FRESH drawer after human confirms |

---

## Verification Mode

**Attestation** — human reviews DRAFT retro before routing proceeds, routing actions confirmed by human, receipt written.

---

## Receipt Extension Fields

```json
{
  "release_ref": "string",
  "patterns_analyzed": "integer",
  "worked_items": "integer",
  "didnt_work_items": "integer",
  "synth_proposals_drafted": "integer",
  "triage_records_drafted": "integer",
  "human_confirmed": "boolean",
  "retro_path": "string"
}
```
