# Security Warning Format

Required format and behavior for all security warnings in UI copy. This is a compliance requirement, not a style preference.

## Acknowledgment requirement

A security warning that can be closed or dismissed without the user actively acknowledging it is non-compliant. Required acknowledgment structure:

1. The warning must state the specific risk (not "this may be unsafe")
2. The user must take an explicit action to proceed (checkbox, typed confirmation, or confirmation button that names the action)
3. A "close" or "X" button must not be the only dismissal option for CRITICAL warnings

## Severity tiers

| Severity | Risk type | Acknowledgment required |
|---|---|---|
| `info` | Informational, no action required | None — dismiss allowed |
| `warning` | Potential data loss or security risk | Confirmation button naming the action |
| `error` | Active problem requiring resolution | Resolution action; no dismiss |
| `critical` | Irreversible or high-impact security risk | Typed confirmation or checkbox + confirm button |

## Copy format by severity

### warning
```
{Specific risk description}.
{What will happen if user proceeds}.
[Cancel] [Proceed with {action}]
```

### error
```
{What is wrong} — {why it is a security issue}.
{Required resolution step}.
[{Resolution action}]
```

### critical
```
{Risk name}: {Specific description of what could be compromised}.
This action {consequence}. {Irreversibility statement if applicable}.
□ I understand that {consequence}
[Cancel] [{Explicit action verb}]
```

## Examples

**Warning — exposing API key:**
```
Sharing this link will expose your API key to anyone who opens it.
Anyone with the key can make requests on your behalf.
[Cancel] [Share link and expose key]
```

**Critical — deleting account:**
```
Account deletion: All your data, projects, and settings will be permanently deleted.
This action cannot be undone. Your account cannot be recovered.
□ I understand that my data cannot be recovered
[Cancel] [Permanently delete account]
```

## Prohibited patterns

- "Are you sure?" without stating what will happen — prohibited
- "This action cannot be undone" without specifying the action — prohibited
- Generic "security warning" without naming the specific risk — prohibited
- Dismiss button as primary action on CRITICAL warnings — prohibited
