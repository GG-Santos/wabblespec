# Extension Engineering — Platform Verification

How to run and interpret the extension verification gates in `verification/gates.md`.

---

## Running All Gates

```bash
# Lint manifest + extension structure (Firefox tool, works for Chrome too)
npx web-ext lint --source-dir dist/

# Build for all targets
npx wxt build
npx wxt build -b firefox

# Run browser extension E2E tests
npx playwright test tests/extension/
```

---

## Manual Verification Steps

### Load unpacked extension in Chrome
1. Navigate to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" → select `dist/chrome-mv3/`
4. Verify extension loads without errors in console
5. Open background service worker DevTools from extensions page

### Verify permissions at install
1. In Chrome, click extension install prompt
2. Verify permissions shown match design-document.md permission table
3. No unexpected permissions appear

### Verify service worker ephemeral behavior
1. Open background service worker console
2. Store something in a module-level variable
3. Wait for service worker to terminate (navigate away, wait 30s)
4. Trigger extension action
5. Verify the module-level variable is gone — only `chrome.storage` data persists

---

## Interpreting Gate Failures

**Gate FAIL — unused permissions:**
- Search codebase for each declared permission's API prefix (`storage`, `tabs`, etc.)
- If `chrome.tabs.query` not found but `tabs` declared → remove permission
- Use `web-ext lint` to detect unused permissions automatically

**Gate FAIL — CSP violation:**
- `Refused to execute inline script` in console → remove all `onclick=`, `onload=` attributes
- `Refused to load script from` → all scripts must be local to extension
- Check manifest `content_security_policy` — must not include `unsafe-inline` or `unsafe-eval`

**Gate FAIL — service worker state loss:**
- Find all module-level variables used for persistent state
- Move each to `chrome.storage.local` or `chrome.storage.session`
- Add `chrome.runtime.onStartup` listener to reinitialize session state

**Gate FAIL — content script message origin not validated:**
- Find all `window.addEventListener('message', ...)` handlers
- Add `if (event.source !== window) return` check
- Add origin validation where cross-origin messages are not expected

---

## Store Submission Verification

Before submitting to Chrome Web Store:
```bash
# Package as zip
npx wxt zip

# Verify zip contents (should not contain source, node_modules, secrets)
unzip -l dist/<extension>-chrome.zip

# Run Chrome's extension analyzer (if available)
# Or manually verify at chrome://extensions in Developer mode
```

Before submitting to Firefox AMO:
```bash
npx wxt zip -b firefox

# Firefox validator
npx web-ext lint --source-dir dist/firefox-mv3/
```
