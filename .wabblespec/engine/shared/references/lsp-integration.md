# LSP Integration

22-language LSP availability, diagnostics usage, and module integration patterns. Consumers: apply, gateway-engineering, executor (Step 3c gate), verifier (Test mode pre-check), explore (via serena MCP), guard (Layer 5 warning on LSP error presence).

## Claude Code Plugin Installation

LSP plugins are installed via the Claude Code plugin system (not via npm/pip separately). Each plugin wires a language server binary into Claude Code's editing protocol. Availability is per-user and per-machine — executor and verifier check availability at wave time, not at session start.

| Plugin ID | Language | Install binary |
|---|---|---|
| `pyright-lsp` | Python | `pip install pyright` or `npm install -g pyright` |
| `typescript-lsp` | TypeScript/JS | `npm install -g typescript-language-server typescript` |
| `rust-analyzer-lsp` | Rust | `rustup component add rust-analyzer` |
| `gopls-lsp` | Go | `go install golang.org/x/tools/gopls@latest` |
| `clangd-lsp` | C/C++ | `winget install LLVM.LLVM` (Windows) |
| `jdtls-lsp` | Java | `brew install jdtls` (macOS) |
| `kotlin-lsp` | Kotlin | `brew install JetBrains/utils/kotlin-lsp` |
| `csharp-lsp` | C# | `dotnet tool install --global csharp-ls` |
| `ruby-lsp` | Ruby | `gem install ruby-lsp` |
| `swift-lsp` | Swift | bundled with Xcode / `brew install swift` |
| `php-lsp` | PHP | `npm install -g intelephense` |
| `lua-lsp` | Lua | `brew install lua-language-server` |

## LSP availability by language

| Language | Server | Diagnostics | Completion | Rename | References |
|---|---|---|---|---|---|
| TypeScript/JS | ts-ls / tsserver | Yes | Yes | Yes | Yes |
| Python | pylsp / pyright | Yes | Yes | Yes | Yes |
| Rust | rust-analyzer | Yes | Yes | Yes | Yes |
| Go | gopls | Yes | Yes | Yes | Yes |
| Java | jdtls | Yes | Yes | Yes | Yes |
| C# | OmniSharp / roslyn | Yes | Yes | Yes | Yes |
| C/C++ | clangd | Yes | Yes | Yes | Yes |
| Ruby | solargraph / ruby-lsp | Yes | Partial | Yes | Yes |
| PHP | intelephense | Yes | Yes | Yes | Yes |
| Kotlin | kotlin-language-server | Yes | Yes | Yes | Yes |
| Swift | sourcekit-lsp | Yes | Yes | Yes | Yes |
| Dart | dart-language-server | Yes | Yes | Yes | Yes |
| Scala | metals | Yes | Yes | Yes | Yes |
| Haskell | haskell-language-server | Yes | Yes | Yes | Yes |
| Elixir | elixir-ls | Yes | Yes | Yes | Yes |
| Lua | lua-language-server | Yes | Yes | Yes | Yes |
| R | languageserver | Partial | Partial | No | No |
| Julia | LanguageServer.jl | Yes | Partial | Yes | Yes |
| YAML | yaml-language-server | Yes | Yes | No | No |
| JSON | vscode-json-languageserver | Yes | Yes | No | No |
| Markdown | marksman | Partial | No | No | Yes |
| SQL | sqls / sqlfluff | Partial | No | No | No |

## Module integration patterns

### Apply (code modification)
Before writing code changes, request LSP diagnostics on the target file. If diagnostics show existing errors: note them in receipt but do not fix unless they are in scope. After writing: request diagnostics again. New errors introduced = scope violation (Guard flag).

### Gateway-engineering
Use LSP workspace symbols to verify that renamed identifiers propagate correctly. Check references before deletion — if LSP reports references exist, deletion is a breaking change requiring human confirmation.

### Executor (Step 3c — post-implementation gate)
After implementation and before Verifier, collect LSP diagnostics on wave output files. Gate rule: 0 errors → proceed; 1+ errors → surface and enter REVISE loop (LSP check takes priority over Verifier invocation). Record `lsp_diagnostics_checked: true`, `lsp_error_count: N` in wave receipt. Skip silently when LSP unavailable or wave produces no language files.

### Verifier (Test mode pre-check)
Before running the test suite in Test mode: collect LSP diagnostics. If 1+ errors: FAIL immediately, report diagnostic list as `fix_recommendation`. Do not run test suite over type-errored code. Record `lsp_errors_checked: true` in verification receipt.

### Explore (via Serena MCP)
Serena wraps multiple LSP servers in one MCP interface and adds semantic search. When `serena` MCP is active, Explore uses `serena_find_references`, `serena_go_to_definition`, and `serena_list_symbols` instead of grep-based traversal for high-value node discovery. See `mcp-servers-integration.md` for Serena call patterns.

### Guard (Layer 5 extension)
Project-specific guard rules (`.claude/guard.<name>.local.md`) can monitor LSP error state by pattern-matching on shell commands or file edits. A rule that fires on `pyright --outputjson` output with non-zero error count can block a wave with LSP errors from proceeding. See guard skill `Project-Specific Guard Rules` section for rule format.

## Diagnostic severity mapping

| LSP severity | WabbleSpec interpretation |
|---|---|
| Error | Blocks receipt PASS — must be resolved |
| Warning | Flagged in receipt — does not block |
| Information | Recorded — no action required |
| Hint | Ignored unless explicitly requested |

## Fallback when LSP unavailable

If LSP server is not running or language is not in supported list: note `lsp_available: false` in receipt. Do not fail. Apply static analysis fallback (grep for obvious patterns) and note reduced confidence.
