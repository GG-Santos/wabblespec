# ADR-0001 — I11: Framework and Product Space Are Permanently Separated

- **Status**: Accepted
- **Date**: 2026-05-26
- **Invariant**: I11 — FRAMEWORK AND PRODUCT NEVER MIX
- **Enforced by**: Guard (pre-wave authority check), PreToolUse hook (`pre-tool-use-receipt-check.py`)
- **Reviewers**: Derivable from session history; no single-session decision — accumulated across seed runs

---

## Context

WabbleSpec maintains two distinct namespaces in every repository:

- **Framework space** — `.wabblespec/` and all files under it (`wabblespec.yaml`, `engine/`, `state/`). Owned exclusively by framework modules. The module registry (`wabblespec.yaml`) is the canonical source of truth for all 99 modules. If it is corrupted or overwritten mid-session, Guard cannot enforce invariants and the entire receipt chain loses its authority anchor.

- **Product space** — project root excluding `.wabblespec/`, `.claude/`, and `.git/`. Any root-level directory or file not starting with one of those prefixes is product space. Owned by product-space tasks executing under Executor waves. Product receipts are written to `.wabblespec/state/receipts/` by the framework (not by product task code), but actual code/artifact output goes to product space only.

Without a hard boundary, the following failure modes are possible:

1. A task Executor wave writing to `project/` also touches `framework.yaml` (intentionally or by accident), invalidating the module registry for the rest of the session. Guard cannot detect the corruption because the corrupting write has already happened.

2. A product-space test suite that creates fixture files in `.wabblespec/` contaminates the receipt index with synthetic entries, making the Verifier's receipt chain check unreliable.

3. An Autopilot wave that writes session state while a product wave is mid-execution produces a race condition on `session/state.json`.

4. A Synth candidate during L8 evolution modifies its own module's `skill-rules.json` without the Attestation gate, bypassing I8's staged evolution chain.

---

## Decision

`.wabblespec/` is framework space. Project root (excluding `.wabblespec/`, `.claude/`, `.git/`) is product space. **No product-space task writes to `.wabblespec/`, ever.** Framework modules write receipts and state; product task code writes only to product space.

Product-space modules declare `"product_space": true` in their `skill-rules.json` authority block instead of enumerating `"owns"` globs. Guard translates this to: any path not prefixed with `.wabblespec/`, `.claude/`, or `.git/` is authorized.

The boundary is enforced at two layers:

1. **Guard pre-wave** — Guard's authority check reads the executing module's `skill-rules.json`. If `authority.product_space == true`, any path outside `.wabblespec/`, `.claude/`, `.git/` is authorized. Explicit `authority.owns` globs are also supported for modules with narrower authority. Any write targeting `.wabblespec/` from a non-framework module is a HARD error (type: `AUTHORITY_VIOLATION`).

2. **PreToolUse hook** — `pre-tool-use-receipt-check.py` intercepts every Edit/Write/Bash/MultiEdit call and checks whether the target path is inside `.wabblespec/`. If it is, and the current session has no active framework module with authority over that path, the hook emits a warning injection.

Framework modules that legitimately write to `.wabblespec/` are identified by their `authority.owns` declarations in `skill-rules.json`. Those declares are the allowlist.

---

## Alternatives Considered

### Convention only (no enforcement) — Rejected

A documented convention ("don't write to `.wabblespec/` from product tasks") with no enforcement is not a guard, it is a suggestion. Empirical evidence from seed runs: without enforcement, product task code drifted into writing `framework.yaml` on run #4 of the seed sequence when an Executor wave's output contract was ambiguously specified. The drift was silent until Verifier caught a receipt mismatch two waves later. Enforcement is non-negotiable.

### Single allowlist file enumerating permitted paths — Rejected

A static allowlist file (e.g., `.wabblespec/engine/shared/references/framework-paths.json`) enumerating every framework-owned path is too brittle for 99 modules across 8 layers. Every new module addition or path change would require allowlist maintenance, and a stale allowlist is worse than no allowlist (it produces false negatives). The `authority.owns` field in each module's `skill-rules.json` is the correct data structure — it is already validated by `validate-graph.py` and the quality floor gate.

### Path prefix gate only (no module-level authority) — Rejected

A simple `.wabblespec/` prefix guard (any write to this prefix is blocked from product space) is necessary but not sufficient. It does not address the inverse: a framework module accidentally writing to the product directory (e.g., writing a receipt to product space instead of `.wabblespec/state/receipts/`). The bidirectional authority model (owns + reads declared per module) catches both directions.

---

## Consequences

### Positive

- Framework registry (`wabblespec.yaml`) has guaranteed integrity across all execution waves.
- Receipt chain is always written by framework modules, never by product code. Receipts are authentic artifacts.
- Guard's pre-wave authority check is cheap and deterministic: O(n) scan of the wave's planned write targets against the module's declared owns list.
- New module authors get a clear, machine-checkable contract: declare your `authority.owns` paths, write only to those paths.

### Negative

- Module authors cannot write framework files during product task execution. If a module needs to update its own configuration as part of a product task, it must do so through a separate framework task (new Recipe, new task card). This adds friction for self-modifying framework modules (most relevant for L8 evolution chain).
- The PreToolUse hook adds latency to every Edit/Write/Bash call (~20-50ms). For large wave plans with many file writes, this accumulates.

### Neutral

- The boundary does not restrict reading. Product-space modules may read `.wabblespec/` files (receipts, task card, wave plan) to ground their work in spec. The restriction is writes only.

---

## Operational Notes

- If Guard emits `AUTHORITY_VIOLATION`, the correct response is to inspect the planned write targets in the wave plan and move any `.wabblespec/` writes to the appropriate framework module (usually the Executor's receipt write, which it already owns via `authority.owns`).
- The `validate-graph.py --check-hashes` script detects drift in module files after they are written. It does not prevent writes but surfaces them at validation time.
- I11 is non-negotiable. It is not subject to per-task overrides or `collapse_eligible` flags.
