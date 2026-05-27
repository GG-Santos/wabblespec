# Extension Systems Design Template (P2)

> **Platform:** Extension/Plugin
> **Template version:** 1.0
> **Prerequisite:** design-document.md `[REQUIRED]` sections complete.

---

## Build Pipeline

```
src/
  background.ts
  content.ts
  popup/
  options/
  └── Build tool (webpack/vite/parcel)
        ├── background.js     → dist/
        ├── content.js        → dist/
        ├── popup.html+js     → dist/
        ├── manifest.json     → dist/
        └── assets/           → dist/
```

**Build tool:** [ ] Webpack [ ] Vite [ ] Parcel [ ] esbuild direct [ ] WXT [ ] Plasmo

**Why:** ___

**Output:** Single `dist/` directory that is the loadable extension.

---

## Message Passing Architecture

All cross-component communication must be explicit and validated.

```
┌─────────────┐    sendMessage     ┌─────────────────┐
│   Popup     │ ────────────────► │   Background    │
│  (ext page) │ ◄──────────────── │ (service worker)│
└─────────────┘    response        └────────┬────────┘
                                            │ sendMessage
                                            ▼
                                   ┌─────────────────┐
                                   │ Content Script  │
                                   │ (isolated world)│
                                   └─────────────────┘
```

**Message schema:** All messages typed:
```typescript
type Message =
  | { type: 'GET_DATA'; payload: { id: string } }
  | { type: 'SET_PREF'; payload: { key: string; value: unknown } }
```

**Message validation:** Background validates `message.type` against known types before processing.

---

## Storage Strategy

| Data type | Storage API | Reason |
|---|---|---|
| User preferences | `chrome.storage.sync` | Syncs across devices |
| Session state | `chrome.storage.session` | Cleared on browser close |
| Large local data | `chrome.storage.local` | Higher quota (10MB) |
| Sensitive data | `chrome.storage.local` (encrypted) | sync is not encrypted |

**No in-memory singletons for persistent state** — service worker will terminate.

**Storage quota management:** `chrome.storage.local` limit is 10MB. Declare strategy for approaching limit.

---

## Content Script Isolation

Content scripts run in an isolated world — they share the DOM but not JS namespace with the page.

**DOM access pattern:** Content scripts should:
1. Query DOM elements by specific selectors
2. Observe mutations via `MutationObserver` for dynamic pages
3. Never eval page scripts or inject `<script>` tags with `src` pointing to non-extension resources

**postMessage validation:**
```javascript
window.addEventListener('message', (event) => {
  if (event.source !== window) return          // reject non-window sources
  if (event.origin !== location.origin) return // reject cross-origin
  if (!isValidMessage(event.data)) return      // reject unknown types
})
```

---

## Offscreen Documents (MV3)

Required for operations that need DOM or Web Audio API in background:

| Operation | Offscreen reason | Document URL |
|---|---|---|
| Audio playback | `AUDIO_PLAYBACK` | `offscreen.html` |
| Clipboard access | `CLIPBOARD` | `offscreen.html` |
| DOM parsing | `DOM_PARSER` | `offscreen.html` |

Only one offscreen document per extension. Manage lifecycle explicitly.

---

## Cross-Browser Compatibility

| Feature | Chrome | Firefox | Edge | Approach |
|---|---|---|---|---|
| Service worker | MV3 native | Supported (FF 109+) | MV3 native | Standard |
| `browser` namespace | Via polyfill | Native | Via polyfill | `webextension-polyfill` |
| `declarativeNetRequest` | MV3 | Supported | MV3 | Use instead of webRequest |

**Polyfill:** `webextension-polyfill` for cross-browser `browser.*` namespace consistency.

---

## VS Code Extension Architecture (if applicable)

```
extension.ts (activate/deactivate)
  ├── Commands (vscode.commands.registerCommand)
  ├── Language features (providers)
  │     ├── CompletionItemProvider
  │     ├── HoverProvider
  │     └── DiagnosticCollection
  ├── Tree views (vscode.window.createTreeView)
  └── Webview panels (for complex UI)
```

**Activation events:** Declare specific events, not `*` (activates on all events — bad for performance):
```json
"activationEvents": ["onLanguage:typescript", "onCommand:myext.doThing"]
```
