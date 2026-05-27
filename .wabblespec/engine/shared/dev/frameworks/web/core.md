# Web Framework Core

Cross-framework knowledge for browser-targeted frontends. Loaded by Apply for every Web platform task.

## Browser runtime contract

The browser is not a server. Every spec for a Web target must declare:
- **JavaScript execution environment**: which browsers are supported (declare in spec; cannot be implicit)
- **Module system**: ESM-first; CommonJS only via bundler interop
- **DOM availability**: if SSR or SSG, distinguish what runs in Node vs browser
- **Async model**: microtask queue, event loop, no blocking I/O

## Rendering strategies

| Strategy | When | Trade-off |
|---|---|---|
| CSR (client-side rendering) | Rich SPA, auth-gated, personalized | Best interactivity; worst initial LCP |
| SSR (server-side rendering) | SEO required, authenticated content | Good LCP; adds server infrastructure |
| SSG (static site generation) | Content sites, docs, marketing | Best performance; no dynamic per-request data |
| ISR (incremental static regen) | Mixed content freshness | Next.js-specific; trade-off on cache invalidation complexity |
| Streaming SSR | Large pages needing early TTFB | Requires framework support (React 18, Next.js App Router) |

Spec must declare rendering strategy and justify it.

## State management

| Scope | Approach |
|---|---|
| Component-local | `useState` / `ref` / signals — default |
| Cross-component shared | Context (small trees) or state store (large trees) |
| Server state | Query library (TanStack Query, SWR) — not global store |
| URL state | Router-managed; declare which state lives in URL params |
| Persisted state | localStorage (user prefs) or cookies (session); declare size budget |

Anti-pattern: server state in global client store. Server state belongs in a query cache.

## Performance budget — spec requirements

Spec must declare:
- **LCP target**: default < 2.5s on mobile 4G; declare if different
- **CLS target**: < 0.1; list layout shift candidates in spec
- **INP target**: < 200ms; identify interaction-heavy components
- **JS bundle budget**: initial JS < 150KB gzipped; per-route chunks declared
- **Image strategy**: lazy loading on below-fold images; WebP/AVIF with fallback

## Security baseline (web)

Every Web spec must address:
- **CSP**: Content-Security-Policy header declared; no `unsafe-inline` without justification
- **XSS**: No raw HTML insertion of user-controlled content; list `dangerouslySetInnerHTML` / `v-html` / `innerHTML` uses
- **CSRF**: Stateful session: SameSite=Strict cookies + CSRF token. SPA: bearer tokens in memory (not localStorage)
- **CORS**: Declared; no wildcard origin without justification
- **Subresource integrity**: CDN-sourced scripts must have SRI hash

## Browser API usage

Declare which browser APIs are used. APIs requiring justification:
- Geolocation — user prompt; spec must declare purpose
- Camera/microphone — user prompt; HTTPS required
- Notifications — user prompt; must have opt-in flow
- Service Worker — declare caching strategy and update flow
- IndexedDB / localStorage — declare size budget and eviction policy
- Clipboard API — user gesture required
