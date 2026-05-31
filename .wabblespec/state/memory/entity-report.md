# Entity Graph Report

> Generated: 2026-05-31T12:10:51.800224+00:00
> Drawers scanned: 174
> Nodes: 339  Edges: 1268

## Entity Type Breakdown

- concept: 106
- module: 32
- file: 201

## Top 20 Entities by Degree (most connected)

| Entity | Type | Degree | Drawer count |
|---|---|---|---|
| executor | module | 63 | 13 |
| document | module | 61 | 12 |
| specify | module | 59 | 10 |
| guard | module | 56 | 12 |
| instinct | module | 50 | 11 |
| verifier | module | 45 | 12 |
| gateway-security | module | 44 | 5 |
| autopilot | module | 43 | 5 |
| benchmark | module | 43 | 8 |
| memory | module | 42 | 6 |
| augment | module | 41 | 7 |
| polish | module | 40 | 4 |
| recipe | module | 40 | 6 |
| archive | module | 36 | 6 |
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
| benchmark | document | 5 |
| archive | executor | 5 |
| archive | guard | 5 |
| archive | verifier | 5 |
| executor | specify | 5 |
| document | specify | 4 |
| guard | instinct | 4 |
| instinct | synth | 4 |
| 100/100 | instinct | 4 |
| executor | recipe | 4 |
| benchmark | memory | 3 |
| augment | recipe | 3 |

---

## Expansion rule

Do not add a 4th entity type until 50+ drawers exist AND a real query fails because the missing type would have answered it.
