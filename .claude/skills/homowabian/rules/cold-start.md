# Cold-Start Behavior — Homowabian

Defines how Homowabian register activation behaves when its configuration is absent.

## Absent: CLAUDE.md register declaration

Condition: No Homowabian register line in CLAUDE.md.
Detection: CLAUDE.md scan finds no `homowabian:` or register declaration.
Action: Default to `normal` register. Log: "No Homowabian register declared — using normal."
Do NOT: Activate lite, full, or ultra register without explicit declaration.

## Absent: SKILL.md (module definition missing)

Condition: `modules/l6/homowabian/SKILL.md` missing.
Detection: File read returns 404.
Action: Fall back to default register behavior (normal). Log: "Homowabian SKILL.md missing — register defaults apply."

## Register defaults (applied even without configuration)

| Register | Behavior |
|---|---|
| `normal` | Standard response length; all capabilities active |
| `lite` | Reduced length target; no extended analysis |
| `full` | Extended analysis permitted; higher token budget |
| `ultra` | Maximum depth; no brevity constraints |

## Default state on cold start

| Field | Default |
|---|---|
| `register` | `normal` — unless declared in CLAUDE.md |
| `activation` | Passive — no skill invocation needed; reads CLAUDE.md on session open |
| `override` | User can switch register mid-session via explicit instruction |
