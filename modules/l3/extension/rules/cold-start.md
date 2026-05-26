# Cold-Start Behavior — Platform Extension/Plugin

Defines how the extension/plugin platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `_shared/dev/frameworks/extension/core.md` missing.
Detection: File read returns 404.
Action: Log warning. Apply continues without MV3 manifest rules, service worker constraints, and message validation requirements. Decompose proceeds.
Do NOT: Fail the session.

## Absent: security reference files

Condition: `modules/l3/extension/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic controls. Message validation (always check type) and host permission minimization remain enforced as platform invariants.

## Absent: spec-template files

Condition: `modules/l3/extension/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `manifest_version` | MV3 required — MV2 is a BLOCK for new extensions |
| `target_browser` | Not declared — Specify must elicit (Chrome / Firefox / Edge / All) |
| `permissions` | Minimum viable set — Specify must enumerate required permissions; over-broad = FLAG |
| `host_permissions` | Not declared — Specify must declare; `<all_urls>` is a BLOCK without justification |
| `message_validation` | Required — all `chrome.runtime.onMessage` handlers must validate `message.type` |
| `content_script_csp` | Enforced: no inline scripts, no eval in content scripts |
| `service_worker_lifetime` | 5 min idle timeout enforced by browser — no persistent background state assumption |

MV3 requirement and message validation are platform invariants — enforced even without framework files.
