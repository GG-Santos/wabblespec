# Ref-Eval: claude-code-security-review-main

**Date:** 2026-05-31  
**Slug:** claude-code-security-review-main  
**Trust level:** MEDIUM  
**Reference path:** `C:\Vaults\references\Core Project References\claude-code-security-review-main`

---

## File Inventory

| File | Purpose | Size | Key Contents | Status | Transfer Check |
|---|---|---|---|---|---|
| README.md | Overview, features, config | Medium | Architecture, config options, /security-review command description | Read | — |
| .claude/commands/security-review.md | Slash command definition | Medium | 3-phase methodology, 17 hard exclusion rules, 12 precedents, confidence scoring (0.7/0.8/0.9), parallel sub-task filter | Read | — |
| claudecode/prompts.py | Prompt template | Medium | JSON output schema with `exploit_scenario` field, category taxonomy (10 categories), severity/confidence tiers | Read | — |
| claudecode/findings_filter.py | Two-stage filter pipeline | Large | HardExclusionRules class with 7 pre-compiled regex category sets; FilterStats dataclass | Read | — |
| claudecode/github_action_audit.py | Main entry point | Large | Full pipeline: env config, GitHub client, diff filtering, retry logic (3x, 5s×attempt), PROMPT_TOO_LONG fallback | Read | — |
| claudecode/claude_api_client.py | Per-finding API calls | Medium | analyze_single_finding(), system prompt, retry+backoff, rate-limit handling | Read | — |
| claudecode/json_parser.py | JSON extraction | Small | Multi-strategy extractor: code blocks first, then brace-scan | Read | — |
| claudecode/constants.py | Config constants | Small | SUBPROCESS_TIMEOUT=1200, DEFAULT_MAX_RETRIES=3, RATE_LIMIT_BACKOFF_MAX=30, PROMPT_TOKEN_LIMIT=16384 | Read | I6: model names hardcoded |
| claudecode/evals/eval_engine.py | PR eval framework | Large | EvalResult dataclass, git worktree management, threading locks, timeout constants (TIMEOUT_CLAUDECODE=1800) | Read | — |
| claudecode/evals/run_eval.py | Eval CLI | Medium | repo#num spec parser, result display, JSON save | Read | — |
| claudecode/evals/README.md | Eval docs | Small | Requirements, usage, output format | Read | — |
| docs/custom-filtering-instructions.md | Filter customization guide | Small | Three-section format: HARD EXCLUSIONS / SIGNAL QUALITY CRITERIA / PRECEDENTS | Read | — |
| docs/custom-security-scan-instructions.md | Scan customization guide | Small | Custom category extension format, compliance/industry examples | Read | — |
| examples/custom-false-positive-filtering.txt | K8s-specific filter example | Small | 12 exclusions, 4 criteria, 12 precedents — shows real-world usage pattern | Read | — |
| examples/custom-security-scan-instructions.txt | Compliance scan example | Small | GDPR/HIPAA/PCI DSS/financial/e-commerce categories | Read | — |
| action.yml | GitHub Action definition | Large | Full composite step sequence, PR cache deduplication (marker+cache key pattern), pinned action hashes | Read | — |
| .github/workflows/sast.yml | Self-test CI workflow | Small | Runs action on own PRs | Read | — |
| claudecode/test_hard_exclusion_rules.py | Hard exclusion tests | Large | Boundary tests at N-1/N/N+1 for DOS/rate-limit/resource/memory-safety patterns | Read | — |
| claudecode/test_prompts.py | Prompt tests | Small (skimmed) | Prompt content assertions | Skimmed | — |
| claudecode/test_*.py (9 remaining) | Test suites | Various | Unit and integration tests | Skimmed | No additional transferable patterns beyond what test_hard_exclusion_rules.py shows |
| scripts/comment-pr-findings.js | PR comment poster | Small | GitHub Actions step to post findings as PR comments | Not read | Transfer check: JS/GitHub Actions specific — no transferable behavioral content for WabbleSpec |
| scripts/comment-pr-findings.bun.test.js | Bun test for comment script | Small | — | Not read | Transfer check: test for GitHub Actions JS — not transferable |
| scripts/package.json | Node deps | Small | — | Not read | Transfer check: bun dependency only — not transferable |

---

## Connection Map

```
[action.yml] --env-vars--> [github_action_audit.py]: GITHUB_REPOSITORY, PR_NUMBER, ANTHROPIC_API_KEY, ENABLE_CLAUDE_FILTERING, EXCLUDE_DIRECTORIES, FALSE_POSITIVE_FILTERING_INSTRUCTIONS, CUSTOM_SECURITY_SCAN_INSTRUCTIONS, CLAUDE_MODEL, CLAUDECODE_TIMEOUT, REPO_PATH
[action.yml] --cache-key--> [.claudecode-marker/marker.json]: claudecode-<repo_id>-pr-<pr_num>-<sha>; if marker exists → skip scan (deduplication)
[github_action_audit.py] --imports--> [prompts.py]: get_security_audit_prompt(pr_data, pr_diff, include_diff, custom_scan_instructions) → string
[github_action_audit.py] --imports--> [findings_filter.py]: FindingsFilter.filter_findings(findings, pr_context) → (success, filtered_results, FilterStats)
[github_action_audit.py] --imports--> [json_parser.py]: parse_json_with_fallbacks(text) → (bool, dict)
[github_action_audit.py] --subprocess--> [claude CLI]: stdin=prompt, --output-format json → stdout JSON: {type, subtype, is_error, result: "<findings-JSON-string>"}
[github_action_audit.py] --double-parse--> [json_parser.py]: parse result field string → findings JSON
[findings_filter.py] --imports--> [claude_api_client.py]: ClaudeAPIClient.analyze_single_finding(finding, pr_context, custom_instructions) → {confidence_score, keep_finding, exclusion_reason, justification}
[findings_filter.py] --imports--> [constants.py]: DEFAULT_CLAUDE_MODEL
[claude_api_client.py] --imports--> [constants.py]: DEFAULT_CLAUDE_MODEL, DEFAULT_TIMEOUT_SECONDS, DEFAULT_MAX_RETRIES, RATE_LIMIT_BACKOFF_MAX, PROMPT_TOKEN_LIMIT
[evals/eval_engine.py] --subprocess--> [github_action_audit.py]: runs full audit as child process, captures stdout JSON
[evals/run_eval.py] --imports--> [evals/eval_engine.py]: run_single_evaluation(EvalCase) → EvalResult
[.claude/commands/security-review.md] --sub-tasks--> [parallel filter sub-tasks]: one identify sub-task → N parallel false-positive filter sub-tasks (per vulnerability)
```

If `constants.py` changed `DEFAULT_CLAUDE_MODEL`: `findings_filter.py`, `claude_api_client.py`, and `github_action_audit.py` all break. Single point of I6 failure propagated to 3+ files.

---

## Dimension 1 — Behavior (operational detail)

**Multi-stage pipeline:**
1. `get_security_audit_prompt()`: Injects PR metadata + diff + 10 vulnerability categories + severity guidelines + confidence scoring thresholds + JSON output schema. Custom scan instructions appended after "Data Exposure" category (not replacing).
2. `SimpleClaudeRunner.run_security_audit()`: Subprocess Claude CLI with 3 retries (5×attempt second sleep), 1200s timeout. PROMPT_TOO_LONG error detected via `is_error: true, result: "Prompt is too long"` → retry without diff. Double-parse architecture: stdout → JSON wrapper → `.result` string → findings JSON.
3. HardExclusionRules (Stage 1 filter): Pre-compiled regex on `title + description` for 7 categories:
   - DOS: "denial of service", "exhaust.*resource", "infinite.*loop"
   - Rate limiting: "missing.*rate limit", "add.*rate limit", "unlimited.*requests"
   - Resource management: "resource leak potential", "unclosed.*resource", "database.*leak"
   - Open redirect: "open redirect", "unvalidated redirect", "malicious.*redirect"
   - Memory safety (non-C/C++ only — `.c/.cc/.cpp/.h` exempt): buffer overflow, use-after-free, OOB, segfault, integer overflow
   - Regex injection: "regex.*injection", "regex.*denial of service"
   - SSRF (HTML files only): "ssrf", "server.*side.*request.*forgery"
   - .md files: always excluded
4. Claude API Stage 2 filter: Per-finding `analyze_single_finding()` → `{confidence_score: 1-10, keep_finding: bool, exclusion_reason, justification}`. If API fails → keep finding with confidence=10.0 (fail-open).
5. FilterStats: `{total_findings, hard_excluded, claude_excluded, kept_findings, exclusion_breakdown: Dict[str,int], confidence_scores: List[float], runtime_seconds}`.

**Slash command 3-phase methodology:**
- Phase 1 (Context Research): Identify existing security frameworks, established secure coding patterns, sanitization patterns, project security model
- Phase 2 (Comparative Analysis): Compare new code vs existing patterns, identify deviations, flag inconsistent implementations, new attack surfaces
- Phase 3 (Vulnerability Assessment): Trace data flow from user inputs to sensitive operations, privilege boundary crossings, injection points

**Slash command parallel sub-task pattern:**
1. One sub-task identifies all vulnerabilities (full codebase context)
2. Per-vulnerability sub-tasks run in parallel for false positive filtering (each independently applies hard exclusion list + precedents)
3. Filter out any vulnerability where parallel sub-task returned confidence < 8

**Confidence scoring (slash command):**
- 0.9-1.0: Certain exploit path identified, tested if possible
- 0.8-0.9: Clear vulnerability pattern with known exploitation methods
- 0.7-0.8: Suspicious pattern requiring specific conditions to exploit
- Below 0.7: Do not report (too speculative)

**17-item hard exclusion list (slash command, verbatim):**
1. Denial of Service (DOS) vulnerabilities, even if they allow service disruption
2. Secrets or sensitive data stored on disk (handled by other processes)
3. Rate limiting or resource exhaustion issues
4. Memory consumption or CPU exhaustion issues
5. Lack of input validation on non-security-critical fields without proven security impact
6. Input sanitization concerns for GitHub Action workflows unless clearly triggerable via untrusted input
7. A lack of hardening measures — only flag concrete vulnerabilities
8. Race conditions or timing attacks that are theoretical rather than practical issues
9. Vulnerabilities related to outdated third-party libraries
10. Memory safety issues are impossible in Rust — do not report in Rust or any memory-safe language
11. Files that are only unit tests or only used as part of running tests
12. Log spoofing concerns — outputting un-sanitized user input to logs is not a vulnerability
13. SSRF vulnerabilities that only control the path (only concern if controlling host or protocol)
14. Including user-controlled content in AI system prompts is not a vulnerability
15. Regex injection — injecting untrusted content into a regex is not a vulnerability
16. Regex DOS concerns
16. [sic — duplicate numbering] Insecure documentation — do not report any findings in .md files
17. A lack of audit logs is not a vulnerability

**12-item precedents list (slash command, verbatim):**
1. Logging high value secrets in plaintext is a vulnerability. Logging URLs is assumed to be safe.
2. UUIDs can be assumed to be unguessable and do not need to be validated.
3. Environment variables and CLI flags are trusted values. Any attack relying on controlling an env var is invalid.
4. Resource management issues such as memory or file descriptor leaks are not valid.
5. Subtle or low impact web vulnerabilities such as tabnabbing, XS-Leaks, prototype pollution, and open redirects should not be reported unless extremely high confidence.
6. React and Angular are generally secure against XSS. Do not report XSS in React/Angular unless using `dangerouslySetInnerHTML`, `bypassSecurityTrustHtml`, or similar.
7. Most vulnerabilities in GitHub Action workflows are not exploitable in practice. Ensure concrete and very specific attack path before validating.
8. A lack of permission checking or authentication in client-side JS/TS code is not a vulnerability. Server-side is responsible for validating all inputs.
9. Only include MEDIUM findings if they are obvious and concrete issues.
10. Most vulnerabilities in ipython notebooks (.ipynb files) are not exploitable in practice. Require concrete and very specific attack path.
11. Logging non-PII data is not a vulnerability. Only report logging vulnerabilities if they expose secrets, passwords, or PII.
12. Command injection vulnerabilities in shell scripts are generally not exploitable in practice. Only report if concrete and very specific attack path for untrusted input.

**Exit code semantics:**
- 0: No HIGH severity findings
- 1: HIGH severity findings found
- 2: Configuration error

---

## Dimension 2 — Format (identifier level)

**Finding JSON schema (output from Claude):**
```json
{
  "file": "path/to/file.py",
  "line": 42,
  "severity": "HIGH|MEDIUM|LOW",
  "category": "sql_injection|xss|command_injection|...",
  "description": "User input passed to SQL query without parameterization",
  "exploit_scenario": "Attacker could extract database contents by manipulating the 'search' parameter...",
  "recommendation": "Replace string formatting with parameterized queries...",
  "confidence": 0.95
}
```

**FilterStats dataclass fields:** `total_findings: int`, `hard_excluded: int`, `claude_excluded: int`, `kept_findings: int`, `exclusion_breakdown: Dict[str, int]`, `confidence_scores: List[float]`, `runtime_seconds: float`

**EvalResult dataclass fields:** `repo_name: str`, `pr_number: int`, `description: str`, `success: bool`, `runtime_seconds: float`, `findings_count: int`, `detected_vulnerabilities: bool`, `error_message: str`, `findings_summary: Optional[List[Dict]]`, `full_findings: Optional[List[Dict]]`

**Custom filtering file format (3 sections):**
```
HARD EXCLUSIONS - Automatically exclude findings matching these patterns:
1. ...

SIGNAL QUALITY CRITERIA - For remaining findings, assess:
1. ...

PRECEDENTS -
1. ...
```

**Slash command finding output format (markdown):**
```
# Vuln N: Category: file.py:line
* Severity: HIGH|MEDIUM|LOW
* Description: ...
* Exploit Scenario: ...
* Recommendation: ...
```

**Slash command allowed tools:** `Bash(git diff:*)`, `Bash(git status:*)`, `Bash(git log:*)`, `Bash(git show:*)`, `Bash(git remote show:*)`, `Read`, `Glob`, `Grep`, `LS`, `Task`

---

## Dimension 3 — Interactions (contract level)

**prompts.py → github_action_audit.py:** `get_security_audit_prompt(pr_data, pr_diff, include_diff=True, custom_scan_instructions=None)` returns a string prompt. `custom_scan_instructions` appended after "Data Exposure" category. If `include_diff=False`, diff section replaced with instruction to use file exploration tools.

**github_action_audit.py → claude CLI:** stdin=prompt string, captures stdout JSON. Double-parse: outer JSON wrapper (`{type, subtype, is_error, result}`) → `.result` is a string → parse that string for `{findings: [...], analysis_summary: {...}}`. If `.result == "Prompt is too long"`: trigger PROMPT_TOO_LONG retry without diff.

**claude_api_client.py → findings_filter.py:** `analyze_single_finding(finding, pr_context, custom_instructions)` → `{confidence_score: int(1-10), keep_finding: bool, exclusion_reason: str|null, justification: str}`. If `keep_finding: true`: finding passed through with `_filter_metadata: {confidence_score, justification}` added. If API fails: finding kept with `confidence_score: 10.0`, `justification: "Claude API failed: <error>"`.

**action.yml → github_action_audit.py (cache/dedup contract):** Before scan, checks for `.claudecode-marker/marker.json`. Key: `claudecode-<repo_id>-pr-<pr_num>-<sha>`. Restore-key: `claudecode-<repo_id>-pr-<pr_num>-`. If marker exists and `run-every-commit != true`: skip scan entirely. Prevents double-scanning when both push and PR events fire. Race condition prevention: marker is reserved before cache saved.

**Generated file filter contract:** Diff sections matching `@generated by`, `@generated`, `Code generated by OpenAPI Generator`, `Code generated by protoc-gen-go` are stripped before the prompt is built.

---

## Reference Type and Maturity

- **Type:** Production GitHub Action + Claude Code slash command — a deployed, official Anthropic tool
- **Maturity signals:** Active test suite (10+ files), pytest.ini, CI workflow, pinned action hashes (commit SHA), official Anthropic authorship, production usage
- **Red flags:** Model names hardcoded (`constants.py` line 8, `claude_api_client.py` line 68) — direct I6 violations. Duplicate item #16 in slash command exclusion list (copy-paste artifact).

---

## Section 1 — Reference Summary

**What type and what problem it solves:**  
Production GitHub Action + slash command skill for AI-powered security review of PRs. Solves the false-positive noise problem of SAST tools by adding: (1) semantic understanding of vulnerability context, (2) a curated two-stage filter pipeline (hard rules + per-finding AI analysis), and (3) language/framework-specific exemption rules.

**Behavioral content:**  
Multi-stage filter pipeline with 7-category regex taxonomy; 3-phase review methodology (context → comparative → assessment); parallel sub-task false positive filtering; 17-item hard exclusion list with language-specific precision (Rust, React, Angular, ipynb, shell scripts, client-side JS); 12-item precedents list for framework-specific allowances; confidence scoring with explicit 0.7 cutoff; PROMPT_TOO_LONG fallback; generated file filtering; PR cache deduplication.

**Structural content:**  
Clean module decomposition (prompts / filter / runner / client / parser). Finding schema with `exploit_scenario` as a required field. 3-section custom filtering override format (HARD EXCLUSIONS / SIGNAL QUALITY CRITERIA / PRECEDENTS). FilterStats dataclass for audit trail of what was filtered and why.

**Interaction content:**  
Double-parse architecture (CLI output → wrapper JSON → result string → findings JSON). Environment variable contract (8 env vars) between CI and audit script. Fail-open design: if API filter fails, keep finding with confidence=10.0.

**Maturity:** Core filtering logic and test suite are mature. GitHub Actions coupling is stable but not portable to WabbleSpec. Slash command format is immediately usable.

---

## Section 2 — Benefits We Can Get

| Location | What to adapt | Why it helps | How to adapt | Impact |
|---|---|---|---|---|
| security-review.md lines 139-169 | 17-item hard exclusion list with language/framework precision | Production-hardened false-positive rules — covers Rust/React/Angular/ipynb/shell script exceptions that our gateway-security has no equivalent for | Add as `## Hard Exclusion Rules` section in `gateway-security/SKILL.md` | High |
| security-review.md lines 157-169 | 12-item precedents list | Framework-specific allowances (env vars trusted, UUIDs unguessable, client-side auth not required) prevent over-reporting in security audits | Add as `## Precedents` section in `gateway-security/SKILL.md` | High |
| security-review.md lines 185-189 | Parallel sub-task false-positive filter pattern | One identifying sub-task + N parallel per-finding filter sub-tasks eliminates the serial review bottleneck for multi-finding audits | Add as a dispatch pattern in `adversary/SKILL.md` for multi-finding security mode | Medium |
| security-review.md lines 124-130 | Confidence scoring: 0.7 cutoff / 0.8-0.9 / 0.9-1.0 tiers with exact meanings | Explicit numeric thresholds prevent "too speculative" findings from surfacing; 0.7 is a named non-report boundary | Add tiered confidence table to `adversary/SKILL.md` Claim Confidence Protocol (currently has < 0.7 trigger for invoking adversary, but no tiered scoring for findings themselves) | Medium |
| prompts.py lines 128-149 | `exploit_scenario` as required finding field in JSON schema | Forces the reviewer to prove exploitability (attack path required), not just assert vulnerability existence — eliminates unfalsifiable claims | Add `exploit_scenario` to `adversary/SKILL.md` counter_analysis output schema | Medium |
| docs/custom-filtering-instructions.md | 3-section override format (HARD EXCLUSIONS / SIGNAL QUALITY CRITERIA / PRECEDENTS) | Generalizes beyond security to any finding classification — provides a structured vocabulary for overriding defaults in any module that produces findings | Add as a reference doc pattern for gateway-security and future audit tools | Low |
| findings_filter.py lines 31-75 | Pre-compiled regex category taxonomy (7 categories named) | The category names and pattern groups are the transferable vocabulary, even without the Python code — usable as filter vocabulary in Guard skill-rules.json | Study: adopt the 7-category names into security false-positive reference doc | Low |

---

## Section 3 — Negative Effects / Risks

| Location | Risk | Why it hurts | Mitigation | Severity |
|---|---|---|---|---|
| constants.py line 8, claude_api_client.py line 68 | Model names hardcoded: `claude-opus-4-1-20250805`, `claude-3-5-haiku-20241022` | Direct I6 violation — names in framework files are banned | Do not copy these constants; use capability descriptors | Critical |
| security-review.md lines 154-155 | Duplicate item #16 (two entries numbered 16) | Shows the list was assembled without final review — there may be internal contradictions | Audit each rule independently before adopting | Low |
| action.yml + github_action_audit.py + scripts/comment-pr-findings.js | GitHub Actions CI bundle architecture | Not portable to WabbleSpec hook/skill model; prompt injection explicitly not hardened (README line 44) | Do not adopt the CI bundle; adopt behavioral content only | Medium |
| claude_api_client.py lines 263-306 | Per-finding API calls (N calls for N findings) | For a 20-finding result set: 20 API calls; operational cost too high for WabbleSpec integration | Adopt the filtering vocabulary (what to filter), not the per-call architecture | Low |

---

## Section 4 — Adapt vs Avoid

| Reference Part | Adapt / Avoid / Study Only | Reason | Target Area | Priority |
|---|---|---|---|---|
| 17-item hard exclusion list (security-review.md lines 139-169) | Adapt | Production-hardened; no equivalent in gateway-security | `.claude/skills/gateway-security/SKILL.md` | High |
| 12-item precedents list (security-review.md lines 157-169) | Adapt | Framework-specific allowances missing from WabbleSpec | `.claude/skills/gateway-security/SKILL.md` | High |
| `exploit_scenario` field in finding schema (prompts.py lines 128-149) | Adapt | Required field proving attack path — additive to adversary output | `.claude/skills/adversary/SKILL.md` | Medium |
| Parallel sub-task filter pattern (security-review.md lines 185-189) | Adapt | One identify + N parallel filter — reduces false positives in multi-finding security audits | `.claude/skills/adversary/SKILL.md` | Medium |
| Confidence tiers 0.7/0.8-0.9/0.9-1.0 with meanings (security-review.md lines 124-130) | Adapt | Adds numeric precision to existing < 0.7 trigger in adversary | `.claude/skills/adversary/SKILL.md` | Medium |
| 3-phase methodology (security-review.md lines 89-102) | Adapt | Context → Comparative → Assessment — missing from gateway-security activation sequence | `.claude/skills/gateway-security/SKILL.md` | Medium |
| 3-section filtering override format (docs/custom-filtering-instructions.md) | Study Only | Format is transferable; actual implementation needs to be WabbleSpec-native | gateway-security references/ | Low |
| HardExclusionRules regex patterns (findings_filter.py lines 31-75) | Study Only | Python code is not portable; adopt the 7-category taxonomy names only | Gateway-security reference doc | Low |
| constants.py model names | Avoid | I6 violation | Anywhere | Critical |
| GitHub Actions CI bundle (action.yml, github_action_audit.py, scripts/) | Avoid | Not portable; prompt injection not hardened | — | High |
| Per-finding Claude API call architecture | Avoid | N API calls per scan — excessive for integration | — | Medium |

---

## Section 5 — Integration Fit

| Dimension | Score (1–10) | Explanation |
|---|---|---|
| Concept fit | 8 | Security review of diffs/commits maps directly to adversary/guard threat model and gateway-security's SAST concern |
| Architecture fit | 4 | GitHub Actions CI bundle is not portable; slash command format and behavioral content are directly portable |
| Implementation fit | 7 | Slash command is directly adaptable (format: `.claude/commands/`); filtering rules are additive to existing skills |
| Maintenance fit | 7 | Hard exclusion rules and precedents are stable; language/framework-specific rules evolve slowly |
| Risk level | 3 | (10 = very risky) Only risk is I6 from model constants — easily avoided by not importing constants.py |
| Overall usefulness | 7 | Immediately useful for gateway-security and adversary; CI bundle is not |

**Overall usefulness 7 — worth active use.**

---

## Section 6 — Recommended Extraction Plan

**Phase 1 (Safe Learning — implement now):**
- [P1-A] Add 17-item hard exclusion list + 12-item precedents list to `gateway-security/SKILL.md` (security-review.md lines 139-169)
- [P1-B] Add `exploit_scenario` to adversary's counter_analysis output schema (prompts.py lines 128-149)
- [P1-C] Add confidence tiers (0.7/0.8-0.9/0.9-1.0 table) to adversary's Claim Confidence Protocol (security-review.md lines 124-130)

**Phase 2 (Low-Risk Adaptation — implement now):**
- [P2-A] Add 3-phase security review methodology to gateway-security Phase B activation sequence (security-review.md lines 89-102)
- [P2-B] Add parallel sub-task filter dispatch pattern to adversary SKILL.md (security-review.md lines 185-189)

**Phase 3 (Deeper Integration — deferred):**
- Write a `security-false-positive-taxonomy.md` reference doc encoding the 7-category HardExclusionRules taxonomy in framework-neutral form; wire into gateway-security references/ directory

**Phase 4 (Do Not Cross):**
- constants.py model names (I6)
- GitHub Actions CI bundle (not portable, not hardened)
- Per-finding API call architecture (operational cost)

---

## Section 7 — Final Verdict

**Classification: supporting-reference (7/10)**

**Best 3 to steal:**
1. 17-item hard exclusion list with language/framework precision — `security-review.md` lines 139-169 — this is production-hardened false-positive filtering vocabulary that WabbleSpec has no equivalent for
2. Parallel sub-task false-positive filter pattern (one identify + N parallel filter) — `security-review.md` lines 185-189 — eliminates serial review bottleneck for multi-finding audits
3. `exploit_scenario` as required finding field — `prompts.py` lines 128-149 — proves exploitability rather than asserting it

**Worst 3 to avoid:**
1. `constants.py` line 8: `DEFAULT_CLAUDE_MODEL = 'claude-opus-4-1-20250805'` — I6 violation
2. GitHub Actions CI bundle — not portable, prompt injection not hardened (README line 44)
3. Per-finding Claude API calls — N calls for N findings, excessive operational cost

**Recommended next action:** Implement Phase 1-2 items (all additive, no breaking changes). Phase 1 closes a real gap: gateway-security currently has no false-positive filtering vocabulary; adversary's finding schema has no exploit_scenario requirement.

---

## Section 8 — Project Synthesis

**Synthesis 1: Confidence-gated adversarial escalation in multi-finding security audits**
- What: When gateway-security identifies multiple SAST findings, apply the 0.7/0.8/0.9 confidence tiers at the dispatch point: < 0.7 findings never enter adversary, 0.7-0.8 get one-pass adversarial check, 0.9+ get full DREAD scoring
- Reference contribution: 0.7 cutoff / 0.8-0.9 / 0.9-1.0 tiered confidence scoring with named meanings
- Project contribution: Adversary's existing DREAD scoring and dual-perspective requirement — combining gives a graduated escalation path
- Target: `.claude/skills/adversary/SKILL.md` — add a `## Security Audit Mode` section that dispatches based on confidence tier
- Gap closed: Currently adversary does not distinguish between findings that are certain exploits and findings that are speculative — all get full DREAD treatment regardless of evidence quality

**Synthesis 2: Guard OPSEC noise taxonomy × security false-positive precedents**
- What: Guard's QUIET/MODERATE/LOUD OPSEC noise taxonomy (from pentest reference) cross-indexed with the 12 precedents from this reference creates a dual-axis filter: OPSEC noise level AND false-positive category, both checked before a Guard block fires
- Reference contribution: 12 precedents (env vars trusted, UUIDs unguessable, client-side auth not required, ipynb low-risk)
- Project contribution: Guard's existing OPSEC noise taxonomy from pentest reference
- Target: `.claude/skills/guard/skill-rules.json` — add a `security_precedents` array that Guard checks before classifying a tool call as LOUD
- Gap closed: Guard currently has no framework for dismissing low-signal security signals that look dangerous but are actually safe (e.g., an env var read that looks like secret exposure)

**Synthesis 3: Wave-review false-positive filter using the 7-category HardExclusionRules taxonomy**
- What: Wave-review currently applies 4 Dream anti-pattern filters. Adding a secondary pass using the 7-category taxonomy (DOS/rate-limit/resource/redirect/memory-safety/regex-injection/SSRF) would filter wave-level findings that match known false-positive patterns before they surface as instinct observations
- Reference contribution: 7-category pre-compiled regex taxonomy from `findings_filter.py` lines 31-75
- Project contribution: Wave-review's Dream anti-pattern filters and instinct observation gating
- Target: `.wabblespec/engine/modules/l6/wave-review/SKILL.md` — add `## False-Positive Pre-Filter` subsection with the 7 category names (not the regexes) as named exclusion groups
- Gap closed: Wave-review currently has no vocabulary for "this looks like a finding but is actually a known low-signal category" — it applies Dream filters but has no per-finding exclusion taxonomy

---

## Section 9 — Expansion Opportunities

**Per-skill growth scan:**

| Reference Capability | Project Equivalent? | Tier 7 Candidate |
|---|---|---|
| Hard exclusion rule engine (regex-based) | No equivalent script; rules are in SKILL.md prose | No (Tier 3 — new reference doc, not new module) |
| Per-finding confidence scoring | Adversary has DREAD (impact-based), not confidence-based scoring | No (Tier 1 — additive to adversary) |
| 3-phase review methodology | Not formalized in gateway-security | No (Tier 1 — additive) |
| Parallel sub-task filter dispatch | Adversary dispatches single adversarial review | No (Tier 1 — additive) |
| PR eval harness (eval_engine.py) — git worktree checkout of real PRs, concurrent evaluation, EvalResult dataclass | No equivalent anywhere in WabbleSpec | **Yes (Tier 7)** |
| Custom filtering instruction format (3-section override) | No structured override format for per-project security customization | No (Tier 3 — new reference doc) |
| PR deduplication cache (marker file + cache key pattern) | No CI integration | No (I11 — product-space, out of scope) |

**Expansion Opportunity:**

| Capability | Reference location | Why project lacks it | What it unlocks | Dependencies | Effort | Tier 7 |
|---|---|---|---|---|---|---|
| PR security eval harness — run gateway-security or adversary against real GitHub PRs via git worktree checkout with concurrent evaluation, EvalResult tracking, and JSON output | `claudecode/evals/eval_engine.py` lines 56-465, `evals/run_eval.py` | WabbleSpec has skill-tdd (behavioral harness) and benchmark-loop (quality metric loop) but no PR-specific security eval that checks out real code from GitHub | Enables regression testing of gateway-security rule changes against real PR history; validates that hard exclusion rule additions don't introduce false negatives | GitHub CLI (`gh`), git worktree support, ANTHROPIC_API_KEY, GITHUB_TOKEN | weeks | Yes |

**Gateway bundling signal:** Only one Tier 7 item identified — no bundling needed.

---

## Memory Drawers Written

- `wings/references/rooms/claude-code-security-review-main/` — 3 drawers:
  - `security-hard-exclusion-rules.json` — 17-item list + 7-category taxonomy
  - `security-precedents.json` — 12-item framework-specific allowances
  - `exploit-scenario-field.json` — finding schema + parallel sub-task pattern
