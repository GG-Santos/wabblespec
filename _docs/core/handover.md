# Handover

Clean-slate briefing for resuming WabbleSpec v6.1 work in a new session. Copy this into the session start when context is lost.

---

## What this project is

WabbleSpec v6.1 is a receipt-gated, spec-driven execution framework built on Claude Code. Every task runs through a fixed pipeline (Recipe → ScopeFrame → Specify → Decompose → [Gateway] → Executor → Verifier → Archive). No task is complete without an Archive delivery receipt. The framework governs itself — all 99 modules are registered in `framework.yaml`, all have passing quality floor checks.

## Current state (VERSION 0.3.6)

- **99 modules** registered in `framework.yaml`, all `build_status: built`
- **96/96 modules** pass the quality floor (all `L\d+` layers; `layer: shared` modules are excluded)
- **19 PASS receipts** accumulated across 3 complete pipeline runs
- **L8 gate:** 19/100 — NOT cleared (needs 100+ PASS receipts + 3 human-validated Instinct patterns)
- **Integration gate (Phase 5-6):** 3/10 complete runs — NOT cleared

## What was just done

See `.wabblespec/CHANGELOG.md` for the authoritative record. Summary of recent work:
- Front 3: Promoted 9 deferred modules (monitor, deploy, package, release, polish, memory-mine + 3 gateways) to `build_status: built`
- Front 2: Gateway leaf plan written and executed — all 6 gateways are rules-only (no leaf skill modules)
- Front 1: Built `validate-graph.py` and `quality-floor-check.py`; caught and fixed A7 violation and BOM issue; 30 quality floor failures resolved to 0

## Where things live

| What | Where |
|------|-------|
| Module registry | `framework.yaml` |
| Module specs | `modules/l{N}/{name}/SKILL.md` |
| Module rules | `modules/l{N}/{name}/skill-rules.json` |
| Receipts | `.wabblespec/receipts/` |
| Current task card | `.wabblespec/plans/task-card.md` |
| Current wave plan | `.wabblespec/plans/wave-current.md` |
| Quality floor checker | `_shared/scripts/quality-floor-check.py` |
| Graph validator | `_shared/scripts/validate-graph.py` |
| Health reports | `.wabblespec/health/` |
| Changelog | `.wabblespec/CHANGELOG.md` |
| Version | `.wabblespec/VERSION` |
| Hooks | `hooks/pre-tool-use-receipt-check.py`, `modules/l2/executor/hooks/post-wave-receipt-check.py` |

## What's next

1. **More pipeline seed runs** — need 10+ complete runs to clear Integration gate (Phase 5-6); need 100+ PASS receipts for L8 gate
2. **Integration Phases 5-6** — gated on 10+ real receipt runs; once cleared, integration work can resume
3. **L8 evolution** — gated on 100+ receipts + 3 human-validated Instinct patterns + benchmark schema

## Key rules to not violate

- Never skip a receipt. A stage is not done until its receipt is written.
- Never write to another module's `authority.owns` paths.
- Archive is the only module that bumps VERSION.
- Never amend a written receipt — receipts are append-only.
- `framework.yaml` shared file consumers must be valid module IDs (A7 rule) — never script paths.
- Run `validate-graph.py` after any `framework.yaml` change.

## How to resume a pipeline run

1. Check `.wabblespec/receipts/` for the most recent run-id
2. Find which stages are missing receipts
3. Resume from the first missing stage
4. If the last stage was Executor without Verifier/Archive: run verifier first, do not re-run Executor

## Useful commands

```bash
# Quality floor check
python _shared/scripts/quality-floor-check.py --framework framework.yaml

# Validate framework graph
python _shared/scripts/validate-graph.py --framework framework.yaml

# Check module specifically
python _shared/scripts/quality-floor-check.py --framework framework.yaml --module {id} --verbose

# Count PASS receipts
ls .wabblespec/receipts/ | grep -c delivery
```
