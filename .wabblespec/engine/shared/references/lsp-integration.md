# LSP Integration

22-language LSP availability, diagnostics usage, and module integration patterns. Consumers: apply, gateway-engineering.

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

## Diagnostic severity mapping

| LSP severity | WabbleSpec interpretation |
|---|---|
| Error | Blocks receipt PASS — must be resolved |
| Warning | Flagged in receipt — does not block |
| Information | Recorded — no action required |
| Hint | Ignored unless explicitly requested |

## Fallback when LSP unavailable

If LSP server is not running or language is not in supported list: note `lsp_available: false` in receipt. Do not fail. Apply static analysis fallback (grep for obvious patterns) and note reduced confidence.
