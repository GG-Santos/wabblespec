# Cold-Start Behavior — Runtime Probe

Defines what Runtime Probe does when its expected upstream artifacts are absent.

## Absent: runtime-state.json

Condition: `.wabblespec/runtime-state.json` does not exist.
Detection: File read returns 404.
Action: Write capability defaults. Runtime Probe is designed to run first and detect from the live environment — absence of a prior runtime-state.json is the expected cold-start condition, not an error.
Output: Fresh `runtime-state.json` with all eight capability descriptors set to their detected or default values.

## Absent: prior receipts

Condition: No receipts from upstream modules.
Detection: `.wabblespec/state/receipts/` is empty or missing expected stems.
Action: Runtime Probe has no upstream receipt dependencies — proceed normally.
Do NOT: Pause or surface DEPENDENCY errors.

## Default state on cold start

| Capability descriptor | Default (if detection fails) |
|---|---|
| `reasoning` | `standard` |
| `context_window` | `large` |
| `vision` | `absent` |
| `tool_use` | `native` |
| `output_length` | `standard` |
| `multilingual` | `standard` |
| `code_execution` | `absent` |
| `file_access` | `absent` |

Defaults are conservative. If any capability cannot be detected with confidence, default to the lower tier. ModelRouter must not assume a capability not declared in runtime-state.json.
