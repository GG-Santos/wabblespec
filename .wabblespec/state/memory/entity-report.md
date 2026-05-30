# Entity Graph Report

> Generated: 2026-05-30T18:00:21.571990+00:00
> Drawers scanned: 102
> Nodes: 191  Edges: 899

## Entity Type Breakdown

- concept: 54
- module: 31
- file: 106

## Top 20 Entities by Degree (most connected)

| Entity | Type | Degree | Drawer count |
|---|---|---|---|
| guard | module | 56 | 12 |
| instinct | module | 50 | 11 |
| executor | module | 50 | 11 |
| specify | module | 45 | 7 |
| verifier | module | 44 | 11 |
| autopilot | module | 43 | 5 |
| gateway-security | module | 42 | 4 |
| augment | module | 41 | 7 |
| polish | module | 40 | 4 |
| recipe | module | 40 | 6 |
| document | module | 36 | 7 |
| archive | module | 36 | 6 |
| memory | module | 33 | 4 |
| benchmark | module | 30 | 5 |
| synth | module | 29 | 4 |
| gateway-ai | module | 29 | 2 |
| gateway-engineering | module | 29 | 2 |
| forge | module | 27 | 3 |
| provenance | module | 25 | 3 |
| blueprint | module | 25 | 2 |

## Top 15 Relationships (highest co-occurrence weight)

| Entity A | Entity B | Weight |
|---|---|---|
| guard | verifier | 6 |
| executor | verifier | 6 |
| executor | guard | 6 |
| archive | executor | 5 |
| archive | guard | 5 |
| archive | verifier | 5 |
| executor | specify | 5 |
| benchmark | document | 4 |
| guard | instinct | 4 |
| instinct | synth | 4 |
| 100/100 | instinct | 4 |
| executor | recipe | 4 |
| augment | recipe | 3 |
| augment | document | 3 |
| augment | executor | 3 |

---

## Expansion rule

Do not add a 4th entity type until 50+ drawers exist AND a real query fails because the missing type would have answered it.
