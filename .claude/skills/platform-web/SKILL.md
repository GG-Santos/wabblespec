---
name: platform-web
description: Web platform package. Activates when Recipe detects a browser-targeted frontend. Loads Web spec templates, Core Web Vitals budgets, CSP/XSS security controls, and accessibility gates. Produces a materially different spec from CLI or API targets for the same task.
---

# Platform: Web

You are the Web platform layer. You activate when Recipe identifies a browser-targeted frontend and you load the constraints, templates, and verification gates specific to that target.

## What this skill does

| Concern | Web | CLI | API/Service |
|---|---|---|---|
| Primary user interface | Browser DOM | Terminal args/stdout | HTTP endpoints |
| Success signal | Visual render + CWV | Exit code 0 | HTTP 2xx |
| Auth state | Session cookies / JWTs in memory | Env vars | Auth headers |
| Performance measure | LCP < 2.5s, CLS < 0.1, INP < 200ms | Cold start < 100ms | p99 latency < 200ms |
| Security primary concern | XSS, CSRF, CSP | Shell injection, credential exposure | Auth bypass, injection |
| Accessibility | WCAG 2.1 AA required | --help text quality | API docs |
| Distribution | CDN / hosting | Binary / npm global | Container registry |
| Output contract | HTML/CSS/JS rendered in browser | stdout (data) + stderr (errors) | Response body |
| Config storage | localStorage, cookies, env vars at build time | XDG config file, env vars at runtime | Env vars, secrets manager |

A spec written without this platform context misses: Core Web Vitals targets, browser support matrix, CSP header requirement, XSS prevention (dangerouslySetInnerHTML), CSRF protection, accessibility requirements, bundle size budget, and hydration strategy.

## When to use

Invoked per activators declared in `skill-rules.json`.

## Activation sequence

```
1. Recipe identifies Web target and signals platform-web activation
2. Load spec-template variant (design-document.md, systems-design.md, technical-spec.md)
3. Detect framework (React/Next/Vue/Svelte/Angular) via skill-rules.json signals
4. Load matched language module from _shared/dev/languages/node/
5. Load engineering/build-toolchain.md and engineering/performance-budgets.md
6. Load security/threat-model.md and security/platform-controls.md
7. Register verification/gates.md with Verifier
8. Write platform activation receipt
```

## Design phase sequence

```
P0: product-concept.md           ← Pillars, user value proposition, scope tiers (REQUIRED before P1)
P1: design-document.md           ← Product requirements, user stories, browser support matrix
P2: systems-design.md            ← Architecture, state management, rendering strategy
    framework-specific/          ← Load matched framework doc (conditional on detection)
      nextjs.md                  ← If next.config.* detected
      react.md                   ← If react in package.json, no Next.js
      vue.md                     ← If *.vue files detected
      svelte.md                  ← If *.svelte files detected
P3: technical-spec.md            ← Implementation spec, GWT acceptance scenarios
```

**Invariant:** product-concept.md pillars must be declared before Specify receipt is written. Framework-specific doc must be loaded if a supported framework is detected — generic template is insufficient for Next.js RSC or SvelteKit routing concerns.

## Framework routing

| Detected signal | Framework context |
|---|---|
| `next.config.*`, `app/` or `pages/` directory | Next.js (SSR/SSG/ISR concerns activate) |
| `react` in package.json, `*.tsx`/`*.jsx` | React (SPA patterns) |
| `vue` in package.json, `*.vue` | Vue + Vite (Composition API) |
| `svelte` in package.json, `*.svelte` | SvelteKit |
| `@angular/core` in package.json | Angular (standalone components) |
| `astro` in package.json | Astro (islands architecture) |
| `index.html` at root, no framework | Vanilla HTML/CSS/JS |

## Files loaded by this module

**Always loaded:**
```
modules/l3/web/
  spec-template/product-concept.md        ← P0 (always)
  spec-template/design-document.md
  spec-template/systems-design.md
  spec-template/technical-spec.md
  engineering/build-toolchain.md
  engineering/performance-budgets.md
  engineering/platform-verification.md
  engineering/qa-pipeline.md
  security/threat-model.md
  security/platform-controls.md
  verification/gates.md
```

**Conditionally loaded (framework-specific):**
```
modules/l3/web/spec-template/framework-specific/
  nextjs.md     ← if next.config.* or app/ or pages/ directory detected
  react.md      ← if react in package.json and no Next.js detected
  vue.md        ← if *.vue files detected
  svelte.md     ← if *.svelte files detected
```

## Capability handoff

Declared in platform activation receipt. Apply reads this to resolve which `_shared/dev/frameworks/` and gateway `references/` files load into Specify context.

```yaml
capability_handoff:
  always_load:
    - _shared/dev/frameworks/web/core.md
    - _shared/dev/frameworks/web/security.md
    - modules/l3/web/spec-template/product-concept.md
  conditional_load:
    - signal: "next.config.* or app/ or pages/ directory"
      load: modules/l3/web/spec-template/framework-specific/nextjs.md
    - signal: "react in package.json, no Next.js detected"
      load: modules/l3/web/spec-template/framework-specific/react.md
    - signal: "*.vue files detected"
      load: modules/l3/web/spec-template/framework-specific/vue.md
    - signal: "*.svelte files detected"
      load: modules/l3/web/spec-template/framework-specific/svelte.md
  gateway_references:
    - gateway-security/references/
    - gateway-engineering/references/
    - gateway-aesthetic/references/      # if aesthetic gateway active
    - gateway-design/references/         # if design gateway active
    - gateway-experience/references/     # if experience gateway active
```

## Output contract

Writes a receipt to `.wabblespec/receipts/` on successful completion.
