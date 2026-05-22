# Priority 1 — Shared Schemas

Infrastructure before modules. Every module references these. Plan these before any module SKILL.md is written.

Three schemas required:
1. `skill-rules.json` — activation and authority declaration
2. `receipt.schema.json` — base receipt structure (module receipts extend this)
3. `error-event.schema.json` — typed error taxonomy

---

## 1. skill-rules.json

Every module package has one. Framework reads it at Gate 4 (Activation). Declares:
- When this module activates
- What build targets it applies to
- What runtime lanes it supports
- What output it owns (authority)
- What verification mode it requires

### Schema

```json
{
  "module": "string — canonical module name",
  "layer": "L0|L1|L2|L3|L4|L5|L6|L7|L8",
  "tier": "1|2|3|4|5",
  "activators": [
    "string — pattern that triggers this module (regex or keyword)"
  ],
  "anti_activators": [
    "string — pattern that suppresses activation even when activators match"
  ],
  "build_targets": [
    "Web|API-Service|Game|Mobile|Desktop|CLI|IoT-Embedded|Library-Package|Extension-Plugin|Data-Pipeline|AI-Agent|ALL"
  ],
  "runtime_lanes": [
    "string — vendor-neutral capability descriptor, not model name"
  ],
  "phases": [
    "Research|Plan|Execute|ALL"
  ],
  "stages": [
    "P1|P2|P3|P4|ALL"
  ],
  "authority": {
    "owns": [
      "string — artifact or output this module exclusively produces"
    ],
    "reads": [
      "string — artifact or output this module consumes but does not own"
    ]
  },
  "verification_mode": "Test|Review|Audit|Measurement|Observation|Attestation|Demonstration",
  "receipt_required": true,
  "collapse_eligible": false,
  "gate_collapsing_conditions": "string — conditions under which Plan+Execute collapse (null if not eligible)"
}
```

### Rules

- `activators` are matched against session context, task shape, and incoming request text
- `anti_activators` take precedence over `activators` when both match
- `build_targets: ["ALL"]` means module applies regardless of target
- `runtime_lanes` uses capability descriptors, never model names (e.g. "code-generation", "analysis", "synthesis")
- `authority.owns` must be unique — no two modules in the same session own the same artifact
- `verification_mode` is required — no module omits it
- `receipt_required: true` for all non-trivial modules. Only utility scripts may set false.
- `collapse_eligible: true` only for modules that support Plan+Execute collapse (see I2)

### Location

```
.wabblespec/modules/<MODULE-NAME>/skill-rules.json
```

For platform packages:

```
.wabblespec/modules/platform/<TARGET>/skill-rules.json
```

For shared infrastructure:

```
.wabblespec/_shared/schemas/skill-rules.schema.json  <- the schema itself
```

---

## 2. receipt.schema.json (Base)

All module receipts extend this base. Platform and module-specific receipts add fields but cannot remove base fields.

### Base Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "module",
    "layer",
    "timestamp",
    "runtime",
    "platforms",
    "phase",
    "stage",
    "inputs",
    "outputs",
    "validation",
    "not_tested",
    "confidence"
  ],
  "properties": {
    "module": {
      "type": "string",
      "description": "Canonical module name"
    },
    "layer": {
      "type": "string",
      "enum": ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8"]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "runtime": {
      "type": "object",
      "required": ["selected", "reason", "task_shape", "available_tools", "fallback", "verification_mode"],
      "properties": {
        "selected": { "type": "string" },
        "reason": { "type": "string" },
        "task_shape": {
          "type": "string",
          "enum": ["creative", "analytical", "code", "conversational", "technical"]
        },
        "available_tools": {
          "type": "array",
          "items": { "type": "string" }
        },
        "fallback": { "type": "string" },
        "verification_mode": {
          "type": "string",
          "enum": ["Test", "Review", "Audit", "Measurement", "Observation", "Attestation", "Demonstration"]
        }
      }
    },
    "platforms": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["Web", "API-Service", "Game", "Mobile", "Desktop", "CLI", "IoT-Embedded", "Library-Package", "Extension-Plugin", "Data-Pipeline", "AI-Agent", "ALL"]
      }
    },
    "phase": {
      "type": "string",
      "enum": ["Research", "Plan", "Execute", "Collapsed"]
    },
    "stage": {
      "type": "string",
      "enum": ["P1", "P2", "P3", "P4", "Execution"]
    },
    "inputs": {
      "type": "array",
      "description": "Upstream receipts and artifacts this execution read",
      "items": {
        "type": "object",
        "required": ["artifact", "source_module", "staleness_state"],
        "properties": {
          "artifact": { "type": "string" },
          "source_module": { "type": "string" },
          "staleness_state": {
            "type": "string",
            "enum": ["FRESH", "AGING", "STALE", "EXPIRED", "NEEDS_REVERIFICATION", "SUPERSEDED"]
          }
        }
      }
    },
    "outputs": {
      "type": "array",
      "description": "Artifacts produced by this execution",
      "items": {
        "type": "object",
        "required": ["artifact", "path"],
        "properties": {
          "artifact": { "type": "string" },
          "path": { "type": "string" }
        }
      }
    },
    "tools_used": {
      "type": "array",
      "items": { "type": "string" }
    },
    "memory_updates": {
      "type": "array",
      "description": "Evidence written to or read from Memory during this execution",
      "items": {
        "type": "object",
        "required": ["operation", "drawer", "staleness_state"],
        "properties": {
          "operation": { "type": "string", "enum": ["write", "read", "invalidate"] },
          "drawer": { "type": "string" },
          "staleness_state": { "type": "string" }
        }
      }
    },
    "validation": {
      "type": "object",
      "required": ["mode", "result", "revise_cycles"],
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["Test", "Review", "Audit", "Measurement", "Observation", "Attestation", "Demonstration"]
        },
        "result": { "type": "string", "enum": ["PASS", "FAIL", "BLOCKED", "SKIPPED"] },
        "revise_cycles": { "type": "integer", "minimum": 0, "maximum": 3 },
        "failure_reason": { "type": "string" },
        "escalation_point": { "type": "string" }
      }
    },
    "not_tested": {
      "type": "array",
      "description": "Explicit list of what was not verified. Required. Empty array is valid only if everything was verified.",
      "items": { "type": "string" }
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence in output correctness. 1.0 = fully verified. < 0.7 = should flag."
    }
  }
}
```

### Module Receipt Extension Pattern

Each module's `schemas/receipt.schema.json` uses `allOf` to extend the base:

```json
{
  "allOf": [
    { "$ref": ".wabblespec/_shared/schemas/receipt.base.schema.json" },
    {
      "type": "object",
      "properties": {
        "module_specific_field": { "type": "string" }
      }
    }
  ]
}
```

### Location

```
.wabblespec/_shared/schemas/receipt.base.schema.json   <- base schema
.wabblespec/modules/<MODULE>/schemas/receipt.schema.json  <- module extension
```

### Receipt File Location

```
.wabblespec/modules/<MODULE>/receipts/MODULE-RECEIPT.md   <- human-readable
.wabblespec/receipts/<MODULE>-<timestamp>.json            <- machine-readable (optional)
```

---

## 3. error-event.schema.json

All modules emit typed errors. Orchestration routes by type.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "module", "message", "timestamp", "recoverable"],
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "SOFT",
        "HARD",
        "DEPENDENCY",
        "CONTEXT_EXHAUSTION",
        "SPEC_VIOLATION",
        "STALENESS_VIOLATION"
      ]
    },
    "module": {
      "type": "string",
      "description": "Module that emitted the error"
    },
    "message": {
      "type": "string",
      "description": "Human-readable error description"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "recoverable": {
      "type": "boolean",
      "description": "Whether execution can continue after this error"
    },
    "upstream_module": {
      "type": "string",
      "description": "For DEPENDENCY errors: which upstream module failed"
    },
    "artifact": {
      "type": "string",
      "description": "For SPEC_VIOLATION or STALENESS_VIOLATION: which artifact triggered the error"
    },
    "staleness_state": {
      "type": "string",
      "enum": ["FRESH", "AGING", "STALE", "EXPIRED", "NEEDS_REVERIFICATION", "SUPERSEDED"],
      "description": "For STALENESS_VIOLATION: the staleness state of the offending evidence"
    },
    "routing": {
      "type": "object",
      "description": "Orchestration routing instructions",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["retry", "halt", "pause", "compress", "loop_back", "quarantine"]
        },
        "target": {
          "type": "string",
          "description": "Where to route: module name, checkpoint label, or spec stage"
        }
      }
    }
  }
}
```

### Error Type to Routing Action Map

| Type | recoverable | routing.action |
|---|---|---|
| SOFT | true | retry |
| HARD | false | halt |
| DEPENDENCY | false | pause |
| CONTEXT_EXHAUSTION | true | compress |
| SPEC_VIOLATION | false | loop_back |
| STALENESS_VIOLATION | false | quarantine |

### Location

```
.wabblespec/_shared/schemas/error-event.schema.json
```

---

## Schema Dependency Graph

```
error-event.schema.json     <- no dependencies
skill-rules.schema.json     <- no dependencies
receipt.base.schema.json    <- no dependencies

receipt.schema.json (per module)
  <- extends receipt.base.schema.json
  <- references skill-rules.json for verification_mode values
```

---

## Open Decisions

None. All three schemas are fully defined. Ready to use for Priority 2 module planning.

---

## Status

| Schema | Defined | Location set | Ready |
|---|---|---|---|
| skill-rules.json | Yes | `.wabblespec/_shared/schemas/` | Yes |
| receipt.base.schema.json | Yes | `.wabblespec/_shared/schemas/` | Yes |
| error-event.schema.json | Yes | `.wabblespec/_shared/schemas/` | Yes |
