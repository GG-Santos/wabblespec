# Extension Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Manifest Validation

**Check:** Manifest is valid for declared manifest version. All required fields present.

**Method:**
```bash
npx web-ext lint --source-dir dist/
# Chrome: load unpacked in chrome://extensions — must load without errors
```

**Pass:** Zero lint errors. Extension loads in target browser without errors.
**Fail:** Any manifest validation error or extension load failure.

---

## Gate 2: Permission Audit

**Check:** Every declared permission is used. No speculative permissions. Host permissions minimized.

**Method:**
```bash
# List declared permissions
cat dist/manifest.json | jq '.permissions, .host_permissions'

# For each permission, verify usage in source:
grep -r "chrome.storage" src/       # for 'storage' permission
grep -r "chrome.tabs" src/          # for 'tabs' permission
```

**Pass:** Every permission has at least one API call in source. No permission present with zero uses.
**Fail:** Any declared permission with no corresponding API usage in source.

---

## Gate 3: Content Security Policy

**Check:** Extension pages declare strict CSP. No `unsafe-inline`, no `unsafe-eval`, no external script sources.

**Method:**
```bash
cat dist/manifest.json | jq '.content_security_policy'
# Must contain: script-src 'self'; object-src 'none';
# Must NOT contain: unsafe-inline, unsafe-eval, http://, https:// in script-src
```

**Pass:** CSP present with `script-src 'self'` and `object-src 'none'`. No unsafe values.
**Fail:** CSP absent, contains `unsafe-inline`, contains `unsafe-eval`, or allows external script sources.

---

## Gate 4: No innerHTML with External Data

**Check:** No assignment of externally-sourced strings to innerHTML.

**Method:**
```bash
grep -n "innerHTML" src/**/*.ts src/**/*.js
# Review each match — verify no external/storage/message data assigned without sanitization
```

**Pass:** Zero innerHTML usages with external data. All innerHTML usages use only static string literals.
**Fail:** Any innerHTML assignment with data sourced from storage, messages, fetch, or page content.

---

## Gate 5: Message Origin Validation

**Check:** All postMessage handlers validate sender origin.

**Method:**
```bash
grep -n "addEventListener.*message" src/**/*.ts
# For each match, verify event.source and event.origin checks are present
```

**Pass:** Every `message` event listener includes `event.source` validation. Cross-origin handlers include `event.origin` validation.
**Fail:** Any message listener without origin validation.

---

## Gate 6: Service Worker State Correctness

**Check:** No persistent state stored in module-level variables. All persistent state in chrome.storage.

**Method:**
```bash
grep -n "^let\|^var\|^const" src/background.ts
# Review each — module-level variables must not hold state that must survive SW termination
```

**Manual test:** Load extension, trigger actions, wait for SW to terminate (30s), trigger again. State must be correct.

**Pass:** No module-level variables holding persistent state. All data read from chrome.storage on each message.
**Fail:** Any persistent state in module scope that is lost on service worker termination.

---

## Gate 7: No Remote Code Execution

**Check:** No eval, new Function, remote script injection, or external script loading.

**Method:**
```bash
grep -rn "eval(" src/
grep -rn "new Function(" src/
grep -rn "setTimeout.*string" src/
grep -rn "script.*src.*http" src/
```

**Pass:** Zero matches for all patterns.
**Fail:** Any match found.

---

## Gate 8: Extension Loads in Target Browsers

**Check:** Built extension loads without errors in all declared target browsers.

**Method:**
```bash
# Chrome: load unpacked dist/chrome-mv3/ in chrome://extensions
# Firefox: load dist/firefox-mv3/ via about:debugging
# Verify: background SW console shows no errors; content scripts inject correctly
```

**Pass:** Extension loads in all target browsers. Zero console errors on load. Core functionality verified manually.
**Fail:** Extension fails to load, or produces console errors on load in any target browser.

---

## Gate 9: Store Submission Package

**Check:** Packaged zip contains only distribution files. No source, no secrets, no test data.

**Method:**
```bash
npx wxt zip
unzip -l dist/<extension>-chrome.zip
# Must NOT contain: src/, test/, .env, node_modules/, *.key, *.pem
```

**Pass:** Zip contains only: manifest.json, bundled JS files, HTML files, icons, and declared web-accessible resources.
**Fail:** Any source file, secret, or test fixture present in submission package.

---

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Manifest validation | Yes |
| 2 | Permission audit — no unused permissions | Yes |
| 3 | Content Security Policy strict | Yes |
| 4 | No innerHTML with external data | Yes |
| 5 | Message origin validation | Yes |
| 6 | Service worker state correctness | Yes |
| 7 | No remote code execution | Yes |
| 8 | Loads in all target browsers | Yes |
| 9 | Store submission package clean | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
