# Extension / Plugin Framework Core

Cross-framework knowledge for browser extensions and editor plugins. Loaded by Apply for every Extension platform task.

## Extension architecture (browser MV3)

```
manifest.json           ← declares everything; no runtime discovery
  permissions           ← what the extension can do
  host_permissions      ← which pages it can access
  content_scripts       ← what runs in page context
  background            ← service worker (MV3)
  action                ← popup + icon
  options_page          ← settings page
```

### Process contexts

| Context | What it is | DOM access | Chrome APIs |
|---|---|---|---|
| Service worker | Background script (MV3) | No | Most APIs |
| Content script | Injected into page | Yes (isolated DOM) | Limited subset |
| Popup | action.html page | Own document | Most APIs |
| Options page | options_page.html | Own document | Most APIs |

Content scripts run in an isolated JS context — they share the DOM with the page but cannot access the page's JS variables or prototype chain. They are isolated from the extension's service worker.

## Manifest V3 requirements

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0.0",
  "description": "One sentence.",
  "permissions": ["storage", "activeTab"],
  "host_permissions": ["https://api.example.com/*"],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [{
    "matches": ["https://example.com/*"],
    "js": ["content.js"],
    "run_at": "document_idle"
  }],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon128.png"
  }
}
```

### Service worker constraints (MV3)

The background service worker is ephemeral — it can be killed at any time:
- Do not store state in global variables — use `chrome.storage.local`
- Do not assume the service worker is alive when content scripts message it — use event listeners
- Do not use persistent connections in service workers (they prevent sleep)

## Permission minimization

Every permission must be justified in spec. Principle: request the minimum necessary.

| Permission | Triggers user prompt? | Notes |
|---|---|---|
| `activeTab` | No (on click) | Preferred over `<all_urls>` for per-click access |
| `storage` | No | Required for `chrome.storage` |
| `tabs` | No | Access to tab URLs and titles |
| `cookies` | No | Read/write cookies |
| `<all_urls>` | Yes (at install) | Avoid — triggers warning; use specific host patterns |
| `history` | Yes (at install) | Justify explicitly |

Host permissions: use the narrowest pattern that works. `https://example.com/*` is better than `https://*/*`.

## Message passing

```javascript
// Content script → service worker
chrome.runtime.sendMessage({ type: "ACTION", payload: data }, response => {
  if (chrome.runtime.lastError) { /* handle disconnect */ }
})

// Service worker listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== "ACTION") return  // always check type
  // validate sender.tab.url if needed
  doWork(message.payload).then(result => sendResponse({ ok: true, result }))
  return true  // required for async sendResponse
})

// Popup ↔ content script (via service worker)
chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
  chrome.tabs.sendMessage(tab.id, { type: "QUERY" }, response => {})
})
```

Validate message `type` on every listener — extensions receive messages from all origins.

## Storage

```javascript
// Store
await chrome.storage.local.set({ key: value })
await chrome.storage.sync.set({ key: value })  // synced across devices, 100KB limit

// Read
const { key } = await chrome.storage.local.get("key")

// Remove
await chrome.storage.local.remove("key")
```

Spec must declare: what is stored in `local` vs `sync`; estimated size; eviction strategy.

## Content Security Policy (MV3)

MV3 enforces strict CSP — no remote code execution:
- No `eval()` in extension pages
- No inline event handlers in popup HTML
- No loading scripts from external URLs at runtime
- `content_security_policy` in manifest can be tightened but not loosened from MV3 defaults

## Store submission

Spec must address:
- Chrome Web Store review: may take 1-7 days; rejection reasons must be addressed before resubmission
- Privacy policy: required if extension collects any user data
- Single-purpose policy: extension must have one clear purpose
- Permissions justification: store review requires justification for sensitive permissions
