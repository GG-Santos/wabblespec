# Domain Pack Specification

Status: Optional / Future
Source pattern: `financial-services-main` plugins + managed-agent-cookbooks

A domain pack is a self-contained vertical extension to WabbleSpec. It adds domain-specific skills and agents without modifying any core module. Core remains unchanged whether or not a pack is installed.

---

## What a domain pack is

A domain pack bundles:

- A plugin manifest (`plugin.json`)
- One or more agent system prompts
- Domain skills (each with `SKILL.md` + `skill-rules.json`)
- A deployment cookbook (`agent.yaml` + `subagents/*.yaml`)

It does NOT:

- Modify any file under `modules/`
- Modify `framework.yaml` or `BUILD-PLAN.md`
- Override shared schemas or references under `_shared/`
- Require live data connectors (MCP servers for external APIs are optional and deployment-specific)

---

## Directory layout

```
domain-packs/
  <pack-name>/
    plugin.json
    agents/
      <pack-name>.md
    skills/
      <skill-name>/
        SKILL.md
        skill-rules.json
    cookbook/
      agent.yaml
      subagents/
        <worker-a>.yaml
        <worker-b>.yaml
        <writer-worker>.yaml   # only worker with Write
```

---

## plugin.json

Minimal manifest. No runtime logic.

```json
{
  "name": "<pack-name>",
  "version": "0.1.0",
  "description": "<one-line purpose>",
  "author": {
    "name": "<team or person>"
  }
}
```

---

## agent.yaml (cookbook manifest)

Describes the orchestrator agent for deployment. References skills from the pack's own directory.

```yaml
name: <pack-name>
model: claude-opus-4-7

system:
  file: ../agents/<pack-name>.md
  append: "You are running headless. Produce files in ./out/; do not assume an interactive session."

tools:
  - type: agent_toolset_20260401
    default_config: { enabled: false }
    configs:
      - { name: read,  enabled: true }
      - { name: grep,  enabled: true }
      - { name: glob,  enabled: true }

skills:
  - { from_plugin: .. }   # resolves all skills/ under this pack

callable_agents:
  - { manifest: ./subagents/<worker-a>.yaml }
  - { manifest: ./subagents/<worker-b>.yaml }
  - { manifest: ./subagents/<writer-worker>.yaml }   # only one gets Write
```

MCP servers are deployment-specific. If the pack requires external data, declare `mcp_servers` in the deployment environment — not in this committed manifest.

---

## Subagent manifest (subagents/*.yaml)

Each leaf worker declares its own tools and a bounded output schema.

```yaml
name: <pack-name>-<role>
model: claude-opus-4-7

system:
  text: |
    <Single-role description. State what the worker reads, what it produces,
    and that it does not write files unless it is the designated writer.>

tools:
  - type: agent_toolset_20260401
    default_config: { enabled: false }
    configs:
      - { name: read, enabled: true }
      - { name: grep, enabled: true }
      # Writer worker only: add { name: write, enabled: true }

skills: []
callable_agents: []

output_schema:
  type: object
  required: [<required-fields>]
  additionalProperties: false
  properties:
    <field>: { type: string, maxLength: <N>, pattern: "<safe-pattern>" }
    <list-field>:
      type: array
      maxItems: <N>
      items:
        type: object
        additionalProperties: false
        properties:
          <item-field>: { type: <type> }
```

Rules for output schemas:
- `additionalProperties: false` on every object
- `maxLength` on every string field
- `maxItems` on every array
- Pattern-constrain string fields where possible
- The writer worker does not need an `output_schema` — its output is a file

---

## Delegation rules

Adapted from `financial-services-main` managed-agent-cookbooks README:

1. **One level only.** Orchestrator calls workers. Workers do not call further subagents.
2. **Write isolation.** Only one leaf worker has `Write` enabled. All other workers are read-only.
3. **No direct agent-to-agent calls.** When one agent needs to hand off to another, it emits a structured `handoff_request` in its output. An external orchestrator (or the Recipe router) routes it as a new activation event.

---

## Skill rules (skill-rules.json)

Each domain skill follows the canonical WabbleSpec skill-rules schema:

```json
{
  "module": "<skill-name>",
  "layer": "domain-pack",
  "tier": 2,
  "activators": ["<trigger phrase>"],
  "anti_activators": [],
  "preconditions": [],
  "build_targets": ["ALL"],
  "phases": [],
  "stages": [],
  "authority": {
    "owns": [],
    "reads": []
  },
  "verification_mode": "Audit",
  "receipt_required": false,
  "collapse_eligible": true,
  "invariants": [],
  "produces": [],
  "depends_on": [],
  "consumed_by": [],
  "loading_gate": "activation",
  "commands": [],
  "file_path_patterns": []
}
```

`layer` is `"domain-pack"` — not a core layer (L0–L8). This keeps domain skills out of the core module graph.

---

## Recipe routing

Recipe detects domain-pack activators by scanning `skill-rules.json` files under `domain-packs/`. Domain packs register the same way as core skills. Recipe routes to the pack orchestrator when an activator fires. No core module is modified.

If no domain pack is installed, Recipe routing is unaffected.

---

## Isolation contract

A domain pack MUST NOT:

- Import from or depend on a specific core module by path
- Write to `.wabblespec/receipts/` (receipt namespace is core-only)
- Override `framework.yaml` entries
- Assume live external API connectivity (MCP connectors are deployment-optional)

A domain pack MAY:

- Reference shared schemas under `_shared/schemas/` as read-only
- Reference shared references under `_shared/references/` as read-only
- Produce its own receipts under a pack-namespaced path (e.g., `.wabblespec/domain-packs/<pack-name>/receipts/`)

---

## What was not taken from financial-services-main

- Live MCP connector declarations (`capiq`, `daloopa`) — financial-specific, deployment-specific
- `deploy-managed-agent.sh` and `orchestrate.py` — infrastructure scripts, not a framework pattern
- Partner-built plugin structure (`plugins/partner-built/`) — third-party integration, not a pack authoring pattern
- `steering-examples.json` format — financial-specific evaluation artifact, no equivalent in WabbleSpec yet
- Financial-specific output schema fields (tickers, EV multiples, NAV) — domain content, not structural pattern
