# Cold-Start Behavior — Platform Library/Package

Defines how the library/package platform module behaves when its expected framework files or upstream artifacts are absent.

## Absent: capability_handoff framework files

Condition: `.wabblespec/engine/shared/dev/frameworks/library/core.md` missing.
Detection: File read returns 404.
Action: Log warning. Apply continues without semver contract, tree-shaking, and supply chain security rules. Decompose proceeds.
Do NOT: Fail the session.

## Absent: security reference files

Condition: `modules/l3/library/security/threat-model.md` or `security/platform-controls.md` absent.
Action: Gateway-security uses generic controls. Supply chain rules (no postinstall scripts, 2FA on publish) remain enforced as platform invariants.

## Absent: spec-template files

Condition: `modules/l3/library/spec-template/design-document.md` absent.
Action: Specify uses generic structure.

## Default state on cold start

| Field | Default |
|---|---|
| `versioning` | Semver required — MAJOR.MINOR.PATCH; Specify must declare current version and breaking change policy |
| `public_api_surface` | Not declared — Specify must declare which exports are public API (semver-governed) |
| `tree_shaking` | Required for JS/TS libraries — side-effect free unless declared |
| `peer_dependencies` | Not declared — Specify must declare; bundling peer deps is a FLAG |
| `deprecation_policy` | Not declared — Specify must declare notice period (minimum: one minor version) |
| `publish_auth` | 2FA required on npm/PyPI/crates.io; Specify must declare publish account |
| `postinstall_scripts` | Forbidden — no postinstall scripts that execute code |

Semver and no-postinstall-scripts are platform invariants — enforced even without framework files.
