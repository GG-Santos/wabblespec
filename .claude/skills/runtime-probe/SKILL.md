---
name: runtime-probe
description: Detects available runtime capabilities and writes runtime-state.json with nine vendor-neutral capability descriptors. Never writes model names — only capability descriptors. ModelRouter reads runtime-state.json to select the right capability for each task shape. User can override via runtime.json.
---

# RuntimeProbe

You detect what the current runtime can do and record it as capability descriptors. You never record model names, provider names, or platform-specific identifiers. ModelRouter reads your output; ModelRouter never reads model identity.

## What this skill does

Detects available runtime capabilities and writes runtime-state.json with nine vendor-neutral capability descriptors. Never writes model names — only capability descriptors. ModelRouter reads runtime-state.json to select the right capability for each task shape. User can override via runtime.json.

## When to use

- Session start for any multi-wave execution
- `/runtime-probe` command
- ModelRouter signals missing or stale runtime-state.json
- runtime-state.json older than declared staleness threshold

## Nine capability descriptors

Every capability is binary: available or unavailable. Confidence indicates how reliably you detected it.

| Descriptor | What it means |
|---|---|
| `code-generation` | Can write, complete, and refactor code across common languages |
| `analysis` | Can analyze code, data, documents for patterns, defects, compliance |
| `synthesis` | Can synthesize information from multiple sources into structured artifacts |
| `instruction-following` | Can follow multi-step structured instructions reliably (recipes, checklists) |
| `reasoning` | Can reason through multi-step problems with intermediate steps |
| `tool-use` | Can invoke declared tools with structured input/output |
| `vision` | Can process images, screenshots, diagrams |
| `embedding` | Can produce vector embeddings for semantic similarity |
| `context7` | Can retrieve up-to-date library documentation via ctx7 CLI or context7 MCP server |
| `serena` | Can perform semantic code navigation via LSP (find-references, go-to-definition, list-symbols) |
| `playwright` | Can automate browser interactions and capture screenshots for E2E verification |
| `github-mcp` | Can manage GitHub PRs and issues; post inline review comments |
| `linear-mcp` | Can read/write Linear issues for task card population and archive sync |

## Detection approach

Probe each capability through a minimal behavioral test — not by reading model identity. Detection methods:

| Capability | Detection signal |
|---|---|
| code-generation | Attempt small code completion — pass if syntactically correct output |
| analysis | Attempt structured pattern identification — pass if structured response |
| synthesis | Attempt multi-source summary — pass if coherent synthesis produced |
| instruction-following | Provide numbered checklist — pass if all steps followed in order |
| reasoning | Pose multi-step problem — pass if intermediate steps visible |
| tool-use | Check if tool invocation mechanism is available in current context |
| vision | Check if image input is accepted in current context |
| embedding | Check if embedding generation is available in current context |
| context7 | Check for `resolve-library-id` / `get-library-docs` in available tools (MCP); if absent, check `ctx7` binary on PATH (CLI). MCP preferred over CLI when both present. |
| serena | Check for `serena_find_references` or `serena_list_symbols` in available MCP tools. |
| playwright | Check for `playwright_navigate` or `playwright_screenshot` in available MCP tools. |
| github-mcp | Check for GitHub MCP tools (e.g., `create_pull_request`, `list_issues`) in available tools. |
| linear-mcp | Check for Linear MCP tools (e.g., `linear_get_issue`, `linear_update_issue_status`) in available tools. |

If detection is uncertain, record as available with confidence < 0.7 and note uncertainty.

## Reference Routing

| Situation | Reference |
|---|---|
| RuntimeProbe receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type runtime-probe` |

## Output contract

Write to `.wabblespec/state/runtime/runtime-state.json`:

```json
{
  "probed_at": "ISO 8601",
  "capabilities": {
    "code-generation": { "available": true, "confidence": 0.95 },
    "analysis": { "available": true, "confidence": 0.95 },
    "synthesis": { "available": true, "confidence": 0.9 },
    "instruction-following": { "available": true, "confidence": 0.95 },
    "reasoning": { "available": true, "confidence": 0.85 },
    "tool-use": { "available": true, "confidence": 0.95 },
    "vision": { "available": false, "confidence": 0.9 },
    "embedding": { "available": false, "confidence": 0.9 },
    "context7": { "available": false, "detection": "none", "confidence": 0.95 }
  },
  "overrides_applied": false,
  "override_source": null
}
```

## User overrides

If `.wabblespec/state/runtime/runtime.json` exists, apply its declarations over probe results:

```json
{
  "overrides": {
    "vision": { "available": true, "confidence": 1.0 },
    "embedding": { "available": true, "confidence": 1.0 }
  }
}
```

Overridden fields: set `overrides_applied: true`, set `override_source: "runtime.json"`. Record which fields were overridden in the receipt.

## What never appears in output

- Model names (`claude-sonnet-4-6`, `gpt-4o`, etc.)
- Provider names (`Anthropic`, `OpenAI`, etc.)
- Platform-specific API identifiers
- Version numbers

ModelRouter uses capability descriptors only. Any module that needs to route by capability reads runtime-state.json — never queries model identity.

## What not to do

- Do not write model names or provider names anywhere
- Do not skip detection — do not assume capabilities without probing
- Do not write runtime-state.json without probing (or applying declared overrides)
- Do not block session start if runtime-state.json already exists and is FRESH — reuse it
