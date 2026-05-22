# Extra References — v6.1 Extraction Cards

> Source: `C:\Vaults\references\Extra Project References\`
> These repos were partially mapped in EXTRA-REFERENCE-INTEGRATION-MAP.md (v6) but need v6.1-specific extraction.
> Two repos (agent-creator, claude-code-main) are NEW — not in v6 ledger at all.

---

## agent-creator [NEW — not in v6 ledger]

**Location:** `Extra Project References\agent-creator\`
**Files:** `SKILL.md`, `references/prompt-patterns.md`
**v6.1 relevance: TOP — Reviewer agent + Executor agent design**

### Key facts

- Agents = isolated context windows. Skills = shared context.
- `description` field is PRIMARY TRIGGERING MECHANISM — determines invocation.
- Tool count directly impacts token budget: 3-5 tools = 2-5k tokens; 15+ tools = 15-25k tokens.

### What to copy for v6.1

**Agent description pattern:**
```yaml
description: [Role/capability]. MUST BE USED for [specific scenarios]. Examples: "[trigger 1]", "[trigger 2]"
```

**Minimal viable toolset by agent type:**
- Read-only (Reviewer): `Glob, Grep, Read, LS`
- Research (Researcher): add `WebFetch, WebSearch`
- Planning (Specify agent): add `Write, Edit, TodoWrite`
- Implementation (Executor): add `Bash, Task`
- Orchestrator: `Glob, Grep, Read, LS, Task, TodoWrite`

**Agent system prompt structure:**
```
# [Role Title]
[One-sentence mission]
## Core Principles
## Responsibilities / Methodology
## Quality Standards / Output Format
## Constraints (YOUR ROLE ENDS HERE)
```

**Hard Stop pattern** (use in Reviewer, Verifier agents):
```markdown
## YOUR ROLE ENDS HERE
CRITICAL BOUNDARY: You are strictly a [role]. Once you have [completed action]:
- DO NOT [prohibited action]
- [Other role] handles [out-of-scope actions]
```

**Quality gates pattern** (use in Verifier):
```markdown
## Quality Gates (ALL Must Pass)
- [ ] [Criterion]
If ANY gate fails, do not proceed.
```

### What to avoid
- Over-engineering: 15+ tool agents, 30k token prompts, one mega-agent
- Vague descriptions ("helps with coding")
- Tool overload "just in case"
- Missing "done" criteria

### Application to v6.1 modules

| v6.1 module | agent-creator pattern to apply |
|---|---|
| Reviewer subagent | Hard Stop pattern + Read-only toolset + Adversary persona |
| Verifier | Quality Gates pattern + output format spec |
| Executor | Numbered Steps pattern + boundary definition |
| Receipt schema | Output Format Specification pattern |

---

## claude-code-main [NEW — not in v6 ledger]

**Location:** `Extra Project References\claude-code-main\`
**Key file:** `examples/hooks/bash_command_validator_example.py`
**v6.1 relevance: TOP — Hook implementation blueprint**

### What this is

Official Anthropic Claude Code repository. Contains the canonical hook example: a `PreToolUse` hook for the Bash tool that reads JSON from stdin, validates the command, and exits with code 0 (pass), 1 (warn user), or 2 (block + show Claude).

### Hook exit code contract

```
exit 0  → allow tool call to proceed
exit 1  → show stderr to user, does NOT block Claude
exit 2  → block tool call, show stderr to Claude (Claude sees the error)
```

### Exact hook pattern for v6.1 receipt validator

```python
import json, sys

def main():
    input_data = json.load(sys.stdin)
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    
    # Check receipt existence here
    # If missing: sys.exit(2) to block + inform Claude
    # If present: sys.exit(0) to allow

if __name__ == "__main__":
    main()
```

**settings.json hook registration:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{ "type": "command", "command": "python3 /path/to/receipt-validator.py" }]
      }
    ]
  }
}
```

### Specific to WabbleSpec receipt hook

The receipt validator should:
1. Read `tool_name` and `tool_input` from stdin JSON
2. Check if upstream receipt exists in `.wabblespec/receipts/`
3. If missing: exit 2 with message "Receipt missing: [phase]. Run Verifier first."
4. If present and valid: exit 0

This is a **PowerShell script on Windows** (not Python) since WabbleSpec targets Windows/PowerShell:
```powershell
$input_data = $env:STDIN | ConvertFrom-Json
# Check .wabblespec/receipts/ for required receipt
# Exit 2 if missing
```

### Also in this repo

- `.claude/commands/`: slash commands for commit-push-pr, dedupe, triage-issue — pattern reference for WabbleSpec command structure
- `.claude-plugin/marketplace.json`: plugin manifest format reference
- `.github/workflows/claude.yml`: GitHub Actions + Claude Code integration pattern

---

## toprank-main

**Location:** `Extra Project References\toprank-main\`
**v6.1 relevance: HIGH — Verifier + Archive**

### Key patterns for v6.1

| Pattern | What it does | Apply to |
|---|---|---|
| Manifest-driven modules | Each module declares its own eval fixtures | Verifier acceptance criteria |
| Fixture-backed E2E evals | Test cases are stored fixtures, not ad-hoc | Verifier test suite |
| LLM judge | AI evaluates output against rubric | Reviewer adversarial check |
| Eval persistence | Results stored to file, not ephemeral | Archive receipt index |
| Touchfile-based eval selection | Run only relevant evals per change | Progressive loading |
| Policy gates | Gate on PASS/FAIL, block on FAIL | Receipt chain enforcement |

**Critical caution:** Live mutation workflows need approval gates and rollback receipts.

### What to extract for Receipt schema

Toprank's eval persistence pattern maps to WabbleSpec receipt structure:
- Each eval run produces a persisted result record
- Records are indexed by phase + timestamp
- Policy gate checks record before allowing next phase

---

## pentest-ai-agents-main

**Location:** `Extra Project References\pentest-ai-agents-main\`
**v6.1 relevance: HIGH — Archive (findings DB) + Verifier (status transitions)**

### Key patterns for v6.1

| Pattern | What it does | Apply to |
|---|---|---|
| YAML role frontmatter | Declares agent authority scope | skill-rules.json authority |
| Router commands | Route tasks by type to handlers | Recipe target routing |
| Findings DB | Append-only record of verification results | Archive receipt index |
| Status transitions | OPEN → IN_PROGRESS → RESOLVED → VERIFIED | Receipt state machine |
| Scope guard | Block execution outside declared scope | Guard invariant enforcement |
| Reproducibility fields | Every finding records its reproduction steps | Receipt provenance |

**Status transition model** (apply to receipt schema):
```
PENDING → IN_PROGRESS → PASS | FAIL | BLOCKED
```

**Caution:** Do not import offensive instructions. Keep authorized-use boundaries.

---

## context-mode-main

**Location:** `Extra Project References\context-mode-main\`
**v6.1 relevance: HIGH — Memory (session continuity, SQLite/FTS5)**

### Key patterns for v6.1

| Pattern | What it does | Apply to |
|---|---|---|
| SQLite/FTS5 retrieval | Full-text search over stored context | MemorySearch |
| Session continuity | State survives session boundaries | Memory staleness tracking |
| Hook-based context injection | Load relevant memory via pre-tool-use hook | Memory retrieval gate |
| Sandboxed verbose tool output | Isolate large tool outputs from main context | Context economy |
| `doctor/stats/insight` commands | Diagnostics for memory state | `/wabble-health` equivalent |

**Key lesson for WabbleSpec Memory:**
- SQLite + FTS5 is a viable plain-file-adjacent approach (single `.db` file, no server)
- Avoids embedding dependency while still enabling structured search
- Session continuity via stored state proves FRESH/EXPIRED tracking is implementable

**Caution:** Treat implementation as reference, not module naming (corrupted text in some files).

---

## claude-ads-main

**Location:** `Extra Project References\claude-ads-main\`
**v6.1 relevance: MED — Command routing + Receipt scoring**

### Key patterns for v6.1

| Pattern | What it does | Apply to |
|---|---|---|
| Thin command router | Single entry point routes to bounded subskills | Recipe detection |
| Bounded subskills | Each subskill has declared scope | Module authority |
| Weighted PASS/WARNING/FAIL scoring | Graded output not binary | Verifier receipt format |
| Preflight report gate | Run checks before main task | Guard pre-execution |
| CI checks | Automated quality gates | Hook enforcement |

**PASS/WARNING/FAIL scoring** — apply to Verifier receipt:
- PASS: all checks green
- WARNING: non-blocking issues found, documented
- FAIL: blocking issue, pipeline halted

**Keep:** Source branding/community material as provenance-only (do not copy content).

---

## hyperframes-main

**Location:** `Extra Project References\hyperframes-main\`
**v6.1 relevance: MED — Archive (deterministic render/receipt)**

### Key patterns for v6.1

| Pattern | What it does | Apply to |
|---|---|---|
| Deterministic render loop | Same input → same output, verified | Receipt reproducibility |
| Preview/render/lint CLI | Three-phase check before artifact acceptance | Verifier check sequence |
| Adapter registry | Register output handlers by type | Platform package routing |
| Media regression checks | Detect output drift between runs | Verifier regression gate |
| Multi-runtime plugin manifests | Declare runtime deps per module | skill-rules.json |

**Check license and install requirements** before using runtime/asset dependencies.

---

## Open-LLM-VTuber-main

**Location:** `Extra Project References\Open-LLM-VTuber-main\`
**v6.1 relevance: LOW — Provider abstraction (deferred)**

| Pattern | v6.1 relevance |
|---|---|
| Provider/modality abstraction | Validates RuntimeProbe direction but deferred |
| Offline/local provider support | Validates local-first Memory design |
| Device permission notes | Platform Mobile gate reference |

**Do not copy:** Character assets or brand identity.
**Defer:** All provider abstraction until single-Claude deployment is proven.
