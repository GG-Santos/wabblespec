# Flag Commands

Four modes. Each maps to a specific lifecycle transition.

## create

```
/flag create --id <flag_id> --description <text> --sunset <condition>
```

Creates a new flag in DRAFT state. Writes entry to `flag-manifest.json`. Required parameters:
- `--id`: unique flag identifier, kebab-case (e.g., `new-auth-flow`)
- `--description`: what behavior the flag gates
- `--sunset`: condition or date when flag should be retired

Output: flag-receipt with `mode: create`, `previous_state: null`, `new_state: DRAFT`.

---

## rollout

```
/flag rollout --id <flag_id> [--pct <0-100>] [--cohort <cohort-name>]
```

Transitions flag from DRAFT to ROLLING or ACTIVE. Runs rollout gate before proceeding.

- `--pct 100` or no pct argument → ACTIVE (full rollout)
- `--pct <N>` where N < 100 → ROLLING at N%
- `--cohort <name>` → ROLLING for named cohort

Output: flag-receipt with `mode: rollout`, `rollout_gate_passed: boolean`, `new_state: ACTIVE | ROLLING`. If gate fails: receipt with `status: FAIL`, gate conditions listed.

---

## audit

```
/flag audit [--id <flag_id>]
```

Reviews current flag state against lifecycle rules. Without `--id`: audits all flags in manifest. With `--id`: audits one flag.

Flags as stale: any flag in ACTIVE or ROLLING state that has no recorded progress toward retirement in the last 30 sessions (estimated).

Output: flag-receipt with `mode: audit`. Lists stale flags, ROLLING flags with no monitoring evidence, flags missing sunset condition.

---

## retire

```
/flag retire --id <flag_id> [--remove-code]
```

Transitions flag from ACTIVE or ROLLING to RETIRED. Updates `flag-manifest.json`. 

- `--remove-code`: signals that the flag-gated code should be permanently merged (remove the flag check). Does not do the code change — records the intent in receipt for Executor to carry out.
- Without `--remove-code`: flag is marked RETIRED but code cleanup is deferred.

Output: flag-receipt with `mode: retire`, `new_state: RETIRED`.
