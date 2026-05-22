# WabbleSpec v6.1 — Expression

**Layer:** L6 Expression
**Document scope:** All L6 modules — Homowabian, Document, Polish, ResearchLog
**Depends on:** L5 Memory (drawers, Provenance, EntityGraph, MemorySearch), L1 Specify (spec artifacts), L2 Economy

---

## Overview

L6 Expression governs how knowledge is shaped into output. Where L5 Memory stores evidence, L6 converts that evidence into the right voice, the right artifact format, and the right record. Expression does not invent — it organizes, refines, and captures what other layers produce.

Four modules:

| Module | Tier | Purpose |
|---|---|---|
| Homowabian | 2 — CORE | Voice register control — how all output sounds |
| Document | 3 — SUPPORTING | Long-form documentation generation from spec artifacts |
| Polish | 3 — SUPPORTING | 4-pass artifact refinement before delivery |
| ResearchLog | 3 — SUPPORTING | Research session capture, writes findings to Memory |

L6 is always downstream — it runs after execution modules produce content, before Delivery layers receive it.

---

## Layer Boundaries

What L6 owns:
- Voice register (Homowabian)
- Documentation artifact generation from existing spec content (Document)
- Prose refinement on generated artifacts (Polish)
- Research session capture and Memory handoff (ResearchLog)

What L6 does not own:
- Code generation (Apply)
- Spec writing (Specify)
- Memory storage (Memory, MemorySearch, Provenance)
- Delivery packaging (Package, Deploy, Release)
- Evidence origination (all upstream modules)

Hard boundary: Document and Polish are read-only on `.wabblespec/`. They cannot modify spec artifacts. They write only to `project/repo/docs/` (Document) or overwrite the artifact they polished (Polish), always with a diff record.

---

## Homowabian

**Tier:** 2 — CORE
**v5.3 origin:** v5.3 Invariant 7 (compression by default) — named and separated from Economy in v6.1

### Purpose

Homowabian governs voice register across all module output. Four registers: lite, full, ultra, normal. It controls HOW output sounds. Economy controls output density. These are orthogonal — full register can be dense, normal register can be compressed.

Every module output passes through Homowabian before reaching the user or next module. Homowabian does not produce artifacts — it transforms output in-place.

### Register Definitions

**lite**

Brief, direct, status-oriented. Progress updates, confirmations, short responses.

- Fragments acceptable
- No preamble, no closing
- State result, state next step
- Drop articles, drop filler

Example: `Wave 3 complete. 4 files written. Starting Wave 4.`

**full**

Dense planning synthesis. Complex plans, spec writing, analysis.

- Structured sections with headers
- Technical depth preserved
- Tables and lists preferred over prose
- No filler, no hedging

Example: module plan documents, architecture guides, analysis outputs.

**ultra**

Maximum compression. Module-to-module handoffs, internal receipts, machine-readable output.

- No prose explanation
- Data and decisions only
- Single-line entries per item
- No headers unless structurally required

Example: receipt fields, routing decisions, error events.

**normal**

Plain prose. Required for code, commits, security warnings, irreversible action confirmations, exact technical instructions.

- Standard written English
- Full sentences, full articles
- Context and explanation included where needed
- No compression artifacts

Example: commit messages, security advisories, user-facing error messages with resolution steps.

### Auto-Switch Rules

These override any active register. Homowabian cannot suppress them.

| Condition | Forced register | Reason |
|---|---|---|
| Code block output | normal (block only) | Compression changes meaning |
| Git commit message | normal | Shared artifact — must be readable |
| Security warning | normal | Clarity required for safety |
| Irreversible action confirmation | normal | User must fully understand before acting |
| Attestation verification mode | normal | Human sign-off requires unambiguous language |
| PR or issue content | normal | Shared external artifacts |

After auto-switch block completes: return to prior register.

### Register Selection Guidance

| Context | Register |
|---|---|
| Session progress update | lite |
| Planning synthesis | full |
| Spec writing | full |
| Module-to-module handoff | ultra |
| Receipt content | ultra |
| Error event body (type field) | ultra |
| Error event body (message field) | normal |
| User-facing explanation (simple) | lite |
| User-facing explanation (complex) | full |
| Code, commits, security | normal (forced) |

### Workflow

```
1. Receive output from any module

2. Check auto-switch conditions:
   -> Code block? -> apply normal for block, restore after
   -> Security / irreversible / Attestation? -> apply normal for block, restore after

3. Check active register (session state or explicit /homowabian override)

4. Apply register transformation:
   -> lite:   strip preamble, strip closing, compress to fragments where safe
   -> full:   structure with headers/tables, remove filler
   -> ultra:  strip all prose, data only
   -> normal: pass through with standard prose cleanup only

5. Return transformed output

6. Log register if override was applied (Economy owns the log)
```

### Activation

`skill-rules.json` triggers Homowabian on:
- Any output generation by any module (passive — always active)
- Explicit register change: `/homowabian lite|full|ultra|normal`
- Auto-switch conditions (Attestation, security warnings, irreversible actions)

### Integration Points

| Module | Relationship |
|---|---|
| Economy | Orthogonal. Economy compresses density, Homowabian adjusts voice. Economy reads Homowabian register to skip compression in normal mode. Homowabian reads Economy's compression level to avoid conflict. |
| All L0-L7 modules | Passive layer on all output — every module output passes through |
| Verifier | Attestation verification mode forces normal register |
| Reviewer | Reviewer writes full register for analysis, normal for escalation notices |
| Polish | Polish reads active Homowabian register from meta.md (Pass 1: register enforcement) |

### Verification Mode

**Observation** — output register matches context. Auto-switch conditions applied correctly. No normal-register content compressed. No code blocks altered by register transformation.

### Receipt Extension Fields

```json
{
  "active_register": "lite|full|ultra|normal",
  "auto_switch_applied": true,
  "auto_switch_reason": "string — reason for auto-switch if applied",
  "register_overrides": 0
}
```

### v5.3 Mapping

| v5.3 Invariant 7 | v6.1 Homowabian |
|---|---|
| Compression = density + voice combined | Separated: density → Economy, voice → Homowabian |
| lite/full/ultra levels | lite/full/ultra/normal register levels (normal added) |
| Normal for security/irreversible | Same auto-switch rules |
| No named identity | Named: Homowabian |
| No module — embedded in Economy | Standalone L6 module |

---

## Document

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Document module — long-form documentation generation

### Purpose

Generate long-form documentation artifacts from spec content and execution receipts. README, architecture guides, API references, onboarding docs, decision logs, changelogs. Document does not invent content — synthesizes from existing spec artifacts, Memory drawers, and receipts. Every output claim is traceable to a source artifact.

### Document Types

| Type | Source artifacts | Output path |
|---|---|---|
| README | P1 design doc, scope.md, project-map.md | `project/repo/README.md` |
| Architecture guide | P2 systems design, ADRs | `project/repo/docs/architecture.md` |
| API reference | P3 technical spec, OpenAPI/proto | `project/repo/docs/api.md` or generated file |
| Onboarding | README, project-map.md, dev modules | `project/repo/docs/onboarding.md` |
| Decision log | All ADRs from Engineering gateway | `project/repo/docs/decisions/` |
| Changelog | Archive receipts, version history | `project/repo/CHANGELOG.md` |

### Content Rules

**Traceability** (`rules/traceability.md`):
- Every claim in generated documentation must be traceable to a source spec artifact, Memory drawer, or receipt
- No invented content — if information is not in source artifacts, Document flags the gap and leaves a placeholder
- Source citation format in output: `<!-- source: .wabblespec/path/to/artifact -->`

**Staleness awareness** (`rules/staleness-awareness.md`):
- Document reads staleness state of all source drawers before generating
- STALE or EXPIRED source: flagged in output with staleness warning — not silently used
- NEEDS_REVERIFICATION source: output marked as requiring verification before publish
- FRESH and AGING sources: usable without warning

**Scope** (`rules/scope.md`):
- Document writes only to `project/repo/docs/` or declared documentation paths
- Read-only access to `.wabblespec/` — never modifies spec artifacts
- Does not write code — documentation only

### Workflow

```
1. Receive document type and scope declaration

2. Identify source artifacts:
   -> Spec artifacts (P1-P4 outputs)
   -> Memory drawers (relevant topic search via MemorySearch)
   -> Receipts (Archive receipts, Engineering gateway ADRs)

3. Check staleness of all source artifacts:
   -> Flag any STALE / EXPIRED sources
   -> Mark NEEDS_REVERIFICATION sources as unverified in output

4. Synthesize content:
   -> Structure from document type template
   -> Content from source artifacts (no invention)
   -> Gaps flagged with placeholder markers

5. Apply Homowabian register:
   -> Documentation defaults to full register (dense, structured)
   -> API reference: ultra register (data-dense, minimal prose)

6. Write output to declared path in project/repo/

7. Write Document receipt
```

### Activation

`skill-rules.json` triggers Document on:
- Explicit `/document <type>` command
- Archive triggers Document after major version bump (README and changelog updated)
- P4 spec stage completion — API reference generated from spec if declared
- Delivery gate — documentation completeness check before ship

### Integration Points

| Module | Relationship |
|---|---|
| Archive | Archive triggers Document after version bump |
| MemorySearch | Document queries Memory for relevant context per section |
| Specify | Document reads spec artifacts as primary source content (read-only) |
| Homowabian | Document applies register — full for guides, ultra for API reference |
| Engineering gateway | Document reads ADRs for decision log generation |
| Provenance | Document checks source provenance before citing |

### Verification Mode

**Observation** — output written to declared path, all sections have source citations, no STALE/EXPIRED sources used without flagging, receipt written.

### Receipt Extension Fields

```json
{
  "document_type": "string",
  "source_artifacts": ["string"],
  "stale_sources_flagged": 0,
  "gaps_flagged": 0,
  "output_path": "string"
}
```

### Templates

Each document type has a template in `templates/`:

| Template | Purpose |
|---|---|
| `templates/readme.md` | README structure per build target |
| `templates/architecture.md` | Architecture guide structure |
| `templates/api-reference.md` | API reference structure |
| `templates/onboarding.md` | Onboarding structure |
| `templates/changelog.md` | Changelog entry format |

Templates define section order and required headings. Document fills sections from source artifacts. Empty sections become flagged placeholders, not omitted sections.

---

## Polish

**Tier:** 3 — SUPPORTING
**v5.3 origin:** Polish module — refinement pass on generated output before delivery

### Purpose

Four-pass refinement on generated artifacts before delivery. Improves clarity, removes redundancy, enforces Homowabian register consistency, catches spec violations in prose. Does not change semantics — surface quality only. Runs after Executor and before Verifier's final pass, or on explicit command.

### What Polish Cannot Touch

Polish never runs on:
- Code files — Apply owns code. Polish cannot write to `project/repo/` code files
- Schema files or JSON artifacts — no prose content
- Receipts — operational artifacts, immutable after write

Attempting Polish on excluded types returns `SPEC_VIOLATION` error and aborts.

### The Four Passes

Polish runs passes sequentially. Each pass has a distinct scope.

**Pass 1: Register enforcement**

Read active Homowabian register from meta.md. For each prose block:

| Register | Check |
|---|---|
| normal | Security warnings, irreversible action context, Attestation content — enforce normal if any detected |
| full | Headers and tables present for structured content. Fragments not in explanatory paragraphs |
| lite | No multi-paragraph prose. No trailing summaries |

Flag register violations — do not silently override.

**Pass 2: Redundancy removal**

Detect and remove:
- Repeated explanations of the same concept in the same artifact
- Trailing summaries that restate what was just said
- Filler phrases (Economy hedge list patterns)
- Section headers with no content below them

Do not remove:
- Repetition that serves clarity (step numbers, prerequisites before destructive actions)
- Intentional emphasis (bold on key terms)

**Pass 3: Structural consistency**

- Table formatting: verify alignment, no empty cells without explicit N/A
- Code block labeling: language identifier present on all code blocks
- Heading hierarchy: H1 only once, H2/H3/H4 sequential, no skipped levels
- Link validity: internal links verified (file path existence), external links flagged for human review

**Pass 4: Spec compliance check (prose)**

- No claims in prose that contradict spec artifacts
- Entity names match canonical names from EntityGraph
- No deprecated term usage (from Specify's non-goals or anti-patterns lists)

Flag violations — do not silently correct. Polish surfaces the problem; Specify resolves it.

### Outputs

| Output | Location | Purpose |
|---|---|---|
| Polished artifact | Overwrites source artifact in place | Refined output |
| Polish diff | `.wabblespec/receipts/polish-diff-<timestamp>.md` | Record of all changes made and why |
| Polish receipt | `.wabblespec/receipts/polish-receipt.md` | I10 compliance |

Polish diff is mandatory. Every change recorded with pass type and reason. Polish never silently overwrites without a diff record.

### Workflow

```
1. Receive artifact path and scope (full 4-pass or specific pass declared)

2. Read artifact

3. Check: is artifact in excluded category (code, schema, receipt)?
   -> IF yes: abort, return SPEC_VIOLATION error

4. Read active Homowabian register from meta.md

5. Run declared passes in sequence:
   -> Pass 1: Register enforcement
   -> Pass 2: Redundancy removal
   -> Pass 3: Structural consistency
   -> Pass 4: Spec compliance check

6. Write polished artifact (overwrite in place)

7. Write polish diff to .wabblespec/receipts/

8. Write Polish receipt
```

### Activation

`skill-rules.json` triggers Polish on:
- Explicit `/polish <artifact>` command
- Verifier routes artifact to Polish when quality dimension fails (prose clarity, register inconsistency)
- Delivery gate triggers Polish pass on documentation artifacts before ship

Polish automatically skips when:
- Homowabian ultra mode active — ultra output already stripped, no prose to refine
- Artifact is in excluded category (code, schema, receipt)

### Integration Points

| Module | Relationship |
|---|---|
| Homowabian | Polish reads active register from meta.md (Pass 1). Homowabian owns register state — Polish enforces it, does not set it |
| Verifier | Verifier routes artifacts to Polish when quality dimension fails |
| Document | Document output is Polish's primary input for pre-delivery passes |
| Economy | Polish applies Economy hedge patterns in Pass 2 redundancy removal |
| Specify | Polish reads spec artifacts for canonical terms in Pass 4 |
| EntityGraph | Polish queries EntityGraph for canonical name verification in Pass 4 |

### Verification Mode

**Observation** — all four passes completed (or declared subset), polish diff written, no excluded types modified, receipt written.

### Receipt Extension Fields

```json
{
  "artifact_path": "string",
  "passes_run": [1, 2, 3, 4],
  "register_violations_fixed": 0,
  "redundancies_removed": 0,
  "structural_issues_fixed": 0,
  "spec_violations_flagged": 0,
  "diff_path": "string"
}
```

---

## ResearchLog

**Tier:** 3 — SUPPORTING
**v5.3 origin:** ResearchLog — research session capture, traceable to Memory

### Purpose

Structured capture of research sessions, reference discoveries, and investigation outcomes. Writes confirmed research findings to Memory as FRESH drawers with full Provenance metadata. Provides a human-readable log of what was investigated, what was found, and what was discarded. Bridges the gap between ad hoc research activity and Memory's evidence store.

Critical rule: discarded findings are never written to Memory. Memory stays clean of rejected evidence. Rejected findings live only in the ResearchLog entry.

### Log Entry Structure

Each research session produces one log entry file:

```markdown
# Research Log — <topic>

**session_id:** string
**timestamp:** ISO 8601
**triggered_by:** ReferenceLoad|Explore|Manual|Phase-Research
**topic:** string
**scope:** string (what was investigated)

## Investigated

<what was looked at — sources, queries, paths explored>

## Findings

<what was confirmed or discovered — with source citations>

## Discarded

<what was considered and rejected — reason required>

## Gaps

<what could not be resolved — declare explicitly>

## Memory Writes

| Drawer ID | Topic | Staleness |
|---|---|---|
| drawer-id | topic summary | FRESH |

## Provenance

**source:** <primary source URL or file path>
**trust_level:** HIGH|MEDIUM|LOW
**cited_by:** [drawer IDs that cite this research]
```

### Drawer Granularity

One drawer per distinct finding — not one drawer per session.

Drawer topic derived from finding content, not session topic. Drawer confidence set from source trust level:

| Trust level | Initial confidence |
|---|---|
| HIGH | 0.9 |
| MEDIUM | 0.7 |
| LOW | 0.5 |

Provenance record written alongside each drawer. EntityGraph notified for entity extraction from each drawer.

### Storage

```
.wabblespec/research-log/
  INDEX.md                        <- chronological index of all sessions
  <session-id>.md                 <- one file per research session
```

`INDEX.md` format:

```markdown
# Research Log Index

| Session ID | Timestamp | Topic | Drawer Count | Triggered By |
|---|---|---|---|---|
| session-id | 2026-05-21T14:30:00Z | topic | 3 | ReferenceLoad |
```

### Workflow

```
1. Research session ends (manual or triggered)

2. Structure findings into log entry format:
   -> Investigated: all sources touched
   -> Findings: confirmed content with source citations
   -> Discarded: rejected content with reason (required)
   -> Gaps: unresolved questions (required — no silent omissions)

3. Write log entry to .wabblespec/research-log/<session-id>.md

4. For each confirmed finding:
   -> Write Memory drawer (topic, content, staleness FRESH)
   -> Write Provenance record (source, trust level, cited_by)
   -> Notify EntityGraph

5. Update .wabblespec/research-log/INDEX.md (append entry)

6. Write ResearchLog receipt
```

### Activation

`skill-rules.json` triggers ResearchLog on:
- ReferenceLoad completes a research session (auto-logs loaded references)
- Explicit `/research-log <topic>` command
- Explore completes project-map discovery (Explore auto-logs findings)
- Research phase end — Research phase always writes a ResearchLog entry before Plan phase begins

### Integration Points

| Module | Relationship |
|---|---|
| ReferenceLoad | ReferenceLoad triggers ResearchLog after completing reference load |
| Explore | Explore triggers ResearchLog after project-map discovery |
| Memory | ResearchLog writes all confirmed findings to Memory as FRESH drawers |
| Provenance | ResearchLog writes Provenance record for each Memory drawer it creates |
| EntityGraph | EntityGraph notified per new drawer from ResearchLog |
| MemorySearch | ResearchLog INDEX.md queryable by MemorySearch for session lookup |

### Verification Mode

**Observation** — log entry written for every Research phase, confirmed findings written to Memory, discarded findings NOT in Memory, INDEX.md updated, receipt written.

### Receipt Extension Fields

```json
{
  "session_id": "string",
  "triggered_by": "ReferenceLoad|Explore|Manual|Phase-Research",
  "findings_count": 0,
  "discarded_count": 0,
  "gaps_count": 0,
  "drawers_written": 0,
  "provenance_records_written": 0
}
```

---

## L6 Layer Interactions

### Expression execution order

For any documentation or refinement task, L6 modules run in this order:

```
Upstream module produces output
  -> Homowabian transforms voice/register (passive, always)
  -> Document generates artifact (if documentation task)
  -> Polish refines artifact (if quality pass triggered)
  -> Verifier checks output (Observation mode)
  -> Delivery layer receives artifact
```

ResearchLog runs orthogonal to this flow — it fires at Research phase end regardless of what else is running.

### Register propagation

Homowabian register is session-scoped state stored in `meta.md`. All L6 modules read register from `meta.md` — they do not set it. Only Homowabian writes register state. Only Autopilot modifies `meta.md` directly; all other modules submit change requests.

### Economy and Homowabian interaction

Economy (L2) and Homowabian (L6) are orthogonal but must not conflict:

| Economy compression | Homowabian register | Result |
|---|---|---|
| high | lite | Fragments compressed further — acceptable |
| high | normal | Economy skips compression — normal overrides |
| low | full | Full prose, low compression — consistent |
| high | ultra | Ultra already stripped — Economy no-ops |

Economy reads Homowabian register. If register is normal, Economy compression is suspended for that output.

---

## Invariants Enforced by L6

| Invariant | How L6 enforces it |
|---|---|
| I6 (Compression by default) | Homowabian lite register as default; normal only forced by auto-switch |
| I10 (Receipts as operational artifacts) | Polish diff mandatory before overwrite; Polish receipt written per run; Document and ResearchLog receipts written per operation |
| I12 (Spec quality over volume) | Polish Pass 2 removes redundancy; Document gaps flagged rather than invented; ResearchLog discards kept out of Memory |

---

## Sub-Components Summary

| Module | Required components |
|---|---|
| Homowabian | SKILL.md, skill-rules.json, references/register-examples.md, rules/auto-switch.md, rules/register-guidance.md, schemas/receipt.schema.json |
| Document | SKILL.md, skill-rules.json, templates/ (5 types), rules/traceability.md, rules/staleness-awareness.md, rules/scope.md, schemas/receipt.schema.json |
| Polish | SKILL.md, skill-rules.json, rules/excluded-types.md, rules/pass-sequence.md, rules/diff-policy.md, schemas/receipt.schema.json |
| ResearchLog | SKILL.md, skill-rules.json, templates/log-entry.md, rules/discard-policy.md, rules/drawer-granularity.md, schemas/receipt.schema.json |

---

## v5.3 Mapping

| v5.3 module | v6.1 module | Change |
|---|---|---|
| Compression (Invariant 7, Economy) | Homowabian | Separated from Economy. Voice register is now standalone module. Normal register added. |
| Document | Document | Unchanged in purpose. Staleness awareness added (STALE/EXPIRED source flagging). |
| Polish | Polish | 4-pass structure formalized. Pass 4 (spec compliance check) added. Diff record now mandatory. |
| ResearchLog | ResearchLog | Drawer granularity rule formalized (one drawer per finding). Trust-level-to-confidence mapping made explicit. |

---

## Cross-References

- L5 Memory store: `WabbleSpec v6.1 — Memory.md`
- L2 Economy (density control): `WabbleSpec v6.1 — Core.md` § Economy
- L7 Delivery (receives Expression output): `WabbleSpec v6.1 — Delivery.md`
- Verification modes: `WabbleSpec v6.1 — Core.md` § Verification Modes
- Invariants: `WabbleSpec v6.1 — Core.md` § Invariants
