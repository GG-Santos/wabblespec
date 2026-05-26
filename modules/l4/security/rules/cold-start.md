# Cold-Start Behavior — Gateway Security

Defines how gateway-security behaves when expected upstream artifacts are absent.

## Absent: gateway-spec-receipt (Phase A not yet run)

Condition: `gateway-security-spec-receipt.json` absent from `.wabblespec/receipts/` when Phase B is triggered.
Detection: Phase B checks for spec receipt before running verdict.
Action: Block Phase B — surface DEPENDENCY error: "Phase A (security analysis) must complete before Phase B verdict." Route back to Specify to complete Phase A.
Do NOT: Issue a verdict without Phase A having run. A verdict without threat model context is invalid.

## Absent: spec to evaluate

Condition: No spec.md exists in `specs/` when Phase A is triggered.
Detection: Specify receipt exists but specs directory is empty or all specs are drafts.
Action: Produce a minimal Phase A output with status INFORM, noting that security analysis requires a populated spec. List the required spec sections (endpoints, data model, auth strategy).

## Absent: reference files

Condition: `references/threat-modeling.md`, `references/owasp.md`, `references/continuous-security.md`, or `references/compliance.md` absent.
Detection: File read returns 404 during Phase A.
Action: Log which files are absent. Proceed with available reference files only. Note in Phase A receipt which reference files were missing.
Do NOT: Block Phase A entirely for missing references. Use whatever is available.

## Absent: cycling reference files (Red/Blue/Purple)

Condition: `references/cycling/red-protocol.md`, `blue-protocol.md`, or `cycle-protocol.md` absent.
Detection: User activates `/security-red` or `/security-cycle` but files not found.
Action: Surface error: "Cycling protocol files missing — cannot activate Red/Blue/Purple mode." Do not improvise a cycling protocol.

## Absent: rules files (auth-policy, secrets-policy)

Condition: `rules/auth-policy.md` or `rules/secrets-policy.md` absent during Phase B.
Detection: File read returns 404.
Action: Log: "Gateway rule file missing: [path]. Phase B verdict issued without this rule set." Proceed with available rules. Missing rule files reduce verdict coverage but do not block the verdict.

## Default state on cold start

| Field | Default |
|---|---|
| `phase_a_status` | `pending` — until spec-receipt written |
| `verdict` | `pending` — until Phase B complete |
| `cycling_mode` | `inactive` — requires explicit `/security-red` or `/security-cycle` activation |
| `score` | null — until first Purple scoring completes |
| `critical_count` | 0 — assumed; actual count from Red findings |

No security verdict defaults are assumed. Every verdict requires explicit Phase B execution.
