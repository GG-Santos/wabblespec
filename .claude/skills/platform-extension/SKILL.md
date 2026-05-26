---
name: platform-extension
description: Extension/Plugin platform. Activates when Recipe detects a browser extension, IDE plugin, or host-application plugin target. Loads extension spec templates, engineering rules, security controls, and verification gates specific to sandboxed plugin environments. Produces a materially different spec from Web or CLI targets — focused on MV3 manifest, host sandbox constraints, permission minimization, and content security policy.
---

# Platform: Extension/Plugin

You are the Extension platform layer. You activate when Recipe identifies a browser extension, IDE plugin, or host-application plugin and you load the constraints, templates, and verification gates specific to that target.

## What this skill does

Loads extension-specific spec templates, engineering standards, security controls, and verification gates. Writes a platform activation receipt.

## When to use

Recipe must have already run and identified Extension/Plugin as the primary target. Activation signals in `skill-rules.json`.

## What makes Extension different from other targets

| Concern | Browser Extension | IDE Plugin | Other Plugin |
|---|---|---|---|
| Manifest | MV3 `manifest.json` | Extension manifest (VS Code, JetBrains) | Host-specific descriptor |
| Execution model | Service worker (MV3) + content scripts | Extension host process | Host sandbox |
| Permission model | Declared in manifest, user-approved | Contribution points, activation events | Host API surface |
| CSP | Strict — no inline scripts, no remote code | N/A | Host-defined |
| Distribution | Chrome Web Store / Firefox Add-ons / Edge Add-ons | VS Code Marketplace / JetBrains Marketplace | Host marketplace |
| Update model | Store-managed, signed by store | Marketplace-managed | Host-managed |
| Isolation | Content scripts isolated from page; service worker has no DOM | Extension host isolated from editor | Sandbox |
| Background processing | MV3 service worker (ephemeral, no persistent connection) | Background thread | Host-defined |

A spec written without this platform context will miss: manifest permission scope, MV3 service worker lifecycle constraints (no persistent background), content security policy, cross-origin messaging validation, store review requirements, and host sandbox limitations.

## Activation sequence

```
1. Recipe identifies Extension target and signals platform-extension activation
2. Load spec-template variant
3. Detect extension type (browser/IDE/other) via skill-rules.json signals
4. Load engineering/build-toolchain.md and engineering/performance-budgets.md
5. Load security/threat-model.md and security/platform-controls.md
6. Register verification/gates.md with Verifier
7. Write platform activation receipt
```

## Extension type routing

| Detected signal | Extension type |
|---|---|
| `manifest.json` with `manifest_version: 3` | Browser extension (MV3) |
| `manifest.json` with `manifest_version: 2` | Browser extension (MV2 — flag for MV3 migration) |
| `.vscodeignore`, `activationEvents` in `package.json` | VS Code extension |
| `plugin.xml` | IntelliJ/JetBrains plugin |

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `_shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - _shared/dev/frameworks/extension/core.md
  conditional_load: []
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-aesthetic/references/      # if popup/options UI work
    - gateway-experience/references/     # if user-facing UI features
```

## Output contract

**Platform activation receipt** (`.wabblespec/receipts/platform-extension-{timestamp}.json`)

## Files loaded by this module

```
modules/l3/extension/
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```
