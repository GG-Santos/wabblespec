# Platform Extension/Plugin — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Extension/Plugin as the primary target,
When platform-extension is invoked,
Then it surfaces: "platform-extension requires Recipe to have identified Extension/Plugin as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Extension/Plugin as the primary target,
When platform-extension activates,
Then the activation sequence completes in order: extension type detection → spec-template load → engineering load → security load → Verifier gate registration → receipt write.

## Extension type routing: browser extension MV3

Given `manifest.json` with `manifest_version: 3` is detected,
When platform-extension detects the extension type,
Then MV3 manifest and service worker lifecycle constraints are activated.
Then the spec notes that MV3 service workers are ephemeral — no persistent background connection.

## Extension type routing: browser extension MV2

Given `manifest.json` with `manifest_version: 2` is detected,
When platform-extension detects the extension type,
Then MV2 context is activated.
Then the spec flags this for MV3 migration and records `mv2_migration_required: true` in the receipt.

## Extension type routing: VS Code extension

Given `.vscodeignore` or `activationEvents` in `package.json` is detected,
When platform-extension detects the extension type,
Then VS Code extension context is activated.
Then extension host process isolation is addressed.

## Extension type routing: JetBrains plugin

Given `plugin.xml` is detected,
When platform-extension detects the extension type,
Then IntelliJ/JetBrains plugin context is activated.

## Extension-specific concerns injected into spec

Given platform-extension is active,
When spec context is assembled,
Then manifest permission scope is declared: minimum required permissions only.
Then content security policy is declared: no inline scripts, no remote code execution.
Then cross-origin messaging validation is addressed: messages from content scripts validated.
Then store review requirements are declared (Chrome Web Store / Firefox Add-ons / Marketplace).
Then host sandbox limitations are declared.

## MV3 service worker lifecycle declared

Given a browser extension MV3 is the detected type,
When spec context is assembled,
Then the spec declares that the service worker is ephemeral and cannot maintain persistent connections.
Then any state that must persist across service worker restarts is stored via `chrome.storage` or equivalent.
Then the spec does not rely on in-memory state surviving between service worker activations.

## Permission minimization declared

Given platform-extension is active,
When spec context is assembled,
Then each requested permission is justified in the spec.
Then broad host permission (`<all_urls>`) requires explicit justification.
Then permissions not required at install time are declared as optional permissions with a request-on-demand pattern.

## Capability handoff

Given platform-extension has activated,
When the capability handoff is declared in the receipt,
Then `.wabblespec/engine/shared/dev/frameworks/extension/core.md` is always loaded.
Then gateway-aesthetic/references/ and gateway-experience/references/ are included only when popup or options UI work is in scope.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-extension attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-extension run,
Then platform-extension does not allow inline scripts in MV3 extension content.
Then platform-extension does not allow remote code loading in browser extensions.
Then platform-extension does not omit permission scope declaration.

## Receipt fields

Given any successful platform-extension activation,
Then a receipt is written to `.wabblespec/state/receipts/platform-extension-<timestamp>.json`.
Then the receipt contains: platform, extension_type_detected, manifest_version, permission_scope_declared, csp_declared, mv2_migration_required, gates_registered, capability_handoff.
