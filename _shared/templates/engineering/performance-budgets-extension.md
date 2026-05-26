# Performance Budgets — Browser Extension

> Template. Copy to `engineering/performance-budgets.md` in your project and fill in values.
> Consume: `l7/monitor`, `l4/engineering`, `l3/extension`.
> Reference: `_shared/references/performance-budgets.md`.

---

## Host impact

### Memory footprint in host browser

**Target:** ≤ 50MB resident memory added to the host browser process by the extension
**Rationale:** Extensions run in shared browser memory space; high memory usage impacts all tabs and degrades perceived browser performance
**Measurement:** Chrome Task Manager / `chrome.system.memory` API delta before/after extension install; measure on idle tab
**PII impact:** none

### CPU impact on page load

**Target:** ≤ 10ms added to page load time on P50 pages (content script injection overhead)
**Rationale:** Content scripts run on every page matching the declared match pattern; cumulative overhead across all page loads is noticeable
**Measurement:** WebPageTest with/without extension; measure TTI delta on 10 representative URLs
**PII impact:** none

### Background service worker CPU (MV3)

**Target:** < 0.5% CPU utilization on average; service worker must be inactive when no events are being processed
**Rationale:** MV3 service workers are ephemeral (no persistent background page); persistent CPU use indicates a bug or misuse of the keep-alive pattern
**Measurement:** Chrome Performance Monitor during 10-minute idle period with extension installed
**PII impact:** none

---

## Startup

### Extension install activation time

**Target:** ≤ 500ms from extension installation to first usable state
**Rationale:** Users expect an extension to be immediately usable after installation; delay implies heavy initialization
**Measurement:** `chrome.runtime.onInstalled` to first UI-ready state; automate with Puppeteer
**PII impact:** none

### Content script injection time

**Target:** Content script must not block DOMContentLoaded; injection overhead ≤ 5ms per page
**Rationale:** Synchronous content script work in `document_start` delays page rendering for all matched pages
**Measurement:** trace content script entry to exit in Timeline; verify no synchronous blocking work at injection
**PII impact:** none

---

## Service worker lifecycle (MV3)

### State persistence

**Target:** Zero reliance on in-memory state in service worker; all persistent state in `chrome.storage` or IndexedDB
**Rationale:** MV3 service workers are terminated by the browser when idle; in-memory state is lost on termination — this is the primary MV3 migration failure mode (enforced in `l3/extension` AT-EXT-01)
**Measurement:** code audit + integration test: terminate service worker manually, verify extension resumes correctly
**PII impact:** none

---

## Bundle

### Extension package size

**Target:** ≤ 10MB unpacked extension size (Chrome Web Store limit is 128MB but large extensions are flagged for review)
**Rationale:** Large extensions trigger additional Chrome Web Store review; size > 10MB usually indicates bundled dependencies that could be removed
**Measurement:** `zip -r extension.zip . && stat extension.zip` in CI; alert on size regression
**PII impact:** none

### Content Security Policy compliance

**Target:** CSP must not include `unsafe-inline` or `unsafe-eval`; no inline scripts
**Rationale:** Required by MV3 and `l3/extension` AT-EXT-04; inline scripts are blocked by Chrome since MV2
**Measurement:** CSP header/manifest audit in CI; `web-ext lint` or equivalent
**PII impact:** none

---

## Permission footprint

### Declared permissions

**Target:** Zero permissions declared that are not actively used by a named feature
**Rationale:** Unused permissions block Chrome Web Store approval and erode user trust; each permission requires a stated purpose in the store listing
**Measurement:** permission audit against feature list on each release; remove unused permissions before release
**PII impact:** permissions like `history`, `bookmarks`, `cookies`, `tabs` constitute PII access — declare handling

---

## Error rate

### Extension crash rate

**Target:** ≥ 99.5% crash-free service worker sessions
**Rationale:** Service worker crashes reset extension state and may cause data loss; crash-free rate is reported in Chrome Developer Dashboard
**Measurement:** Chrome Developer Dashboard error report; Sentry integration for runtime errors
**PII impact:** error reports must not include page content or user data from visited pages

---

## PII fields (excluded from log schema)

<!-- Extensions have significant PII risk due to access to browsing data -->
<!-- Example:
- visited_urls (tabs permission)
- page_content (activeTab permission)
- form_data (content script access)
- cookies (cookies permission)
- browsing_history (history permission)
-->
___ UNDECLARED — REQUIRED; declare all data the extension reads and its retention/transmission policy
