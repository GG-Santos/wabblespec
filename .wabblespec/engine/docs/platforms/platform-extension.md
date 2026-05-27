# Platform: Extension / Plugin

Browser extension or editor plugin target. Activates when Recipe identifies a browser extension (Chrome, Firefox, Safari) or editor plugin (VS Code, JetBrains, etc.) as the primary build target.

**Skill:** `modules/l3/extension/SKILL.md`

## What makes Extension different

| Concern | Extension approach |
|---------|-------------------|
| Permission minimization | Manifest permissions declared minimal — every permission justified |
| Manifest compliance | Manifest V3 (Chrome/Edge), WebExtensions API (Firefox/Safari) — declared |
| Host API boundary | Which host APIs are used declared — updates to host APIs tracked |
| Content script isolation | Content script injection scope declared; world isolation declared |
| Background service worker | MV3 service worker lifecycle constraints acknowledged |
| Store review | App store review guidelines followed; rejection risks identified |
| Cross-browser | Target browsers declared; polyfill strategy for browser differences |

## Platform-specific spec sections

- Manifest: complete manifest.json specification — permissions, content scripts, background, host permissions
- Content script injection: which pages, which contexts, what world
- Message passing: all `chrome.runtime.sendMessage` / `postMessage` patterns declared with schema
- Storage: what is stored in `chrome.storage.local` vs `session` vs `sync` — size budget
- Cross-origin requests: all external origins listed in host_permissions with justification

## Security controls loaded

- Permission scope: no `<all_urls>` without justification; specific host patterns preferred
- Content script XSS: content scripts must not inject user-controlled HTML without sanitization
- Message validation: all messages received via `runtime.onMessage` validated before acting
- Third-party scripts: no third-party scripts injected into pages — only first-party content scripts
- Data exfiltration: content scripts must not send page content to external servers without user knowledge

## Gateway interaction

Extension targets typically activate:
- `gateway-security` — always (content script injection, host permissions, message passing)
- `gateway-engineering` — always (manifest compliance, service worker constraints)
- `gateway-aesthetic` — for popup/options UI work
- `gateway-experience` — for user-facing UI features
