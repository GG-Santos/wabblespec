# Extension Engineering — Performance Budgets

## Service Worker Startup Time

MV3 service workers restart on each event. Startup time directly affects every user interaction.

| Metric | Budget | Notes |
|---|---|---|
| Service worker cold start | < 50ms | Time to first message handled |
| Service worker warm start | < 10ms | Already resident in memory |

**Measurement:**
```javascript
// In background.js
const startTime = performance.now()
chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  console.log('SW ready in', performance.now() - startTime, 'ms')
})
```

**Failure mode:** Heavy imports at top of background.js delay service worker availability. Lazy-load non-critical modules.

---

## Content Script Injection Time

| Metric | Budget |
|---|---|
| Content script parse + execute | < 100ms |
| DOM mutation observer setup | < 10ms |
| First meaningful DOM change | < 200ms after injection |

**Failure mode:** Content scripts that block page load or cause layout thrash. Use `document_idle` injection timing unless `document_start` is strictly required.

---

## Popup Open Time

| Metric | Budget |
|---|---|
| Popup HTML parse + render | < 100ms |
| Data load from chrome.storage | < 50ms |
| First meaningful paint | < 200ms |

**Pattern:** Load storage data as first action in popup script. Render skeleton UI immediately, populate when data arrives.

---

## Bundle Size

| Component | Budget |
|---|---|
| background.js (minified) | < 100 KB |
| content.js (minified) | < 50 KB |
| popup.js (minified) | < 50 KB |
| Total extension package | < 5 MB (typical; store limits vary) |

**Measurement:** `npx wxt build && du -sh dist/`

---

## Memory Usage

| Context | Budget | Notes |
|---|---|---|
| Content script memory | < 20 MB per tab | Scales with open tabs |
| Popup memory | N/A — popup closes on blur | State in storage, not memory |
| Service worker memory | < 50 MB | Evicted when inactive |

**No memory leaks in content scripts.** Content scripts run in every matching tab — a 10MB leak × 20 open tabs = 200MB consumer memory stolen.

---

## Network Requests

| Concern | Policy |
|---|---|
| Requests per user action | ≤ 3 |
| Background polling interval | ≥ 60s (or event-driven — no polling) |
| Request timeout | ≤ 10s with user feedback |
| Caching | `chrome.storage.local` for cacheable responses, declare TTL |

**No background polling** unless explicitly declared in design-document.md with justification. Prefer push (WebSocket) or event-triggered fetch over polling.
