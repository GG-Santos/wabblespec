---
name: research-log
description: Logs research findings as memory drawers with provenance. Use when an Executor wave produces factual evidence worth preserving — API behavior, library constraints, external system behavior, design decisions with evidence. Delegates storage to Memory module.
---

# Research Log

You log research findings. You do not store them yourself — Memory does. You are the interface that formats findings into drawer-ready entries and hands them to Memory.

## When to activate

- During or after a wave where external research was conducted (API docs read, library tested, system behavior observed)
- When a finding will inform future waves or future sessions
- When the same question would otherwise need to be re-researched

**Do not activate for:**
- Internal reasoning or design decisions without external evidence (use Memory directly)
- Findings that are already in an existing FRESH drawer (check MemorySearch first)
- Per-wave implementation notes (those belong in receipts)

## What Research Log produces

One or more drawer entries, each containing:

| Field | Content |
|---|---|
| `topic` | The specific question the finding answers |
| `body` | The finding — concrete, evidence-backed |
| `evidence` | Source: URL, file path, test output, doc version |
| `confidence` | 0.0–1.0 based on evidence quality |
| `staleness_state` | FRESH on creation |
| `expires_at` | Declared when finding has known expiry (e.g., API version) |

## Freshness rules

- If finding depends on a specific library version: set `expires_at` to next major version release estimate
- If finding is from official docs with a version stamp: cite version in evidence
- If finding is from observed behavior with no version anchor: confidence ≤ 0.7, set staleness_state AGING

## Relationship to Memory module

Research Log is a caller of Memory. It formats entries; Memory writes them. If Memory is not active in this session, Research Log writes the entry directly using Memory's drawer schema.

## Receipt

Research Log writes a receipt to `.wabblespec/receipts/research-log-{timestamp}.json` confirming:
- Number of drawers written
- Topics covered
- Confidence range across entries
