---
name: homowabian
description: Register control for WabbleSpec output tone. Switches between lite/full/ultra/normal response modes. One CLAUDE.md line activates. Module exists for documentation only — complexity has not grown enough to warrant skill logic.
---

# Homowabian

Controls the register (tone density) of WabbleSpec output. Analogous to caveman mode for the framework's own voice.

## What this skill does

Register control for WabbleSpec output tone. Switches between lite/full/ultra/normal response modes. One CLAUDE.md line activates. Module exists for documentation only — complexity has not grown enough to warrant skill logic.

## Registers

| Register | Use when | Output style |
|---|---|---|
| `normal` | Default | Full sentences, complete explanations, all context included |
| `lite` | Experienced user, familiar task | Key steps only, no rationale unless asked |
| `full` | New task class, unfamiliar territory | All rationale, all context, all warnings |
| `ultra` | Extremely dense — fragments only | Like caveman mode: no articles, no hedging, technical substance only |

## When to use

One line in CLAUDE.md or project settings:

```
WabbleSpec register: lite
```

No skill invocation required. The register applies to all WabbleSpec module output in the session.

## What changes between registers

**Receipt output:** Always machine-format (JSON). Register does not affect receipts.

**Module output to user:** Affected. `lite` drops rationale sections. `ultra` drops all prose, keys only.

**Gate output:** `lite` and `ultra` show pass/fail per gate, no remediation steps unless a gate fails. `normal` and `full` show all.

## When NOT to compress (regardless of active mode)

Drop to full prose for:
- Security warnings or gateway-security Phase B verdicts (BLOCK, CRITICAL, CVE)
- Irreversible action confirmations (Rollback restore, Forget hard_delete, Deploy to production)
- Multi-step sequences where fragment order or omitted conjunctions risk technical misread
- User confusion signals (repeated question, explicit clarification request)

Resume terse mode after the critical section is complete.

## Current status

Module complexity has not grown beyond this SKILL.md. No skill-rules.json activation logic needed — register is a passive setting, not an invocable skill. Revisit if: register logic becomes conditional on task type, or if per-module register overrides are needed.

## Output contract

Writes a receipt to `.wabblespec/receipts/` on successful completion.
