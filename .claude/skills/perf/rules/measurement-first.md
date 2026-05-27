# Measurement First

No optimization claim is valid without a measured baseline. This rule has no exceptions.

## The rule

Before any optimization work begins: measure current performance with the method appropriate for the platform. Record the baseline. The baseline is the reference against which all claims are evaluated.

**Baseline must be true when:** `baseline_measured: true` in the receipt. If false: the receipt status is FAIL regardless of other findings.

---

## Why

"It's slow" is a symptom. "P95 latency is 450ms against a 200ms SLO budget" is a measurement. Optimization without measurement produces:
- Premature optimization (improving things that are not the bottleneck)
- Unverifiable claims ("it's faster now" without numbers)
- Regressions (unmeasured code paths that slowed down while the measured path improved)

---

## What counts as a baseline measurement

A baseline is valid when it:
1. Was measured in the same environment as the performance budget (prod-equivalent, not local dev)
2. Uses the same measurement method as the budget (same tool, same metric type)
3. Covers the full critical path (not just the hot loop in isolation)
4. Is repeatable (same measurement taken 3× with consistent results — no single-run flukes)

A baseline that fails any of these conditions must be labeled as "preliminary" in the receipt and cannot be used to make optimization claims.

---

## Measurement tools by platform

| Platform | Primary tool |
|---|---|
| Web (browser) | Lighthouse, WebPageTest, Chrome DevTools Performance |
| API / backend | wrk, k6, Apache Bench, platform APM (Datadog, Prometheus) |
| CLI | hyperfine |
| Mobile (iOS) | Instruments (Time Profiler, Allocations) |
| Mobile (Android) | Android Studio Profiler |
| IoT / embedded | hardware timer, logic analyzer |
| Game | engine profiler (Unity Profiler, Unreal Insights) |

Use the tool declared in `platform_budget_applied` if already defined. If no budget exists, select the tool and declare it in the receipt.

---

## Regression detection

After optimization: re-measure all paths that were measured in the baseline, not just the optimized path. Record `regressions_detected: N`. A regression in an unoptimized path is a new bug introduced by the optimization work.
