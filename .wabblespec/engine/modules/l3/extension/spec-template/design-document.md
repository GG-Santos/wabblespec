# Extension Design Document Template (P1)

> **Platform:** Extension/Plugin
> **Template version:** 1.0
> **Populated by:** Specify module (after platform-extension activation)
> **Sections marked `[REQUIRED]` must be filled before Specify receipt is written.**

---

## Overview

[REQUIRED] One paragraph: what this extension does, which host it runs in (Chrome/Firefox/VS Code/etc.), and the primary workflow it enables or replaces for users.

---

## Extension Type [REQUIRED]

[ ] Browser Extension — Manifest V3
[ ] Browser Extension — Manifest V2 (flag: migration to MV3 required before store submission)
[ ] VS Code Extension
[ ] JetBrains Plugin
[ ] Other: ___

**Host application(s):** List specific browsers/IDEs/versions supported.

**Minimum host version:** ___

---

## Permission Scope [REQUIRED]

**Principle of least privilege.** Request only permissions that are strictly required.

### Browser Extension Permissions

| Permission | Why required | Cannot use narrower permission? |
|---|---|---|
| `storage` | Store user preferences | N/A — narrowest available |
| `activeTab` | Access current tab | Using `activeTab` instead of `<all_urls>` |
| [list all] | | |

**Host permissions declared:**
```json
"host_permissions": ["https://api.example.com/*"]
```

Are host permissions limited to specific origins? [ ] Yes — list: ___ [ ] No — explain why broad permissions required: ___

**Permissions NOT requested** (document why these were consciously excluded):
- `history` — not needed
- `bookmarks` — not needed

### VS Code Extension Contribution Points

| Contribution | Purpose | Activation event |
|---|---|---|
| `commands` | [what command] | `onCommand:<id>` |
| `languages` | [language] | `onLanguage:<id>` |

---

## Manifest Structure [REQUIRED] (Browser Extension)

```json
{
  "manifest_version": 3,
  "name": "<Extension Name>",
  "version": "1.0.0",
  "description": "<60 chars max>",
  "permissions": [],
  "host_permissions": [],
  "background": {
    "service_worker": "background.js",
    "type": "module"
  },
  "content_scripts": [],
  "action": {},
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'none';"
  }
}
```

---

## Content Security Policy [REQUIRED] (Browser Extension)

CSP for extension pages (popup, options, sidepanel):

```
script-src 'self'; object-src 'none';
```

**No `unsafe-inline`.** No `unsafe-eval`. No remote script sources.

**Rationale for any CSP deviation:** ___

---

## Component Architecture [REQUIRED]

| Component | File | Execution context | Access |
|---|---|---|---|
| Background service worker | `background.js` | Service worker (no DOM, ephemeral) | chrome.* APIs, fetch |
| Content script | `content.js` | Isolated world on page | Limited DOM, postMessage |
| Popup | `popup.html` + `popup.js` | Extension page (has DOM) | chrome.* APIs |
| Options page | `options.html` | Extension page | chrome.* APIs |

**Message passing:** How components communicate:
```
Popup → Background: chrome.runtime.sendMessage()
Content Script → Background: chrome.runtime.sendMessage()
Background → Content Script: chrome.tabs.sendMessage()
```

---

## Service Worker Lifecycle (MV3) [REQUIRED]

MV3 service workers are ephemeral — they terminate after ~30s of inactivity.

**Persistent state:** Service worker state is lost on termination. Persistent state must use `chrome.storage`, not in-memory variables.

**Long-running operations:** Any operation > 30s must be handled via:
- Offscreen document (for audio, clipboard, DOM parsing)
- Web-accessible resources
- External server with client polling

**Operations that will fail if service worker terminates mid-execution:**
- [list any]

---

## Store Distribution [REQUIRED]

Target store(s):
[ ] Chrome Web Store
[ ] Firefox Add-ons (AMO)
[ ] Edge Add-ons
[ ] Safari Extensions
[ ] VS Code Marketplace (`.vsix` package)
[ ] JetBrains Marketplace

**Review requirements:** Each store has a review process. Declare any content or permission that typically triggers extended review:

---

## GWT Acceptance Scenarios (Extension-specific)

```
Given: the extension is installed in a fresh browser profile
When: the user activates the extension on a page
Then: the extension requests only the permissions declared in manifest
      AND no additional permission prompts appear unexpectedly
      AND the extension does not access any page not in host_permissions

Given: a content script injects into a page
When: the page's own JavaScript runs
Then: the content script cannot access the page's JavaScript variables
      AND the page's JavaScript cannot access content script variables
      AND communication happens only via postMessage with origin validation

Given: the service worker receives a message from a content script
When: processing the message
Then: the message origin is validated before acting on the message
      AND unknown message types are ignored (not processed)
      AND service worker state is not assumed to persist between messages

Given: the extension makes a network request
When: the request is made from background or content script
Then: the destination is within declared host_permissions
      AND the request uses HTTPS
      AND credentials (API keys, tokens) are not in the request URL
```

---

## Open Questions

List any unresolved design decisions. Specify module blocks receipt until all REQUIRED sections complete.
