# System Prompt Tiers

Three-tier naming convention for system prompt assembly. Consumers: Apply, Executor, any module that assembles or contributes to the system prompt.

---

## The three tiers

| Tier | Content | Cache lifetime |
|---|---|---|
| stable | Identity, tool guidance, skill descriptions, environment hints. Does not change during a session. | Session-long |
| context | Project-specific instructions (CLAUDE.md, task card, spec artifacts), caller-supplied system message. Changes between tasks, not between turns. | Task-long |
| volatile | Memory snapshot, user profile, timestamp, session ID. Changes frequently or per-turn. | Short / per-turn |

## Assembly order

Always assemble in this order: `stable` → `context` → `volatile`.

Cache-stable content must come before cache-volatile content. Placing volatile content inside the stable tier invalidates prefix caches on every turn.

## Rules

- **Volatile content never goes in stable.** A timestamp, memory block, or session ID belongs in volatile. Putting it in stable busts the upstream KV-cache every turn.
- **Stable content is built once per session.** If a stable-tier element can change mid-session, it is not stable — move it to context or volatile.
- **Context tier can be session-stable.** If CLAUDE.md and the task card do not change within a session, the context tier is effectively stable for that session. The tier names describe update frequency, not absolute mutability.

## Placement decisions

| Item | Tier | Why |
|---|---|---|
| Framework invariants | stable | Never changes per session |
| Guard policy | stable | Never changes per session |
| Skill module descriptions | stable | Loaded once; skill set does not change mid-session |
| CLAUDE.md | context | Project-specific; changes between projects |
| Active task card | context | Changes between tasks, not between turns |
| Wave plan | context | Updated per task; not per turn |
| Memory drawer content | volatile | Changes as evidence is updated |
| Timestamp / session ID | volatile | Per-session or per-turn |

## Anti-patterns

| Anti-pattern | Cost | Fix |
|---|---|---|
| Timestamp in stable tier | Cache miss every turn | Move timestamp to volatile |
| Memory snapshot in stable tier | Stale memory after first turn | Move to volatile; prefetch per turn |
| Task card in stable tier | Stale card if task changes | Move to context; reload on task change |
| Volatile content baked in at module load time | Incorrect context for the session | Resolve volatile content at invocation, not at module load |

## Cross-references

- `context-engineering.md` — what to load and where to position it in context
- `context-optimization.md` — KV-cache optimization technique list
- `context-budget.md` — when to change load strategy based on context health
