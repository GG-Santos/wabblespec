# Guard and Economy

Two cross-cutting policies that every module must respect: Guard governs what operations are permitted, Economy governs output density.

## Guard policy

Guard (L2) is the runtime enforcement layer. It reads `_shared/infrastructure/guard-policy.md` at cold-start and enforces risk tiers across all module operations.

### Risk tiers

| Tier | Definition | Default action |
|------|-----------|----------------|
| CRITICAL | Irreversible, affects shared state, or risks data loss | BLOCK. Require explicit human confirmation. |
| HIGH | Hard to reverse, or affects multiple modules/files | WARN. Surface to human. Proceed only on acknowledgment. |
| MEDIUM | Reversible but non-trivial to undo | LOG. Record in Guard receipt. Do not block. |
| LOW | Routine read/write within declared scope | PERMIT. No logging. |

### Default CRITICAL operations
- Deleting files or directories
- Force-pushing to git remote
- Dropping or truncating database tables
- Writing outside the project root
- Commands with `--force`, `-f`, `rm -rf` patterns
- Overwriting an existing receipt

### Default HIGH operations
- Modifying `framework.yaml`
- Modifying `_shared/` files
- Writing to another module's directory without declared authority
- Committing changes outside declared wave scope
- Running migrations on non-dev environments

### Five guard layers

Guard enforces five nested scope boundaries, from outermost to innermost:

1. **System boundary** — no writes outside the project root
2. **Framework boundary** — no writes to `.wabblespec/` except by modules with declared authority
3. **Module boundary** — a module writes only to its `authority.owns` paths
4. **Wave boundary** — Executor writes only to paths declared in the current wave plan
5. **Receipt boundary** — written receipts are never overwritten

### Completion promise

A module that starts a process must do one of three things:
1. Complete it and write a receipt (PASS)
2. Fail explicitly with a documented reason (FAIL receipt)
3. Escalate to human with a documented block reason (BLOCKED receipt)

There is no fourth option. "Partially done" is FAIL with documented partial state.

## Economy policy

Every output token must carry information. No decorative prose, no restatements, no padding.

### Output size thresholds

| Size | Action |
|------|--------|
| < 500 tokens | Paste inline. No capture. |
| 500–2000 tokens | Paste inline with compression. |
| > 2000 tokens | Capture to `.wabblespec/captures/{module}-{timestamp}.txt`. Paste summary + citation path. |

Token estimate: 1 token ≈ 4 chars prose, ≈ 3 chars code.

### What to preserve
- Code blocks (verbatim)
- File paths and identifiers
- Exact numeric values
- Error messages and stack traces (always verbatim, never summarized)
- Schema field names and enum values

### What to drop
- Context restatements
- Transition prose ("This means that...")
- Explanations of what built-in tools do
- Hedging on certain facts

### Error output rule
Stack traces, compiler errors, test failures, schema validation errors — always pasted verbatim. If over 2000 tokens: capture AND paste inline. Both.

## Version tracking

Archive has exclusive write authority over `.wabblespec/VERSION`.

Semver bump rules:
| Signal in session | Bump |
|-------------------|------|
| Any receipt has `change_class: BREAKING` | Major (`x.0.0`) |
| Any receipt has `change_class: ADDITIVE` or `DEPRECATION`, no BREAKING | Minor (`0.x.0`) |
| Only COSMETIC changes or no classification | Patch (`0.0.x`) |

Worst signal wins across all receipts in the session.
