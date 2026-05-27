# L0 — Foundation

Entry layer. Every pipeline run starts here. L0 modules run before anything else and produce the session context that all downstream layers consume.

## Modules

| Module | Role |
|--------|------|
| `recipe` | Captures the raw task. Detects platform target, complexity, vagueness. Entry point for all pipeline runs. |
| `product` | Declares the product identity: name, audience, platform, constraints. Loaded once per product, reused across sessions. |
| `ground` | Pre-execution check. Verifies the task card is coherent and safe to proceed before Executor wave 1. Blocks if something is wrong. |
| `runtime-probe` | Detects available runtime capabilities and writes `runtime-state.json`. Eight vendor-neutral capability descriptors. Never writes model names. |
| `reference-load-l0` | Loads external reference material at session start. L0 variant runs before L1 reference-load. |

## Key behaviors

**Recipe** is always the first module in a pipeline run. It determines:
- `platform`: which L3 platform package activates
- `complexity`: Low / Medium / High — drives Decompose wave count and gateway requirement
- `input_vague`: if true, Enhance (L1) runs before ScopeFrame

**Ground** is the safety gate before Executor. For Medium/High complexity tasks, ground must PASS before wave 1 runs. It reads the task card and wave plan and confirms:
- Scope is defined and bounded
- Wave plan has declared checkpoints
- No contradictions between task card and wave plan

**Runtime-probe** writes `.wabblespec/state/runtime/runtime-state.json`. Model-router (L2) reads this to select capabilities. User overrides via `runtime.json` at project root.

## Receipts

- `recipe-receipt-{run-id}.json`
- `ground-receipt.json` (single, overwritten on each ground check)
- `runtime-probe-receipt-{timestamp}.json`

## Layer rules

- L0 modules may not depend on L1+ modules
- Ground blocks Executor — it does not block Recipe or ScopeFrame
- Runtime-probe is idempotent; safe to re-run any time
