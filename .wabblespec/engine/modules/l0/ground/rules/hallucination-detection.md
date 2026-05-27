# Hallucination Detection Rules

Ground uses these rules to detect hallucinated claims — assertions about the current state of the codebase that cannot be confirmed against actual files.

## What counts as a hallucination risk

A hallucination risk is any claim in a task card or wave plan that:
1. States a file, function, class, API, or configuration key EXISTS in the current codebase
2. States a behavior CURRENTLY WORKS (before this wave executes)
3. States a dependency IS INSTALLED at a specific version
4. States a schema or type IS DEFINED somewhere in the repo

These claims are verifiable. If they are false, the wave plan built on them will fail unexpectedly mid-execution.

## Detection patterns

### Pattern H1: File existence claims

Trigger phrases:
- "reads from [path]"
- "the existing [filename]"
- "in [file], there is"
- "modify [path]"
- "extends [ClassName]" (implies class exists)

Verification: `Path(claimed_path).exists()`

### Pattern H2: Symbol existence claims

Trigger phrases:
- "calls [functionName]"
- "implements [InterfaceName]"
- "uses [ClassName]"
- "[functionName] currently returns"

Verification: grep for symbol name in declared file. Symbol absent = UNVERIFIED.

### Pattern H3: API contract claims

Trigger phrases:
- "endpoint /[path] exists"
- "the [METHOD] /[path] route"
- "the API currently returns [schema]"

Verification: grep for route/path declaration in router files. Schema check requires reading file.

### Pattern H4: Dependency claims

Trigger phrases:
- "using [library]@[version]"
- "[library] is installed"
- "requires [dependency]"

Verification: read package.json / requirements.txt / go.mod / Cargo.toml for dependency + version.

### Pattern H5: Test state claims

Trigger phrases:
- "tests currently pass"
- "the existing tests cover"
- "test [name] verifies"

Verification: check test file exists and test name exists. Pass/fail state: UNVERIFIABLE (mark as ASSUMED).

### Pattern H6: Configuration claims

Trigger phrases:
- "[KEY] is configured in [file]"
- "the config file sets [key]"
- "[env var] is defined"

Verification: read config file, check for key presence.

## Non-hallucination claims (do not flag)

These describe future state, not current state — they are the task's goals, not preconditions:
- "will create [file]"
- "will implement [function]"
- "should return [value]"
- "after this wave, [behavior]"

Do not flag future-state claims as hallucination risks.

## Output format per finding

```json
{
  "pattern": "H1|H2|H3|H4|H5|H6",
  "claim": "exact claim text from task card",
  "verification_method": "file_exists|grep|package_manifest|config_read|unverifiable",
  "result": "VERIFIED|UNVERIFIED|ASSUMED|MISSING",
  "evidence": "file path or null",
  "note": "optional explanation"
}
```

## Severity mapping

| Result | Severity | Effect on ground receipt |
|---|---|---|
| VERIFIED | None | Added to `verified` bucket |
| UNVERIFIED | WARNING | Added to `unverified` bucket; Executor flagged |
| ASSUMED | INFO | Added to `assumed` bucket; no blocking |
| MISSING | ERROR if prerequisite, WARNING if optional | MISSING prerequisite → BLOCK status |

## What Ground does NOT do

- Does not execute code or run tests
- Does not infer behavior from reading code
- Does not make judgment calls about whether code is "correct"
- Does not check performance, security, or correctness — only existence and structure
- Does not flag future-state claims as hallucinations
