# Verification Patterns

How to verify artifacts at depth. Existence alone is insufficient — an artifact that exists, contains stub code, is orphaned from the rest of the system, or is wired but produces no real output is not verified.

Sourced from: `research/ref-eval/get-shit-done-redux.md` → B8, B9, wiring patterns.

---

## 4-Level Verification Framework

Every artifact that renders dynamic data or provides functional behavior must pass all four levels. Utilities, configs, and documentation need only Levels 1–2.

| Level | Question | What it catches |
|---|---|---|
| 1 — Exists | File at declared path? | Missing artifact |
| 2 — Substantive | Real implementation, not stub or placeholder? | Placeholder code passing existence check |
| 3 — Wired | Connected to the rest of the system? | Orphaned artifact that is never called |
| 4 — Functional | Actually produces real output when invoked? | Hollow wiring — connected but data doesn't flow |

**When to run Level 4:** Only for artifacts that pass Levels 1–3 AND render dynamic data or produce functional output (command outputs, script results, generated artifacts). Skip Level 4 for: pure configuration files, documentation, schema definitions, static templates.

**Final artifact status:**

| Exists | Substantive | Wired | Functional | Status |
|---|---|---|---|---|
| ✓ | ✓ | ✓ | ✓ | VERIFIED |
| ✓ | ✓ | ✓ | ✗ | HOLLOW — wired but output disconnected |
| ✓ | ✓ | ✗ | — | ORPHANED — exists and real, but never called |
| ✓ | ✗ | — | — | STUB — placeholder code |
| ✗ | — | — | — | MISSING |

HOLLOW and ORPHANED are distinct from STUB and MISSING — they indicate the pattern was partially adopted but the integration is incomplete.

---

## Level 2 — Universal Stub Detection Patterns

These patterns indicate placeholder code regardless of language or artifact type.

**Comment-based stubs:**
```
TODO, FIXME, PLACEHOLDER, not implemented, coming soon
```

**Empty returns:**
```
return null, return {}, return [], return None
pass  (body is only pass)
...   (body is only ellipsis)
```

**Log-only implementations:**
Functions or methods whose entire body is only logging calls with no other action.

**Hardcoded values where dynamic content is expected:**
Static string literals used in place of computed values, especially when the surrounding code has parameters or configuration that would imply dynamic output.

**Missing required fields:**
Schemas, configs, or structured outputs that are declared but have only one or two populated fields when the declared contract requires many.

---

## Level 3 — Wiring Verification Patterns

For each connection type, verify both sides: the producer's output shape and the consumer's expectation. A connection described as "A calls B" is not verified. "A calls B with `{field_x, field_y}` and B returns `{result_z}` which A then uses" is verified.

### Pattern: Consumer → Provider

The consumer calls the provider. The provider's output is used (not ignored).

**Positive indicators:**
- Call exists with non-empty arguments
- Response is assigned, awaited, or piped
- Response is used downstream (not immediately discarded)

**Negative indicators (connection is HOLLOW):**
- Call exists but response is immediately discarded
- Call is commented out
- Call uses a hardcoded or empty argument

### Pattern: Producer → Storage

A producer writes to a store (file, database, state). The store contains real data (not empty or hardcoded).

**Positive indicators:**
- Write call exists with dynamic content
- Result is committed or confirmed
- A reader can retrieve what was written

**Negative indicators:**
- Write exists but with static/empty content
- Write call is present but never awaited
- Result is written but immediately overwritten with a static value

### Pattern: Handler → Action

An event handler (CLI flag, config key, trigger condition) is wired to an action. The action executes when the handler fires, not just logs or no-ops.

**Positive indicators:**
- Handler calls the action function/method/script
- Action function has non-trivial body
- The path from handler to action has no dead code between them

**Negative indicators (STUB wiring):**
- Handler exists but action body is empty or only logging
- Handler body is `pass`, `...`, or returns immediately
- Handler calls a function that itself is a stub

### Pattern: State → Output

A state variable or intermediate result is read and incorporated into the final output.

**Positive indicators:**
- State variable appears in the output construction path
- Output varies when state varies (not hardcoded)
- State is populated from a real source (not initialized to empty and never updated)

**Negative indicators:**
- State variable is declared and updated but never read in the output path
- Output renders a different variable than the one populated by the data source

---

## Level 4 — Functional / Data-Flow Verification

For artifacts that pass Level 3, verify the data source actually produces real output. The most common failure: wiring is present, but the source returns empty, static, or hardcoded data.

**Data-flow status:**

| Data source | Produces real data | Status |
|---|---|---|
| Real query or computation found | Yes | FLOWING |
| Fetch exists but returns static fallback only | No | STATIC |
| No data source found | — | DISCONNECTED |
| Output hardcoded at the call site | No | HARDCODED |

**What to check:**
1. Identify the data variable the artifact uses for output.
2. Trace where that variable is set.
3. Verify the source of that assignment is a real query or computation, not a static value.
4. Verify the result of the query is actually passed to the output path.

---

## When Human Verification is Required

Some things cannot be verified programmatically. Always route to human verification for:

- Visual appearance (does this render correctly?)
- User flow completion (can the user actually do the thing end-to-end?)
- Real-time behavior (WebSocket, streaming, event-driven)
- External service integration (real API calls, authentication flows)
- Performance feel (response time perception)
- Error message clarity (is the message actually helpful?)

Route to human verification when uncertain about:
- Complex connections that cannot be traced without running the system
- Dynamic behavior that depends on external state
- Edge cases and error states in interactive systems

---

## Scope Reduction Language — Stub Indicator

When reviewing artifact content, these phrases signal intentional underdelivery when found in implementation artifacts. Flag them for manual review if found in wave output:

`static for now`, `hardcoded for now`, `placeholder`, `not yet wired`, `will be wired later`, `coming soon`, `TODO`, `FIXME`, `v1`, `simplified version`, `basic version`, `minimal implementation`

These are not automatically FAIL — context matters. A scaffold file with `TODO` during an early wave is expected. The same pattern in a final wave artifact is a stub.
