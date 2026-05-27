# Entity Graph Report

> Generated: 2026-05-24T13:09:29.147163+00:00
> Drawers scanned: 12
> Nodes: 36  Edges: 83

## Entity Type Breakdown

- concept: 11
- module: 13
- file: 12

## Top 20 Entities by Degree (most connected)

| Entity | Type | Degree | Drawer count |
|---|---|---|---|
| guard | module | 14 | 3 |
| verifier | module | 10 | 2 |
| decompose | module | 10 | 2 |
| archive | module | 10 | 2 |
| recipe | module | 10 | 2 |
| memory | module | 8 | 2 |
| phase 2 module order rationale | concept | 8 | 1 |
| executor | module | 8 | 1 |
| reviewer | module | 8 | 1 |
| specify | module | 8 | 1 |
| PASS/FAIL/PARTIAL | file | 7 | 3 |
| receipt schema design | concept | 5 | 2 |
| guard memory backend invariants | concept | 4 | 1 |
| scripts/migrate-json-drawers.py | file | 4 | 1 |
| wabblespec/memory/chroma | file | 4 | 1 |
| memory drawer storage structure | concept | 4 | 1 |
| EXPIRED/SUPERSEDED | file | 4 | 1 |
| wabblespec/memory/wings | file | 4 | 1 |
| instinct | module | 4 | 1 |
| L0-L8/shared | file | 3 | 1 |

## Top 15 Relationships (highest co-occurrence weight)

| Entity A | Entity B | Weight |
|---|---|---|
| archive | recipe | 2 |
| receipt schema design | PASS/FAIL/PARTIAL | 2 |
| verifier check types | PASS/FAIL/PARTIAL | 1 |
| verifier check types | verifier | 1 |
| PASS/FAIL/PARTIAL | verifier | 1 |
| skill factory gaps and wabblespec templates | factory | 1 |
| skill factory gaps and wabblespec templates | scaffold | 1 |
| factory | scaffold | 1 |
| guard module invariant enforcement | _shared/references/invariants.md | 1 |
| guard module invariant enforcement | guard | 1 |
| _shared/references/invariants.md | guard | 1 |
| guard memory backend invariants | scripts/migrate-json-drawers.py | 1 |
| guard memory backend invariants | wabblespec/memory/chroma | 1 |
| guard memory backend invariants | guard | 1 |
| guard memory backend invariants | memory | 1 |

---

## Expansion rule

Do not add a 4th entity type until 50+ drawers exist AND a real query fails because the missing type would have answered it.
