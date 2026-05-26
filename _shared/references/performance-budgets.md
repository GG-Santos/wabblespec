---
name: performance-budgets
description: Cross-platform SLO declaration patterns and guidance. Reference for Monitor, Engineering gateway, and L3 platform modules. Defines how to express performance budgets so they are machine-consumable by Monitor's SLO codification step.
---

# Performance Budgets Reference

This document defines how WabbleSpec projects declare performance budgets (SLOs). Monitor's `Step 1 — Extract SLO declarations` reads these files. Engineering gateway's Phase B loads them for quality gate evaluation.

## Consumer modules

| Module | How it uses performance budgets |
|---|---|
| `l7/monitor` | Reads `engineering/performance-budgets.md` to generate metric definitions, alert rules, and dashboard templates |
| `l4/engineering` | Reads declared budgets to verify Engineering quality gates (latency budget declared, error rate target present) |
| `l3/web` | References CWV budgets (LCP/CLS/INP) during spec generation |
| `l3/api-service` | References p99 latency and error rate during spec generation |
| `l3/cli` | References cold-start and memory ceiling during spec generation |

## Where to place budget files

Each project has a single performance budget file at the path Monitor expects:

```
{project-root}/engineering/performance-budgets.md
```

Scaffold creates this file (empty) for each new project. Fill it in before running Monitor or before Engineering gateway Phase B.

Platform-specific templates: `_shared/templates/engineering/performance-budgets-{platform}.md`

## SLO declaration format

Each SLO is declared as a named block with a `target:` line Monitor can parse. Undeclared dimensions are marked `___ UNDECLARED` — Monitor will mark them `UNDECLARED` in generated configs rather than inventing targets.

```markdown
## {dimension-name}

**Target:** {value} {unit} at {percentile} over {window}
**Rationale:** {why this target — must be user-outcome linked, not arbitrary}
**Measurement:** {how this is measured in production}
**UNDECLARED** (use this when target has not been set)
```

## SLO tiers

Choose the tier that matches your deployment context. Do not pick a tighter tier than you can maintain — unreachable SLOs produce alerts that are ignored.

| Tier | Use case | Latency P99 | Error rate | Availability |
|---|---|---|---|---|
| **Tier 1 — Critical path** | Payments, auth, primary product action | < 200ms | < 0.1% | 99.9% |
| **Tier 2 — Standard** | Core product features, API endpoints | < 500ms | < 1% | 99.5% |
| **Tier 3 — Background** | Async jobs, non-real-time processing, internal APIs | < 5s | < 5% | 99% |

## Monitor-specific rules

From `modules/l7/monitor/SKILL.md`:

1. **Monitor derives, never invents.** If no SLO is declared for a dimension, Monitor marks it `UNDECLARED` and does not generate an alert with a guessed threshold.
2. **Every generated alert must have a runbook reference.** Stub file acceptable on first run.
3. **Alert thresholds match declared targets exactly.** Do not tighten or loosen without changing the budget file.
4. **No PII in log schema.** Declare PII fields explicitly so Monitor excludes them.

## Engineering gateway rules

From `modules/l4/engineering/rules/code-quality-policy.md`:

- If no performance budget exists: Engineering gateway WARNS — not having a budget is a gap, not a block.
- If budget exists but latency target is undeclared for a user-facing path: FLAG.
- If observed latency in receipts consistently misses a declared target: surface as finding.

## Web platform (CWV)

Core Web Vitals are the authoritative performance budgets for web projects. Declare them using Google's threshold tiers:

| Metric | Good | Needs Improvement | Poor |
|---|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5s | 2.5s–4.0s | > 4.0s |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| INP (Interaction to Next Paint) | ≤ 200ms | 200ms–500ms | > 500ms |

Target for new projects: all three in "Good" tier.

## API-Service platform

Standard SLO pattern for HTTP/gRPC services:

```
p50 latency < 50ms
p95 latency < 200ms
p99 latency < 500ms
Error rate (5xx) < 1% over 5-minute window
Throughput: state expected RPS range
Timeout: declare per-endpoint client timeout
```

## CLI platform

CLI performance budgets are different — users tolerate longer cold start than web users tolerate LCP, but interactive commands have sub-second expectations:

```
Cold start (first output line): < 100ms for tool-level init
Command execution (non-I/O): < 500ms for interactive commands
Memory ceiling: < 100MB for standard operation
Exit code contract: 0 = success, 1 = user error, 2 = system error
```

## IoT / Embedded platform

Resource budgets replace latency SLOs:

```
Flash budget: declare % of available flash (target ≤ 80%)
RAM budget: declare % of available RAM at peak (target ≤ 75%)
Watchdog window: declare watchdog timeout (required — no undeclared watchdog)
Startup time: declare time to first ready signal
```

## PII field declaration

If your project logs or processes PII, declare it here so Monitor excludes it from the log schema:

```markdown
## PII fields (excluded from log schema)

- user_email
- ip_address
- session_token
- payment_card_number
```
