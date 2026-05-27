# Extension Technical Spec Template (P3)

> **Platform:** Extension/Plugin
> **Template version:** 1.0
> **Prerequisite:** systems-design.md complete.

---

## Component Implementation Specs

### Background Service Worker

**Lifecycle:**
- `chrome.runtime.onInstalled` — setup: initialize storage defaults, create context menus
- `chrome.runtime.onStartup` — reinitialize ephemeral state
- Message handler: `chrome.runtime.onMessage`

**State:** All persistent state via `chrome.storage`. No module-level variables for state that must survive service worker termination.

**GWT scenarios:**
```
Given: service worker terminates (30s inactivity)
When: a message arrives
Then: service worker restarts automatically
      AND message is handled correctly (state read from storage, not memory)
      AND no data loss occurs from the termination
```

---

### Content Script

**Injection timing:** [ ] `document_idle` (default) [ ] `document_start` [ ] `document_end`

**Rationale for timing:** ___

**DOM operations:** List all DOM elements queried or modified:

| Selector | Operation | Reason |
|---|---|---|
| `#<id>` | read / write / observe | [purpose] |

**GWT scenarios:**
```
Given: content script injected into a page with a slow-loading DOM
When: content script queries for its target elements
Then: queries use MutationObserver to handle elements not yet present
      AND no errors thrown when elements are absent
      AND no infinite loops in observer callbacks
```

---

### Popup / Options Page

**State source:** Popup state loaded from `chrome.storage` on open. Not cached between opens.

**User actions → storage:** Every preference change writes to `chrome.storage` immediately.

**GWT scenarios:**
```
Given: user opens popup
When: popup renders
Then: displayed state matches current chrome.storage values
      AND no stale state from a previous popup session appears

Given: user changes a preference in options page
When: another component reads that preference
Then: the new value is returned immediately after storage write completes
      AND no component caches the old value
```

---

## Error Handling

| Context | Error type | Handling |
|---|---|---|
| `chrome.storage` read/write | `chrome.runtime.lastError` | Check after every storage call; log to console, degrade gracefully |
| Message passing | No listener | `sendMessage` callback receives `undefined` — handle explicitly |
| Network request from background | Fetch failure | Retry with backoff; surface to UI via storage flag |
| Content script injection failure | Script error | Isolated — does not crash extension; log error |

---

## Permissions Audit

Before release, verify each declared permission is actually used:

| Permission | Used in file | Specific API call |
|---|---|---|
| `storage` | `background.ts:42` | `chrome.storage.local.get()` |
| `activeTab` | `popup.ts:17` | `chrome.tabs.query()` |

**Unused permissions must be removed before Gate 1 passes.**

---

## Store Submission Checklist

- [ ] Privacy policy URL added to store listing (required if any data collected)
- [ ] Screenshots prepared (1280x800 or 640x400)
- [ ] Description under 132 characters for summary
- [ ] All permissions justified in store listing description
- [ ] Remote code execution: none (MV3 prohibits; check CSP)
- [ ] No external JavaScript loaded (all JS bundled into extension)
- [ ] Content scripts scoped to minimum required host matches
