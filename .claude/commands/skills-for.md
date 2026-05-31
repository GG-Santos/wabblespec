---
description: Filter the WabbleSpec skill catalog by domain tag, layer, or theme keyword.
argument-hint: <tag, theme, or layer (e.g. "spec", "L2", "memory", "review", "platform")>
---

Filter the WabbleSpec skill catalog by the tag, theme, or layer below.

Filter:
$ARGUMENTS

Match against the taxonomy below. A single argument may match multiple themes. Return every skill that matches.

---

## Layer filter

Match `L0` through `L8` or `shared` to filter by layer directly.

| Layer | What lives there |
|---|---|
| L0 | Product entry: runtime-probe, recipe, product, ground, reference-load-l0 |
| L1 | Spec core + analysis: scope-frame, specify, enhance, sharpen, brainstorm, plan, propose, interview, explore, decompose, reference-load, apply, shift, sync, organize, flag, analyze, perf, deps, api, migrate, test, clean, triage |
| L2 | Orchestration + review: executor, verifier, guard, inference-guard, adversary, reviewer, grader, audit, autopilot, team-plan, model-router, ensemble, rollback, economy, wave-reviewer, wave-fix, wave-refine, ref-eval, ref-plan, ref-adopt, ref-comp, framework-maintenance |
| L3 | Platform packages: platform-web, platform-api-service, platform-cli, platform-mobile, platform-desktop, platform-library, platform-extension, platform-data-pipeline, platform-ai-agent, platform-iot, platform-game |
| L4 | Capability gateways: gateway-security, gateway-engineering, gateway-ai, gateway-aesthetic, gateway-design, gateway-experience |
| L5 | Memory: memory, memory-search, provenance, entity-graph, dream, memory-mine, forget, nexus |
| L6 | Expression: document, polish, proofread, markdown, copy, writer, legal, translate, optimize, market, homowabian, research-log |
| L7 | Delivery: archive, scaffold, deploy, package, release, monitor, watzup, changelog, commit |
| L8 | Evolution: instinct, synth, blueprint, factory, augment, benchmark, benchmark-loop, forge, retro, feedback, skill-tdd |
| shared | Dev infrastructure: shared-dev-languages, shared-dev-databases, shared-dev-api-consumption |

---

## Theme taxonomy

Match any theme tag below. A prompt like "spec" matches all spec-theme skills.

```
entry / session / start      → recipe, runtime-probe, watzup, economy, ground, clean
spec / plan / task            → scope-frame, specify, enhance, sharpen, brainstorm, plan, propose, interview, decompose
execute / run / wave          → executor, apply, rollback, wave-fix, wave-refine, scaffold
review / quality / gate       → guard, verifier, adversary, reviewer, grader, audit, inference-guard
wave-review / async-review    → wave-reviewer, wave-fix, wave-refine
memory / knowledge / evidence → memory, memory-search, provenance, entity-graph, dream, memory-mine, forget, nexus, research-log, reference-load, reference-load-l0
change / drift / diff         → shift, sync, organize, flag, migrate, api
analysis / root-cause / debug → analyze, triage, perf, deps, explore, nexus, audit
orchestration / multi-agent   → autopilot, team-plan, model-router, ensemble, economy
evolution / L8                → instinct, synth, blueprint, factory, augment, benchmark, benchmark-loop, forge, retro, feedback, skill-tdd
content / expression / text   → document, polish, proofread, markdown, copy, writer, legal, translate, optimize, market, homowabian, changelog
delivery / release / ship     → archive, deploy, package, release, commit, changelog, watzup
reference / adopt / research  → ref-eval, ref-plan, ref-adopt, ref-comp, reference-load, reference-load-l0, research-log
platform / build              → platform-web, platform-api-service, platform-cli, platform-mobile, platform-desktop, platform-library, platform-extension, platform-data-pipeline, platform-ai-agent, platform-iot, platform-game
gateway / security / design   → gateway-security, gateway-engineering, gateway-ai, gateway-aesthetic, gateway-design, gateway-experience
```

Additional tag aliases:
```
enforcement / invariant       → guard, inference-guard, verifier
spec / task-card / criteria   → specify, scope-frame, decompose
breakage / breaking / compat  → shift, api, sync
versioning / semver           → api, shift, archive, release
receipt / artifact            → verifier, executor, archive, guard
token / context / budget      → economy, autopilot, model-router
staleness / expiry            → memory, dream, guard, provenance
flags / rollout               → flag
performance / perf            → perf, optimize, economy
compliance / gdpr / legal     → audit, legal, deps, gateway-security
i18n / translation            → translate
seo / discoverability         → optimize
marketing / go-to-market      → market
routing / dispatch            → recipe, model-router, autopilot, recommend
tdd / testing / fixture       → skill-tdd, test, benchmark
```

---

## Output format

```
**Skills for "<filter>"**:

| Skill | Why it matches | Layer | Notes |
|-------|----------------|-------|-------|
| <name> | <one-line relevance> | L<N> | active / gate-required / L8-gated |

**Suggested first invocation**:
> "<a one-line prompt you can paste directly into Claude Code that uses the top match>"
```

---

## Notes column legend

- **active** — available in the current session without preconditions
- **gate-required** — needs a prior phase receipt (e.g., specify-receipt for executor; decompose-receipt for executor Wave 1)
- **L8-gated** — L8 evolution skills; corpus gate MET but promotion of individual modules still requires benchmark PASS
- **on-stop** — runs automatically via stop hook (dream, memory-mine, entity-graph); invoke manually only for forced refresh
- **background** — typically daemon-run (wave-reviewer async path); can be triggered manually

If the filter does not match any theme or tag, return the closest matches from the taxonomy, list the unmatched filter, and suggest 2-3 nearby tags.

If the filter matches more than 12 skills, group results by sub-theme rather than listing all in a flat table.
