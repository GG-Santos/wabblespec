# Cold-Start Behavior — Guard

Defines what Guard does when its expected upstream artifacts are absent.

## Absent: AGENT.md

Condition: The requesting module has no `AGENT.md` file.
Detection: File read returns 404 for `modules/{layer}/{module}/AGENT.md`.
Action: Load `guard-policy.md` defaults for authority rules. Do not block the wave solely on AGENT.md absence — authority is declared in `skill-rules.json`, not AGENT.md.
Output: Guard proceeds with `skill-rules.json` as the sole authority source.

## Absent: skill-rules.json

Condition: The requesting module has no `skill-rules.json`.
Detection: File read returns 404 for `modules/{layer}/{module}/skill-rules.json`.
Action: HARD error — Layer 4 authority check cannot proceed. I5 violation.
Do NOT: Assume authority based on module name or past behavior.

## Absent: prior receipts

Condition: Wave N has no Wave N-1 receipt in `.wabblespec/state/receipts/`.
Detection: Expected receipt stem missing.
Action: DEPENDENCY error — surface I10 violation, pause wave, name the missing upstream receipt.
Do NOT: Skip the I10 check because Wave N-1 "probably ran."

## Absent: scope.md

Condition: `.wabblespec/scope.md` does not exist when Guard runs Layer 2.
Detection: File read returns 404.
Action: DEPENDENCY error — ScopeFrame must run before any wave is guarded. Layer 2 cannot run without scope boundaries.
Do NOT: Default to "all files in scope."

## Default state on cold start

| Layer | Default when artifacts absent |
|---|---|
| Layer 1 (schema) | Run normally — schema is embedded in Guard, not external |
| Layer 2 (scope) | DEPENDENCY error if scope.md absent |
| Layer 3 (invariants) | Run against `.wabblespec/engine/shared/references/invariants.md`; if absent, DEPENDENCY error |
| Layer 4 (authority) | HARD error if skill-rules.json absent |
| Layer 5 (command risk) | SKIP if wave plan has no shell commands; DEPENDENCY error if policy file absent |
