# Module Plan — Homowabian (L6)

**Tier:** 2 — CORE
**Layer:** L6 Expression
**v5.3 origin:** Named expression of v5.3 Invariant 7 (compression by default). Formalized as standalone module in v6.1. Separated from Economy.

---

## Purpose

Govern voice register and expression style across all module output. Four levels: lite, full, ultra, normal. Homowabian controls HOW output sounds. Economy controls output density. These are orthogonal — Homowabian full can still be dense. Normal prose can still be compressed.

---

## Activation

`skill-rules.json` triggers:
- Any output generation by any module
- Explicit register change request (`/homowabian lite|full|ultra|normal`)
- Auto-switch conditions (Attestation, security warnings, irreversible actions)

---

## Register Definitions

### lite
Brief, direct, status-oriented. Used for progress updates, confirmations, and short responses.

Characteristics:
- Fragments acceptable
- No preamble, no closing
- State result, state next step
- Drop articles, drop filler
- Example: "Wave 3 complete. 4 files written. Starting Wave 4."

### full
Dense planning synthesis. Used for complex multi-part plans, spec writing, analysis.

Characteristics:
- Structured sections with headers
- Technical depth preserved
- Tables and lists preferred over prose
- No filler, no hedging
- Example: Full module plan documents (like this file)

### ultra
Maximum compression. Used for module-to-module handoffs, internal receipts, machine-readable output.

Characteristics:
- No prose explanation
- Data and decisions only
- Single-line entries per item
- No headers unless structurally required
- Example: receipt fields, routing decisions, error events

### normal
Plain prose. Required for code, commits, security warnings, irreversible action confirmations, exact technical instructions.

Characteristics:
- Standard written English
- Full sentences, full articles
- Context and explanation included where needed
- No compression artifacts
- Example: commit messages, security advisories, user-facing error messages with resolution steps

---

## Auto-Switch Rules

These override any active register. Homowabian cannot suppress them.

| Condition | Forced register | Reason |
|---|---|---|
| Code block output | normal (for the block) | Code must be exact — compression changes meaning |
| Git commit message | normal | Commits are shared artifacts |
| Security warning | normal | Clarity required for safety |
| Irreversible action confirmation | normal | User must fully understand before acting |
| Attestation verification mode | normal | Human sign-off requires unambiguous language |
| PR or issue content | normal | Shared external artifacts |

After auto-switch block completes: return to prior register.

---

## Register Selection Guidance

| Context | Recommended register |
|---|---|
| Session progress update | lite |
| Planning synthesis | full |
| Spec writing | full |
| Module-to-module handoff | ultra |
| Receipt content | ultra |
| Error event body | ultra (type field) + normal (message field) |
| User-facing explanation | lite or full depending on complexity |
| Code, commits, security | normal (forced) |

---

## Outputs

Homowabian does not produce artifacts. It transforms output in-place before delivery. All module output passes through Homowabian before reaching user or next module.

---

## Workflow

```
1. Receive output from any module

2. Check auto-switch conditions:
   -> Code block? -> apply normal for block, restore after
   -> Security/irreversible/Attestation? -> apply normal for block, restore after

3. Check active register (session state or explicit override)

4. Apply register transformation:
   -> lite: strip preamble, strip closing, compress to fragments where safe
   -> full: structure with headers/tables, remove filler
   -> ultra: strip all prose, data only
   -> normal: pass through with standard prose cleanup only

5. Return transformed output

6. Log register if override was applied (Economy owns log)
```

---

## Sub-Components

| Component | Type | Purpose |
|---|---|---|
| `SKILL.md` | Required | Orchestration |
| `skill-rules.json` | Required | Activation — passive on all output |
| `references/register-examples.md` | Reference | Examples of each register for each context type |
| `rules/auto-switch.md` | Rules | Complete auto-switch conditions list |
| `rules/register-guidance.md` | Rules | Context to register mapping |
| `schemas/receipt.schema.json` | Schema | Receipt extension |

---

## Integration Points

| Module | Relationship |
|---|---|
| Economy | Orthogonal. Economy compresses density. Homowabian adjusts voice. Homowabian reads Economy's compression level to ensure they do not conflict. Economy reads Homowabian register to skip compression in normal mode. |
| All L0-L7 modules | Passive layer on all output. Every module output passes through. |
| Verifier | Attestation verification mode forces normal register. |
| Reviewer | Reviewer writes in full register for analysis, normal for escalation notices. |

---

## Verification Mode

**Observation** — output register matches context. Auto-switch conditions applied correctly. No normal-register content compressed. No code blocks altered by register transformation.

---

## Receipt Extension Fields

```json
{
  "active_register": "lite|full|ultra|normal",
  "auto_switch_applied": "boolean",
  "auto_switch_reason": "string",
  "register_overrides": "integer"
}
```

---

## v5.3 Mapping

| v5.3 Invariant 7 (compression by default) | v6.1 Homowabian |
|---|---|
| Compression = density + voice combined | SEPARATED: density -> Economy, voice -> Homowabian |
| lite/full/ultra compression levels | lite/full/ultra/normal register levels |
| Normal for security/irreversible | Same auto-switch rules |
| No named identity | Named: Homowabian |
| No module — embedded in Economy | Standalone L6 module |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Register persistence | Session-scoped vs. per-command | Per-module planning |
| Register inheritance | Child modules inherit parent register vs. each module declares own | Per-module planning |
| ultra register for user-facing output | Allowed vs. restricted to module-to-module only | Per-module planning |
