# Platform Web — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Web as the primary target,
When platform-web is invoked,
Then it surfaces: "platform-web requires Recipe to have identified Web as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Web as the primary target,
When platform-web activates,
Then the activation sequence completes in order: spec-template load → framework detection → language module load → engineering load → security load → Verifier gate registration → receipt write.

## Framework routing: Next.js

Given `next.config.*` or an `app/` or `pages/` directory is detected,
When platform-web detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/web/nextjs.md` is loaded.
Then SSR/SSG/ISR concerns are activated in the spec context.

## Framework routing: React

Given `react` is in package.json and `.tsx`/`.jsx` files are present,
When platform-web detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/web/react.md` is loaded.

## Framework routing: Vue

Given `vue` is in package.json and `.vue` files are present,
When platform-web detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/web/vue.md` is loaded.

## Framework routing: SvelteKit

Given `svelte` is in package.json and `.svelte` files are present,
When platform-web detects the framework,
Then `.wabblespec/engine/shared/dev/frameworks/web/svelte.md` is loaded.

## Framework routing: vanilla

Given `index.html` exists at root with no framework detected,
When platform-web handles the project,
Then no framework-specific module is loaded.
Then vanilla HTML/CSS/JS patterns apply.

## Web-specific concerns injected into spec

Given platform-web is active,
When spec context is assembled,
Then Core Web Vitals budgets are declared: LCP < 2.5s, CLS < 0.1, INP < 200ms.
Then browser support matrix is declared.
Then CSP header requirement is present.
Then XSS prevention patterns (no dangerouslySetInnerHTML without justification) are in the spec.
Then CSRF protection is declared.
Then WCAG 2.1 AA accessibility requirement is present.
Then bundle size budget is declared.

## Capability handoff

Given platform-web has activated,
When the capability handoff is declared in the receipt,
Then `.wabblespec/engine/shared/dev/frameworks/web/core.md` and `.wabblespec/engine/shared/dev/frameworks/web/security.md` are always loaded.
Then gateway references include gateway-security/references/ and gateway-engineering/references/.
Then aesthetic/design/experience gateway references are included only when those gateways are active.

## Auth state declared

Given platform-web is active and the spec declares authenticated routes,
When spec context is assembled,
Then session cookie or JWT-in-memory auth state declaration is present.
Then the auth mechanism matches auth-policy.md requirements (HttpOnly cookies, no localStorage for tokens).

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-web attempts to register gates with Verifier,
Then platform-web logs: "verification/gates.md absent — Verifier registration skipped."
Then the platform activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-web run,
Then platform-web does not use CLI or API spec templates for a Web target.
Then platform-web does not activate for non-browser targets.
Then platform-web does not suppress WCAG AA requirement for any visual browser target.

## Receipt fields

Given any successful platform-web activation,
Then a receipt is written to `.wabblespec/state/receipts/platform-web-<timestamp>.json`.
Then the receipt contains: platform, framework_detected, language_module_loaded, templates_activated, cwv_budgets_declared, security_files_loaded, gates_registered, capability_handoff.
