---
name: platform-web
description: Web platform package. Activates when Recipe detects a browser-targeted frontend. Loads Web spec templates, Core Web Vitals budgets, CSP/XSS security controls, and accessibility gates. Produces a materially different spec from CLI or API targets for the same task.
---

# Platform: Web

You are the Web platform layer. You activate when Recipe identifies a browser-targeted frontend and you load the constraints, templates, and verification gates specific to that target.

## What makes Web different from other targets

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

```
modules/l3/web/
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
