# Tauri Framework

Loaded by Apply when src-tauri/tauri.conf.json is detected.

## Version baseline

Tauri 2.x. Tauri 2 introduced the capabilities system (default-deny for all IPC).

## Security model — capabilities

Tauri uses a default-deny capability system. Every command exposed to the frontend must be explicitly declared:

```json
// src-tauri/capabilities/default.json
{
  "identifier": "default",
  "description": "Default capability set",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:allow-read-text-file",
    "dialog:allow-open"
  ]
}
```

Spec must declare: which permissions are granted and why. Never use wildcard permissions.

## Commands (Rust backend)

```rust
// src-tauri/src/lib.rs
#[tauri::command]
async fn read_file(path: String) -> Result<String, String> {
    // Validate path — Tauri does not do this for you
    std::fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![read_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application")
}
```

- Commands are `async` by default in Tauri 2
- Return `Result<T, E>` where E is serializable — errors surface as rejected promises in the frontend
- Validate all inputs in Rust — the frontend is untrusted

## Frontend invocation

```typescript
import { invoke } from '@tauri-apps/api/core'

const content = await invoke<string>('read_file', { path: '/path/to/file' })
```

## Webview

Tauri uses the OS webview (WKWebView on macOS/iOS, WebView2 on Windows, WebKitGTK on Linux). This means:

- CSS/JS compatibility depends on OS webview version — test on target OS
- Windows WebView2 requires WebView2 runtime to be installed (bundled or evergreen)
- No Chromium DevTools by default — enable in development config only

## Events

```rust
// Rust → frontend
app.emit("data-ready", payload).unwrap();

// Frontend → Rust (via event listener)
use tauri::Listener;
app.listen("user-action", |event| { /* handle */ });
```

Events are fire-and-forget. Use commands for request/response patterns.

## Updater

```toml
# Cargo.toml
[dependencies]
tauri = { features = ["updater"] }
```

```json
// tauri.conf.json
{
  "plugins": {
    "updater": {
      "endpoints": ["https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"],
      "pubkey": "..."
    }
  }
}
```

Tauri updater verifies signatures on all update packages. Declare: endpoint URL, public key rotation policy.

## Bundle size advantage

Tauri apps are significantly smaller than Electron (no bundled Chromium). Typical:
- Electron: 50-150MB installed
- Tauri: 5-15MB installed

This is a distribution advantage — declare in spec if size is a concern.
