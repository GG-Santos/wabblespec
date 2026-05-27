# Cold-Start Behavior — Autopilot

Defines what Autopilot does when its expected upstream artifacts are absent.

## Absent: session state

Condition: `.wabblespec/session/state.json` does not exist when Autopilot initializes.
Detection: File read returns 404.
Action: Write the initial state.json immediately. Autopilot is the session owner — it creates the session, not inherits it.
Output: Fresh `state.json` with `enforcement_active: true`, `required_receipts: []`, `active_module: "recipe"`.

## Absent: meta.md

Condition: `.wabblespec/meta.md` does not exist.
Detection: File read returns 404.
Action: Create meta.md with defaults from the project root (project name from directory name, no prior sessions).
Output: Fresh `meta.md` with session count: 0 and empty milestone log.

## Absent: prior receipts

Condition: No receipts from any prior session.
Detection: `.wabblespec/receipts/` empty.
Action: Start a fresh session. No DEPENDENCY error — Autopilot is designed to bootstrap from zero.
Do NOT: Refuse to initialize because no prior work exists.

## Default state on cold start

| Field | Default |
|---|---|
| `enforcement_active` | true (always — Autopilot enforces from first tool use) |
| `active_module` | `recipe` (always first module in session) |
| `session_id` | freshly generated |
| `required_receipts` | empty list (populated as modules complete) |
