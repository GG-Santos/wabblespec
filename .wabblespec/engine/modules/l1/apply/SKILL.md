---
name: apply
description: Gateway routing engine. Reads the active platform package and capability gateways to determine which modules are relevant to the current wave. Assembles multi-module context using Economy placement rules. Produces delta proposals (ADDITIVE/COSMETIC → Specify --patch, BREAKING → Executor halt). Writes only to project/repo/ — never touches .wabblespec/ (I11).
---

# Apply

You are the execution routing layer. You determine what knowledge is relevant to the current wave, assemble it in the correct order, and execute gateway routing. You are the bridge between the spec world and the product code world.

## What this skill does

Gateway routing engine. Reads the active platform package and capability gateways to determine which modules are relevant to the current wave. Assembles multi-module context using Economy placement rules. Produces delta proposals (ADDITIVE/COSMETIC → Specify --patch, BREAKING → Executor halt). Writes only to project/repo/ — never touches .wabblespec/ (I11).

## When to use

- Every Executor wave (activated by Executor, not directly by user)
- After Guard PASS for the current wave
- Explicit `/apply` command for manual routing inspection

## Activation sequence

```
1. Read active platform package (L3) receipt — confirm it has activated
2. Read capability_handoff field from platform receipt
3. Read active capability gateway receipts — confirm which L4 gateways are active
4. Read current wave declaration from Decompose output
5. Resolve content load list (platform always_load + conditional_load + gateway references/)
6. Assemble module context (placement rules below)
7. Execute routing
8. Produce delta proposals for any discovered deviations
9. Write to project/repo/ only
```

## Capability routing

The platform receipt carries a `capability_handoff` field that declares what knowledge to load into Specify context. Apply reads this field and loads the declared files before assembly.

```json
{
  "capability_handoff": {
    "always_load": [".wabblespec/engine/shared/dev/frameworks/web/react.md", "..."],
    "conditional_load": {
      "signal": "file_or_import_pattern",
      "load": ".wabblespec/engine/shared/dev/frameworks/web/nextjs.md"
    }
  }
}
```

### Load resolution order

```
1. always_load — load unconditionally for every wave on this platform
2. conditional_load — evaluate each signal against the project repo; load on match
3. gateway references/ — for each active gateway, load gateway/{name}/references/ files
   declared in that gateway's active phase-A receipt (see gateway-pattern.md Phase A)
4. .wabblespec/engine/shared/dev/infrastructure/ — load if gateway-engineering is active
```

### Routing table — platform to knowledge files

| Platform | always_load | conditional_load signals |
|---|---|---|
| platform-web | `frameworks/web/core.md`, `frameworks/web/security.md` | next.config.* → `frameworks/web/nextjs.md`; `*.vue` → `frameworks/web/vue.md`; `*.svelte` → `frameworks/web/svelte.md` |
| platform-cli | `frameworks/cli/core.md` | cobra/go.mod → `frameworks/cli/cobra.md`; click/typer → `frameworks/cli/click.md`; clap/Cargo.toml → `frameworks/cli/clap.md` |
| platform-api-service | `frameworks/api/core.md`, `frameworks/api/security.md` | graphql → `frameworks/api/graphql.md`; grpc → `frameworks/api/grpc.md` |
| platform-mobile | `frameworks/mobile/core.md` | `*.swift` → `frameworks/mobile/swift-uikit.md`; `*.kt` → `frameworks/mobile/kotlin-compose.md`; react-native → `frameworks/mobile/react-native.md`; flutter → `frameworks/mobile/flutter.md` |
| platform-desktop | `frameworks/desktop/core.md` | electron → `frameworks/desktop/electron.md`; tauri → `frameworks/desktop/tauri.md` |
| platform-game | `frameworks/game/core.md` | unity → `frameworks/game/unity.md`; unreal → `frameworks/game/unreal.md`; godot → `frameworks/game/godot.md` |
| platform-ai-agent | `frameworks/ai/core.md`, `frameworks/ai/safety.md` | langchain → `frameworks/ai/langchain.md`; openai → `frameworks/ai/openai-sdk.md` |
| platform-data-pipeline | `frameworks/data/core.md` | spark → `frameworks/data/spark.md`; dbt → `frameworks/data/dbt.md`; airflow → `frameworks/data/airflow.md` |
| platform-library | `frameworks/library/core.md` | — |
| platform-extension | `frameworks/extension/core.md` | — |
| platform-iot | `frameworks/iot/core.md` | — |

Gateway references/ are loaded per active gateway. Each gateway declares its `references/` directory in its SKILL.md. Apply loads all files in that directory when the gateway is active.

### Engineering infrastructure load

When `gateway-engineering` is active, also load from `.wabblespec/engine/shared/dev/infrastructure/`:
- `cicd.md` — always
- `containers.md` — if Dockerfile or k8s manifest detected in repo
- `iac.md` — if Terraform/Pulumi files detected
- `observability.md` — if metrics/tracing config detected or declared in spec

## Context assembly — placement rules

Context is assembled in three zones to stay within Economy token constraints:

| Zone | Content | Position |
|---|---|---|
| Constraints | Invariants relevant to this wave, gateway rules, scope constraints | Top of context |
| References | Platform package content, shared-dev modules, gateway reference files | Middle |
| Active task | Current wave declaration, spec artifacts for this wave, acceptance criteria | End of context |

Nothing preloaded beyond what the current wave declaration specifies. Every item in context must trace to a declared wave input.

## Delta handling

During execution, Apply may discover that a better approach differs from the current spec. Delta types:

| Delta type | Scope class | Action |
|---|---|---|
| ADDITIVE | LOCAL | Propose patch to Specify via `--patch` flag; Specify classifies LOCAL/BOUNDARY; continue wave if LOCAL |
| ADDITIVE | BOUNDARY | Propose patch to Specify; Specify halts and surfaces to user before continuing |
| COSMETIC | LOCAL | Propose patch to Specify, continue wave |
| COSMETIC | BOUNDARY | Rare — treat as ADDITIVE BOUNDARY |
| BREAKING | any | Halt wave, surface to Executor, do not proceed |

**Scope classification:**
- `LOCAL`: change internal to current module — no API, schema, shared type, or external consumer affected
- `BOUNDARY`: change touches API surface, request/response schema, shared types, DB schema, or any external consumer

Apply must declare scope class in every delta proposal. Specify --patch uses this classification to decide whether to apply inline (LOCAL) or halt for user decision (BOUNDARY).

No silent deviations. No "close enough" interpretation of spec. Every delta is declared.

## Write authority

Apply writes only to `project/repo/`. Hard rule (I11).

Apply never writes to:
- `.wabblespec/` (framework control plane)
- Any file not in the current wave's declared write targets
- Any file owned by another module

If Apply discovers it needs to write outside declared targets, it surfaces a SPEC_VIOLATION error — does not proceed.

## Output contract

Writes a receipt to `.wabblespec/receipts/` on successful completion.

## What not to do

- Do not self-activate outside Executor wave context
- Do not load modules not declared in the current wave
- Do not write to .wabblespec/ for any reason
- Do not proceed on BREAKING delta — halt and surface
- Do not assemble context without placement rules (constraints top, active task end)
