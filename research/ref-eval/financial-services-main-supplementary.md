# Ref-Eval: financial-services-main (Supplementary Pass)

**Date:** 2026-05-31
**Slug:** financial-services-main-supplementary
**Basis:** Prior ref-eval (2026-05-31) was FRESH; this pass completes the per-file inventory for files that were directory-level skipped in the original run.

---

## Newly Inventoried Files (not in original pass)

| File | Status | Key Contents | Transfer check |
|---|---|---|---|
| `earnings-analysis/references/best-practices.md` | Read | Quality checklist (content/format/citations/accuracy/timeliness/style); delivery summary format; headline examples (good/bad) | Yes — checklist structure |
| `earnings-analysis/references/workflow.md` | Read | 4-step staleness verification protocol; 90-day cutoff; 16-step workflow with date-verification gates; fiscal calendar patterns | Yes — date-verification discipline |
| `earnings-analysis/references/report-structure.md` | Read | Page-by-page DOCX templates; thesis pillar impact states (STRENGTHENED/UNCHANGED/WEAKENED); Old→New→Change→Reason estimate table format | Yes — thesis impact vocabulary |
| `gl-recon/SKILL.md` | Read | Full-outer-join matching; 6 break buckets (Matched/Amount/Quantity/Timing/GL-only/Sub-only); cause taxonomy (Timing/FX/Mapping/Duplicate/Fee/Data quality) | Partial — cause taxonomy format |
| `break-trace/SKILL.md` | Read | Root-cause sentence format ("side did what because reason"); JSON with owner + expected_clear_date + action enum (monitor/adjust/raise-ticket/suppress) | Yes — attribution format |
| `kyc-screener/agents/kyc-screener.md` | Read | "This agent recommends; the compliance officer decides" — delegation boundary; Read-only orchestrator pattern reinforced | Reinforces prior T1-1 |
| `xlsx-author/SKILL.md` | Read | Blue/black/green convention; named ranges; balance checks (Checks tab, TRUE/FALSE); one model per file | Yes — named ranges + Checks tab (new to our xlsx.md) |
| `morning-note/SKILL.md` | Read | "Be opinionated — notes that just summarize without a view are useless"; "No news is valid"; lead with most important thing | Partial — already covered by CLAUDE.md concision rules |
| `earnings-preview/SKILL.md` | Read | Bull/Base/Bear scenario table; options-implied move as calibration; "what to watch" per sector | Low — domain-specific |
| `model-update/SKILL.md` | Read | Old/New/Change/Reason table format; GAAP vs adjusted distinction; estimate revision history | Low — domain-specific |

---

## New Transferable Items Found

| Item | Reference location | Gap in current project |
|---|---|---|
| Thesis pillar impact vocabulary (STRENGTHENED/UNCHANGED/WEAKENED) | `report-structure.md` Pages 6-7 | Verifier has PASS/FAIL/BLOCKED but no directional thesis signal |
| Named ranges for cross-sheet references | `xlsx-author/SKILL.md` | `gateway-document/references/xlsx.md` has color coding but no named range guidance |
| Balance Checks Tab (TRUE/FALSE per invariant, last tab, blocks delivery) | `xlsx-author/SKILL.md` | `gateway-document/references/xlsx.md` has formula errors gate but no structured Checks tab pattern |

---

## Items Confirmed Not Transferable

| Item | Reason |
|---|---|
| 90-day staleness check wording | WabbleSpec staleness is automated via EMA decay; the agent-instruction phrasing is for human-facing prompts, not framework rules |
| Root-cause attribution format | analyze SKILL.md already has RCA methods + `root_cause_summary` field; adding the sentence form would be additive but low-impact |
| Opinionated communication principle | Already covered by global CLAUDE.md: "concise in output", "do not pad" |
| Bull/Base/Bear scenarios | Domain-specific; no applicable WabbleSpec context |
| Break classification taxonomy | Financial domain; not applicable |

---

## Sections 8-9 Supplement

**Section 8 (Synthesis) — No new synthesis items.** The items found are additive to existing modules, not novel combinations.

**Section 9 (Expansion) — No new Tier 7 items.** The xlsx-author pattern is an additive Tier 1 (existing reference file), not a net-new capability.

---

## Cookbook Pass — managed-agent-cookbooks/ (all 10 agents)

Files read: `pitch-agent/README.md`, `market-researcher/README.md`, `meeting-prep-agent/README.md`, `model-builder/README.md`, `valuation-reviewer/README.md`, `month-end-closer/README.md`, `statement-auditor/README.md`, `earnings-reviewer/README.md`, `earnings-reviewer/steering-examples.json`, `model-builder/steering-examples.json`, `model-builder/subagents/auditor.yaml`, `pitch-agent/subagents/modeler.yaml`.

### Patterns extracted

**P1 — Subagent role taxonomy** (`model-builder/README.md`, `pitch-agent/README.md`, all READMEs)

Four distinct roles appear consistently across all 10 agents:
1. **Reader** — untrusted-doc processor; Read+Grep only, no MCP; returns schema-validated JSON
2. **Computation worker** — trusted-source fetcher + calculation; Read+Bash (sandboxed); returns JSON, never writes artifact (`pitch-modeler.yaml`: "You do not write the final workbook — the deck-writer does")
3. **Write-holder** — sole artifact producer; Read+Write+Edit; consumes reader/computation JSON
4. **Post-write auditor** — independent re-check after write; Read+Grep only; re-checks the completed artifact (`model-builder`: `builder` writes → `auditor` re-checks ties and balances)

The pre-write critic (gl-reconciler) and post-write auditor (model-builder) are distinct patterns: critic fires before the Write-holder acts; auditor fires after.

**P2 — "Not guaranteed" delegation boundary declaration** (kyc-screener, valuation-reviewer, statement-auditor, meeting-prep-agent, month-end-closer READMEs)

Every recommendation-producing agent explicitly states what it does NOT do. Examples:
- `kyc-screener`: "this agent recommends; the compliance officer decides"
- `valuation-reviewer`: "LP reports require IR and CCO sign-off outside this agent"
- `statement-auditor`: "this agent recommends pass/hold; IR distributes after human sign-off"
- `month-end-closer`: "JE drafts are staged, not posted to the GL"

**P3 — Steering event skip and assumption-injection variants** (`earnings-reviewer/steering-examples.json`, `model-builder/steering-examples.json`)

- Skip variant: `"Update model only: NVDA Q1-FY27, skip note"` — partial execution path declared at initiation
- Assumption injection: `"Build dcf for MSFT, assumptions: {wacc: 0.085, tgr: 0.025, horizon: 5}"` — key parameters passed as structured fields in the steering event

**P4 — Cross-agent handoff dependency graph** (all READMEs)

Explicit directed handoff chains documented per agent: earnings-reviewer → model-builder, pitch-agent → model-builder, market-researcher → model-builder, valuation-reviewer → gl-reconciler, gl-reconciler → month-end-closer. The `orchestrate.py` hard-allowlist enforces this graph at the infrastructure level.

### Implementation disposition

| Pattern | Status | Target |
|---|---|---|
| P1 Subagent role taxonomy | Implemented | `.claude/skills/executor/SKILL.md` + engine module |
| P2 "Not guaranteed" boundary | Implemented | `CLAUDE.md` + adversary + guard + engine modules |
| P3 Steering event variants | Watch-only | WabbleSpec recipe/scope system handles parameterization differently; adopt if CMA steering events become relevant |
| P4 Handoff dependency graph | Watch-only | autopilot allowlist already enforces; explicit graph is documentation, not new logic |
