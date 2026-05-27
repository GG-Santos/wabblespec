# Cold-Start Behavior — Platform Web

Defines how the web platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/web/core.md` or `.wabblespec/engine/shared/dev/frameworks/web/security.md` are missing from the repository.
Detection: File read returns 404 during Apply routing phase.
Action: Log warning — "Web framework file missing: [path]". Apply continues with reduced context. Do not block Decompose.
Do NOT: Fail the session. Missing framework files reduce context quality but do not prevent execution.

## Absent: conditional framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/web/nextjs.md` (or react/vue/svelte) missing when the detected signal matches.
Detection: Signal detected (e.g., `next.config.*` found) but framework file absent.
Action: Proceed without the conditional framework file. Log: "Conditional framework file not found: [path] — proceeding without it."
Do NOT: Manufacture framework guidance from training data alone. Use only what the file would have contained if present.

## Absent: security reference files

Condition: `modules/l3/web/security/threat-model.md` or `security/platform-controls.md` absent.
Detection: File read returns 404.
Action: Surface to gateway-security Phase A: security reference files missing for web platform. Gateway-security should use generic OWASP controls from `references/owasp.md` as fallback.
Do NOT: Skip security analysis. Use fallback references.

## Absent: spec-template files

Condition: `modules/l3/web/spec-template/design-document.md` (or systems-design/technical-spec) absent.
Detection: Specify module requests template, file not found.
Action: Specify falls back to generic template structure. Log: "Web spec-template not found — using generic structure."
Do NOT: Block spec creation. Specify can write a spec without a platform-specific template.

## Default state on cold start

| Field | Default |
|---|---|
| `rendering_strategy` | Not declared — Specify must elicit (CSR / SSR / SSG / ISR) |
| `auth_strategy` | Not declared — Specify must elicit |
| `framework` | Not declared — Apply detects from repo signals |
| `csp_mode` | `report-only` until enforcing mode declared in spec |
| `target_env` | Not declared — Specify must elicit (browser / server / both) |

No defaults are written to state.json by the platform module directly. All defaults become Specify questions if absent from spec.
