# CLI Engineering — Performance Budgets

## Startup Time

**Budget:** Cold start < 100ms for short-lived commands.

Cold start = time from process launch to first byte on stdout (or first prompt, for interactive commands).

**Measurement:**
```bash
time <tool> --version          # simplest: no side effects
hyperfine '<tool> --version'   # statistical: use if available
```

**Why this matters for CLI:** Users run CLIs in tight loops, from scripts, and in CI pipelines. A 500ms startup time on a CI job that runs 200 times costs 100 seconds. Users notice tools that feel slow before they do anything.

**Violations — common causes:**
- Loading all subcommand dependencies at startup (fix: lazy-load per subcommand)
- Importing large libraries unconditionally (fix: dynamic import / deferred require)
- Synchronous network check on startup (fix: async, opt-in, or remove)
- JIT warm-up cost for scripting languages (fix: PyInstaller/Nuitka for Python, ncc for Node)

---

## Runtime Memory

**Budget:** Declared per project. No universal default.

Suggested starting points:
- Simple file processor: < 50MB RSS
- Network-connected tool: < 100MB RSS
- Data transformation: < 200MB RSS (scale with input size — declare O(n) behavior)

**Measurement:**
```bash
/usr/bin/time -v <tool> <cmd>    # Linux
\time -l <tool> <cmd>            # macOS
```

---

## No Unnecessary Startup Dependencies

**Rule:** Do not load dependencies that are not needed for the invoked subcommand.

**Verification:** Profile import tree at startup. For Node: `node --trace-require`. For Python: `python -X importtime`. For Go/Rust: binary size and symbol inspection.

**Pattern:** Structure code so subcommand handlers import their own dependencies, not the top-level entry point.

---

## Binary Size (Go / Rust)

| Target | Budget | Notes |
|---|---|---|
| Go binary (no CGO) | < 15MB | Typical for most CLIs |
| Rust binary (stripped) | < 5MB | Aggressive but achievable |
| Node bundle (esbuild) | < 2MB | For the JS file; node runtime is separate |
| PyInstaller binary | < 30MB | Python runtime bundled — document this |

These are defaults. Declare actual budget in design-document.md. If exceeded, justify.

**Size reduction techniques:**
- Go: `go build -ldflags="-s -w"` strips debug symbols
- Rust: `strip = true` in `[profile.release]` + `opt-level = "z"` (size over speed)
- Both: UPX compression (last resort — adds startup latency, defeats fast-startup goal)

---

## Pipe Performance

**Rule:** When piped (non-TTY stdout), the CLI must not buffer output unnecessarily.

**Verification:** `<tool> <cmd> | head -1` must return the first line without waiting for full output (for streaming commands).

**Pattern:** Flush stdout after each logical output unit. Do not batch all output and flush at exit.

---

## Interactive Mode (if applicable)

If the CLI has an interactive REPL mode:
- First prompt: < 200ms
- Response latency: < 50ms for local operations
- Readline/history: supported, or explicitly not supported (document in design-document)
