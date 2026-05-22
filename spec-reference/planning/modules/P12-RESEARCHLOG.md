# Module Plan — ResearchLog (L6)

**Tier:** 3 — SUPPORTING
**Layer:** L6 Expression
**v5.3 origin:** ResearchLog — research session capture, traceable to Memory

---

## Purpose

Structured capture of research sessions, reference discoveries, and investigation outcomes. Writes research findings to Memory as FRESH drawers with full Provenance metadata. Provides a human-readable log of what was investigated, what was found, and what was discarded. Bridges the gap between ad hoc research activity and Memory's evidence store.

---

## Activation

`skill-rules.json` triggers:
- ReferenceLoad completes a research session (auto-logs loaded references)
- Explicit `/research-log <topic>` command
- Explore completes project-map discovery (Explore auto-logs findings)
- Any research-phase activity — Research phase always writes a ResearchLog entry before Plan phase begins

---

## Log Entry Structure

Each research session produces one log entry:

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

---

## Memory Integration

Every ResearchLog entry automatically triggers Memory writes:
- One drawer per distinct finding (not one drawer per session)
- Drawer topic derived from finding content, not session topic
- Drawer confidence set from source trust level (HIGH → 0.9, MEDIUM → 0.7, LOW → 0.5)
- Provenance record written alongside each drawer
- EntityGraph notified for entity extraction

Discarded findings are NOT written to Memory drawers — only to the ResearchLog entry. Memory stays clean of rejected evidence.

---

## Workflow

```
1. Research session ends (manual or triggered)

2. Structure findings into log entry format:
   -> Investigated: all sources touched
   -> Findings: confirmed content with citations
   -> Discarded: rejected content with reasons
   -> Gaps: unresolved questions

3. Write log entry to .wabblespec/research-log/<session-id>.md

4. For each finding:
   -> Write Memory drawer (topic, content, staleness FRESH)
   -> Write Provenance record
   -> Notify EntityGraph

5. Update research-log/INDEX.md (append entry)

6. Write ResearchLog receipt
```

---

## Storage

```
.wabblespec/research-log/
  INDEX.md                        <- chronological index of all sessions
  <session-id>.md                 <- one file per research session
```

`INDEX.md` structure:

```markdown
# Research Log Index

| Session ID | Timestamp | Topic | Drawer Count | Triggered By |
|---|---|---|---|---|
| session-id | timestamp | topic | 3 | ReferenceLoad |
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — auto from Research phase |
| `templates/log-entry.md` | Template | Log entry structure |
| `rules/discard-policy.md` | Rules | Discarded findings never go to Memory |
| `rules/drawer-granularity.md` | Rules | One drawer per finding, not per session |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| ReferenceLoad | ReferenceLoad triggers ResearchLog after completing reference load |
| Explore | Explore triggers ResearchLog after project-map discovery |
| Memory | ResearchLog writes all confirmed findings to Memory as FRESH drawers |
| Provenance | ResearchLog writes Provenance record for each Memory drawer it creates |
| EntityGraph | EntityGraph notified per new drawer from ResearchLog |
| MemorySearch | ResearchLog INDEX.md queryable by MemorySearch for session lookup |

---

## Verification Mode

**Observation** — log entry written for every Research phase, findings written to Memory, discarded findings NOT in Memory, INDEX.md updated, receipt written.

---

## Receipt Extension Fields

```json
{
  "session_id": "string",
  "triggered_by": "string",
  "findings_count": "integer",
  "discarded_count": "integer",
  "gaps_count": "integer",
  "drawers_written": "integer",
  "provenance_records_written": "integer"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Log entry per finding vs. per session | Per session (current) vs. per finding (more granular, more files) | Implementation |
| Discard visibility | Log only (current) vs. optional discard drawer in Memory with SUPERSEDED status | Per-module planning |
| Session ID format | UUID vs. timestamp-slug (topic-YYYYMMDD-HHMMSS) | Implementation |
