# Session Scope

**target:** Library-Package
**complexity:** Medium
**locked_at:** 2026-05-28T16:00:00Z
**session_id:** queue-orchestrator-20260528

## In Scope

- queue-orchestrator.py with populate/ready/advance/status/run subcommands
- CLAUDE.md entry for the new script

## Out of Scope

- SKILL.md modifications
- Changes to wave-queue.py
- Actual Agent tool invocation (that remains in Claude Code Executor)

## Assumptions

- queue-orchestrator.py delegates queue writes to wave-queue.py — no duplicate lock logic
- ready command output is consumed by Executor skill to fire parallel Agent calls

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
