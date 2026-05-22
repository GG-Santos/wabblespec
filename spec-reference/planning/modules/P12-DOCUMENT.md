# Module Plan — Document (L6)

**Tier:** 3 — SUPPORTING
**Layer:** L6 Expression
**v5.3 origin:** Document module — long-form documentation generation

---

## Purpose

Generate long-form documentation artifacts from spec content and execution receipts. README, architecture guides, API references, onboarding docs, decision logs. Does not invent content — synthesizes from existing spec artifacts, Memory drawers, and receipts. Output always traceable to source artifacts.

---

## Activation

`skill-rules.json` triggers:
- Explicit `/document <type>` command
- Archive triggers Document after major version bump (README and changelog updated)
- P4 spec stage completion (API reference generated from spec if declared)
- Delivery gate (documentation completeness check before ship)

---

## Document Types

| Type | Source artifacts | Output |
|---|---|---|
| README | P1 design doc, scope.md, project-map.md | `project/repo/README.md` |
| Architecture guide | P2 systems design, ADRs | `project/repo/docs/architecture.md` |
| API reference | P3 technical spec, OpenAPI/proto | `project/repo/docs/api.md` or generated file |
| Onboarding | README, project-map.md, dev modules | `project/repo/docs/onboarding.md` |
| Decision log | All ADRs from Engineering gateway | `project/repo/docs/decisions/` |
| Changelog | Archive receipts, version history | `project/repo/CHANGELOG.md` |

---

## Content Rules

`rules/traceability.md`:
- Every claim in generated documentation must be traceable to a source spec artifact, Memory drawer, or receipt
- No invented content — if information is not in source artifacts, Document flags the gap and leaves a placeholder
- Source citation format: `<!-- source: .wabblespec/path/to/artifact -->`

`rules/staleness-awareness.md`:
- Document reads staleness state of all source drawers before generating
- STALE or EXPIRED source: flagged in output with staleness warning, not silently used
- NEEDS_REVERIFICATION source: output marked as requiring verification before publish

`rules/scope.md`:
- Document writes only to `project/repo/docs/` or declared documentation paths
- Does not modify spec artifacts (read-only access to .wabblespec/)
- Does not write code — documentation only

---

## Workflow

```
1. Receive document type and scope declaration

2. Identify source artifacts:
   -> spec artifacts (P1-P4 outputs)
   -> Memory drawers (relevant topic search via MemorySearch)
   -> receipts (Archive, Engineering gateway)

3. Check staleness of all source artifacts
   -> Flag any STALE/EXPIRED sources

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

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation + read-only authority over .wabblespec/ |
| `templates/readme.md` | Template | README structure variant per build target |
| `templates/architecture.md` | Template | Architecture guide structure |
| `templates/api-reference.md` | Template | API reference structure |
| `templates/onboarding.md` | Template | Onboarding structure |
| `templates/changelog.md` | Template | Changelog entry format |
| `rules/traceability.md` | Rules | Source citation requirements |
| `rules/staleness-awareness.md` | Rules | Stale source handling |
| `rules/scope.md` | Rules | Write authority boundaries |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Archive | Archive triggers Document after version bump |
| MemorySearch | Document queries Memory for relevant context per section |
| Specify | Document reads spec artifacts as primary source content |
| Homowabian | Document applies register (full for guides, ultra for API reference) |
| Engineering gateway | Document reads ADRs for decision log generation |
| Provenance | Document checks source provenance before citing |

---

## Verification Mode

**Observation** — output written to declared path, all sections have source citations, no STALE/EXPIRED sources used without flagging, receipt written.

---

## Receipt Extension Fields

```json
{
  "document_type": "string",
  "source_artifacts": ["string"],
  "stale_sources_flagged": "integer",
  "gaps_flagged": "integer",
  "output_path": "string"
}
```

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Auto-update on spec change | Document re-runs on spec delta vs. manual trigger only | Implementation |
| API reference generation | Document generates from spec vs. dedicated codegen tool (TypeDoc, Swagger) | Per-project at P3 |
| Multi-language docs | Scope to English only in v6.1 vs. i18n hook for future | v6.1 scope decision |
