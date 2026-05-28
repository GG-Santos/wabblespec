---
name: agents-architecture
description: Architecture for WabbleSpec skills as Claude Code subagents. Each skill runs in its own context window and returns a validated typed receipt. Orchestrator context sees only the result JSON.
---

# WabbleSpec Skills as Subagents

Each WabbleSpec skill can run as a Claude Code subagent via the Agent tool. The skill runs in its own context window, performs its work, and returns a JSON receipt. The orchestrator (Executor) receives only the receipt JSON — not the skill's internal file operations, reasoning, or intermediate reads.

## Context isolation benefit

A full Archive session currently costs ~40K–80K tokens because all receipts, CHANGELOG context, and wave outputs load into the same window as the orchestrator. As a subagent:

| Component | Orchestrator context | Subagent context |
|---|---|---|
| SKILL.md | Not loaded | Loaded as system prompt |
| Prior wave receipts | Receipt paths only | Loaded as needed |
| CHANGELOG | Never loaded | Loaded if needed |
| Result returned | JSON receipt (< 2KB) | Full work context |

---

## Agent Definition Format

Agent files live in `.claude/agents/<skill-name>.md`. Format:

```yaml
---
name: wabblespec-<skill-name>
description: <skill description — used by Agent tool to select this agent>
model: claude-sonnet-4-6
---
```

Body: the full SKILL.md content, plus an **Output Protocol** section at the end:

```markdown
## Output Protocol (Subagent Mode)

When invoked as a subagent, your final message MUST be valid JSON conforming
to the receipt schema for this skill. No trailing prose after the JSON block.

Example final output:
```json
{ "status": "PASS", "module": "verifier", ... }
```
```

---

## Calling Pattern (Executor)

Executor invokes skills via the Agent tool:

```
Agent(
  subagent_type="claude",
  description="Run Verifier on Wave 1 output",
  prompt="[Verifier inputs + wave plan entry + task card]"
)
```

The agent's return value is the JSON receipt. Executor writes it to the receipts directory using `receipt-writer.py --from-json`.

---

## Output Validation

`agent-output-validator.py` validates the returned JSON against the skill's receipt schema before Executor records it:

```bash
python .wabblespec/engine/shared/scripts/agent-output-validator.py \
  --type verifier \
  --json '{"status": "PASS", ...}'
# Exit 0 = valid, 1 = schema violation, 2 = parse error
```

---

## Pioneer Skills (Implemented)

| Skill | Agent file | Reason |
|---|---|---|
| verifier | `.claude/agents/wabblespec-verifier.md` | Bounded check, clear output schema |
| guard | `.claude/agents/wabblespec-guard.md` | Pattern-matching check, well-defined verdicts |

---

## Migration Path

| Stage | Approach |
|---|---|
| Phase 5-6 (now) | Pioneer agents defined; Executor can call them optionally |
| Phase 7 | Daemon skills (staleness sweep, memory mining) run as `--bg` agents |
| Phase 9 | Wave tasks become queue items executed by worker subagents in parallel |

---

## Cross-references

- Agent validator: `.wabblespec/engine/shared/scripts/agent-output-validator.py`
- Pioneer agent — verifier: `.claude/agents/wabblespec-verifier.md`
- Pioneer agent — guard: `.claude/agents/wabblespec-guard.md`
- Receipt schemas: `.wabblespec/engine/shared/schemas/`
