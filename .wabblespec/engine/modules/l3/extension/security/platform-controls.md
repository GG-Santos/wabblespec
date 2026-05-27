# Extension Security — Platform Controls

These controls apply to all Extension/Plugin targets. Enforced by Verifier via `verification/gates.md`.

---

## Control 1: Strict Content Security Policy

**Rule:** Extension pages (popup, options, sidepanel) must declare a strict CSP.

**Required minimum:**
```json
"content_security_policy": {
  "extension_pages": "script-src 'self'; object-src 'none';"
}
```

**Prohibited:** `unsafe-inline`, `unsafe-eval`, any external script source (`https://cdn.example.com`).

**Enforcement:** `web-ext lint` and manual manifest review.

---

## Control 2: No innerHTML with External Data

**Rule:** Extension pages must never assign externally-sourced strings to `innerHTML`, `outerHTML`, or `insertAdjacentHTML`.

**Enforcement:** Code review. Grep for `innerHTML =` and `insertAdjacentHTML`.

**Required alternative:**
```javascript
element.textContent = userSuppliedString   // safe for text
// or:
const el = document.createElement('div')
el.textContent = userSuppliedString
parent.appendChild(el)
```

---

## Control 3: postMessage Origin Validation

**Rule:** All `window.addEventListener('message', ...)` handlers must validate message origin and source.

**Required pattern:**
```javascript
window.addEventListener('message', (event) => {
  if (event.source !== window) return
  // For cross-origin: if (event.origin !== expectedOrigin) return
  if (!knownMessageTypes.has(event.data?.type)) return
  // process message
})
```

**Enforcement:** Code review. Any message handler without origin validation is a blocker.

---

## Control 4: Message Sender Validation in Background

**Rule:** Background service worker must validate message sender for any operation that reads/writes storage or makes network calls based on message content.

**Pattern:**
```javascript
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  // popup sender: sender.tab is undefined, sender.url starts with chrome-extension://
  // content script sender: sender.tab.url is the page URL
  const isTrustedSender = !sender.tab  // popup/options = trusted
  
  if (message.type === 'PRIVILEGED_OP' && !isTrustedSender) {
    sendResponse({ error: 'unauthorized' })
    return
  }
})
```

---

## Control 5: Minimal Permissions

**Rule:** Every declared permission must be used. Every used API must have its permission declared. No speculative permissions.

**Enforcement:** Gate 2 (permission audit). Each permission mapped to specific API call in technical-spec.md.

**Optional permissions:** For permissions needed rarely, use `chrome.permissions.request()` at runtime instead of declaring at install.

---

## Control 6: No Remote Script Execution

**Rule:** Extension must not load, eval, or execute any JavaScript from a remote URL.

**Enforcement:** CSP blocks this at runtime. Code review confirms no `eval()`, `new Function()`, `setTimeout(string)`, or dynamic `<script src>` injection.

**MV3 note:** Chrome Web Store rejects extensions with remote code execution. This control aligns with store policy.

---

## Control 7: Storage Encryption for Sensitive Data

**Rule:** Sensitive data (tokens, keys, personal data) stored in `chrome.storage` must be encrypted.

**Why:** `chrome.storage.sync` and `chrome.storage.local` are not encrypted at rest. Any extension or native app with storage access can read values.

**Implementation:**
- Use Web Crypto API (`crypto.subtle`) for AES-GCM encryption before storage write
- Key derivation from a user-provided passphrase or from a per-installation random key stored separately
- Clearly document what is stored, where, and whether it is encrypted in design-document.md

---

## Control 8: Content Script Scope Minimization

**Rule:** Content scripts must declare the narrowest possible `matches` pattern.

**Preference order (narrowest to broadest):**
1. `"https://specific-site.com/specific/path/*"` — best
2. `"https://specific-site.com/*"` — acceptable
3. `"https://*/*"` — requires justification
4. `"<all_urls>"` — prohibited unless no narrower pattern is possible (document explicitly)

**Enforcement:** Manifest review. Broad patterns trigger extended store review.
