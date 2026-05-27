# Agent Architecture Standards

## Tool Declaration

Every tool the agent can call declares:

```markdown
## Tool — <tool-name>

**description:** <what this tool does — used by model for tool selection>
**input_schema:** <JSON Schema>
**output_schema:** <JSON Schema>
**side_effects:** true|false
**reversible:** true|false
**attestation_required:** true|false
```

Tools with `side_effects: true` and `reversible: false` require `attestation_required: true` — human confirmation before execution.

## Tool Selection

Model selects which tool to call. Tool execution is deterministic — does what it declares, unconditionally. Model cannot influence tool behavior through arguments beyond the declared input schema.

## Loop Bounds

Maximum iterations declared for all agent loops. No unbounded loops. Default maximum if not declared: 10 iterations. Reaching maximum is a declared error state with declared fallback — not silent termination.

## Observation Format

Tool output returned to model as structured observation — not raw text:

```json
{
  "tool_name": "string",
  "call_id": "string",
  "status": "success|error",
  "result": {},
  "error": null
}
```

## Human-in-the-Loop

Irreversible tool calls (file deletion, payment, API calls with side effects) require Attestation gate — human confirms before execution. Mirrors invariant I8 applied to agent tool use.

## Audit Gates

- [ ] Every tool has complete declaration (description, input_schema, output_schema, side_effects, reversible, attestation_required)
- [ ] All tools with side_effects:true and reversible:false have attestation_required:true
- [ ] Maximum iterations declared for every agent loop
- [ ] Reaching max iterations routes to declared fallback (not silent termination)
- [ ] Tool observations returned as structured JSON (not raw text)
