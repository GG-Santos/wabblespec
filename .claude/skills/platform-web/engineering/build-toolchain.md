# Web Engineering — Build Toolchain

## Bundler

**Default:** Vite (all non-Next.js projects)
**Next.js:** Built-in bundler (Webpack → Turbopack migration path)
**Legacy only:** Webpack — requires justification. No new projects start with Webpack.

**Vite config requirements:**
```typescript
// vite.config.ts minimum
export default defineConfig({
  build: {
    rollupOptions: {
      output: { manualChunks: {...} }  // declare code-splitting strategy
    },
    sourcemap: false,    // production: false (upload to error tracker instead)
    minify: 'esbuild',
  }
})
```

**Bundle analysis:** Required before each release. Tool: `vite-bundle-analyzer` / `@next/bundle-analyzer` / `rollup-plugin-visualizer`. Output reviewed — no undeclared large dependencies.

---

## TypeScript

**Required:** `tsconfig.json` with `strict: true` for all projects. No `any` in component props or API types without explicit `// eslint-disable` + comment.

**Type generation:** API types generated from source of truth (OpenAPI → `openapi-typescript`, GraphQL → `graphql-codegen`, tRPC → inferred). Not hand-maintained.

---

## Package Management

**Lockfile:** Required. `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` committed. CI uses `npm ci` / `yarn install --frozen-lockfile` / `pnpm install --frozen-lockfile`.

**Node version:** `.nvmrc` or `.node-version` in repo root. `engines` field in `package.json`. Minimum Node 18.

---

## CSS

**Preferred:** Tailwind CSS (utility-first, purge dead classes at build)
**Alternative:** CSS Modules (scoped, no global leakage)
**Avoid:** Global CSS files with unscoped selectors (causes specificity conflicts at scale)

**Critical CSS:** Inline above-fold styles in `<head>` for SSR/SSG. Framework handles this (Next.js App Router CSS, Astro scoped styles). For CSR: accept FOUC or use `<style>` injection.

---

## Images

**Next.js:** `next/image` component required. Never `<img>` for above-fold content.
**Vite/SvelteKit/Astro:** `vite-imagetools` or equivalent for format conversion + responsive sizes.
**Manual:** WebP with `<picture>` fallback. `width` and `height` attributes on all `<img>` to prevent CLS.

**LCP image:** `fetchpriority="high"` attribute. No `loading="lazy"`. Preload link in `<head>`.

---

## Web Fonts

```html
<!-- Preload critical font -->
<link rel="preload" href="/fonts/inter-variable.woff2" as="font" type="font/woff2" crossorigin>
```

`font-display: swap` in `@font-face`. Self-host fonts — no CDN dependency for critical path fonts.

---

## Environment Variables

**Build-time client vars:** `NEXT_PUBLIC_` (Next.js) or `VITE_` (Vite) prefix. Embedded in bundle at build time — never secret.

**Server-side only:** No prefix. Never referenced in client code. Fail build if accessed from client bundle.

**Validation at startup:**
```typescript
// Validate required env vars before app starts
const requiredEnv = ['NEXT_PUBLIC_API_URL'] as const
requiredEnv.forEach(key => {
  if (!process.env[key]) throw new Error(`Missing required env var: ${key}`)
})
```

---

## CI Build Gates

Before any deployment:
1. `tsc --noEmit` — zero type errors
2. `eslint` — zero errors (warnings allowed with justification)
3. Unit tests pass
4. Bundle analysis — within declared budget
5. `npm audit --audit-level=high` — zero high/critical findings
6. Lighthouse CI — CWV gates pass (see performance-budgets.md)
7. axe-core scan — zero critical violations

---

## Deployment

**Static (SSG/SPA):** CDN deployment. Files served from edge. No server process.
**SSR:** Node.js server or serverless functions. Declare runtime (Node/Edge/Lambda).
**Hosting:** Declare provider. Declare preview/staging URL pattern.

**Cache headers:**
- Hashed assets (`/assets/main.abc123.js`): `Cache-Control: public, max-age=31536000, immutable`
- HTML files: `Cache-Control: no-cache` (always revalidate for latest deploy)
- API responses: declare per endpoint
