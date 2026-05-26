# L2 — Execution and Control

The enforcement and execution layer. L2 modules run tasks, verify outcomes, enforce policies, and manage session state. Most are invoked by the pipeline, not directly.

## Modules

### Execution
| Module | Role |
|--------|------|
| `executor` | Executes the wave plan wave by wave. Writes to `project/repo/` only. Halts on wave failure. Core pipeline module. |
| `autopilot` | Full lifecycle meta-orchestrator. Owns `.wabblespec/meta.md`. Scale-adaptive autonomy (L0–L4 complexity). Manages phase transitions, triggers Dream post-wave, schedules Evolution. |
| `rollback` | Reverts a wave or execution to a previous checkpoint. Requires a declared rollback target in the wave plan. |

### Verification and quality
| Module | Role |
|--------|------|
| `verifier` | Validates that Executor produced the declared outcomes. Runs checkpoint assertions. Returns PASS, PARTIAL, or FAIL. Core pipeline module. |
| `reviewer` | Code review against spec and engineering standards. Runs REVISE cycles with Adversary+Grader. |
| `grader` | Scores output quality against declared criteria. Used by Reviewer and Benchmark. |
| `adversary` | Generates adversarial test cases and challenge inputs. Works with Grader to surface weaknesses. |
| `audit` | Compliance audit. Checks execution history and receipts against declared policies. |

### Routing and orchestration
| Module | Role |
|--------|------|
| `guard` | Runtime policy enforcement. Applies risk tiers to all operations. Reads `_shared/infrastructure/guard-policy.md`. Five nested scope boundaries. |
| `economy` | Token economy enforcement. Monitors output density against `_shared/infrastructure/economy-principles.md`. |
| `ensemble` | Combines outputs from multiple module runs into a single synthesized result. |
| `model-router` | Selects AI capability tier for each task shape. Reads `runtime-state.json`. Never routes to a named model — routes to capability descriptors. |
| `team-plan` | Coordinates multi-agent or multi-session work. Produces a team execution plan with role assignments. |

## Key behaviors

**Executor** is the only module authorized to write to `project/repo/`. All other modules that produce project artifacts must route through Executor. The post-wave hook (`modules/l2/executor/hooks/post-wave-receipt-check.py`) fires after each tool call to verify wave integrity.

**Guard** enforces five nested scope boundaries. A CRITICAL-tier block halts the entire session — not just the current wave. Guard receipts are written on any WARN or BLOCK event.

**Autopilot** is the orchestrator for multi-stage, multi-session work. It reads the complexity score from Decompose and scales autonomy accordingly: L0 (fully manual) through L4 (fully autonomous within declared scope). Autopilot triggers Dream after each completed wave to capture learnings.

**Verifier** PARTIAL status is not silent acceptance — it escalates to human. A PARTIAL execution is not archived until human reviews and either confirms acceptance or triggers rollback.

## Hooks

- `modules/l2/executor/hooks/post-wave-receipt-check.py` — PostToolUse hook. Fires after Edit/Write/Bash/MultiEdit. Verifies wave receipts are being written correctly.
- `hooks/pre-tool-use-receipt-check.py` — PreToolUse hook (L0-level, not L2). Fires before any write tool call. Both hooks use absolute paths in `.claude/settings.json`.

## Layer rules

- Executor writes only to `project/repo/` — never to `.wabblespec/`
- Guard and Economy run as cross-cutting concerns, not as pipeline stages
- Rollback requires a declared rollback target — cannot roll back without a checkpoint
- Model-router never outputs model names — only capability descriptors
