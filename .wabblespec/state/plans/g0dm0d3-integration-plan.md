# G0DM0D3 Integration Plan
**Status:** PLANNED | **Target:** 0.8.x | **Base version:** 0.7.7
**Created:** 2026-05-25 | **Source reference:** `C:\Users\Kirsten\Downloads\Test\G0DM0D3-main`

---

## What This Plan Does

Extracts and adapts four algorithms from G0DM0D3 as Python scripts in `_shared/scripts/`.
Integrates those scripts into five WabbleSpec module augments and one new module.
All code is independent Python implementation from the G0DM0D3 paper (PAPER.md Sections 3.2–3.5).
No TypeScript copied. License: AGPL-3.0 contamination avoided by design.

**Core decision:** Wave 0 produces working Python scripts, not pseudocode MD.
The scripts ARE the reference documentation. Each script has a header citing the paper section.

---

## Six Deliverables

| # | Deliverable | Type | Source algorithm | WabbleSpec target |
|---|---|---|---|---|
| 1 | InferenceGuard | NEW module L2 | Parseltongue (PAPER §3.4) | Executor pipeline, gateway-security |
| 2 | ContextTuner | AUGMENT model-router | AutoTune (PAPER §3.2) | model-router |
| 3 | STM Pipeline | AUGMENT Polish + Clean | STM modules (PAPER §3.5) | Polish, Clean |
| 4 | Red/Blue integration | AUGMENT gateway-security | ULTRAPLINIAN scoring methodology | red-protocol, blue-protocol, cycle-protocol |
| 5 | ParamLearner | AUGMENT Feedback | EMA feedback loop (PAPER §3.3) | L8 Feedback |
| 6 | Benchmark axis decomposition | AUGMENT Benchmark | Scoring decomposition methodology | L8 Benchmark |

---

## Wave 0 — Python Scripts (no module changes)

**Deliverables — all in `_shared/scripts/`:**

```
_shared/scripts/inference-guard.py     # Parseltongue algorithm: trigger detection + obfuscation
_shared/scripts/context-tuner.py       # AutoTune algorithm: context classification + parameter selection
_shared/scripts/stm-pipeline.py        # STM algorithm: sequential pure-function text transforms
_shared/scripts/param-learner.py       # EMA algorithm: parameter learning from receipt signals
```

**Validation:** Each script runs standalone with `--help`. Each script has a `--test` flag that exercises its own logic against built-in fixture cases. All four pass before any Wave 1+ work begins.

---

## Wave 1 — InferenceGuard New Module
**Processing path:** Specify → Executor → Apply → Verify → Archive
**Version target:** 0.8.0

### Purpose
Prevents false refusals when agents perform legitimate security-domain tasks (Red team simulation, CVE reproduction, vulnerability analysis). Activates only when gateway-security is active or task_type is security-typed. Never fires on general code/spec/planning tasks.

### Module location
```
modules/l2/inference-guard/
  SKILL.md
  skill-rules.json
  rules/
    cold-start.md
    activation-policy.md        # gateway conditions, suppression flag
    trigger-vocabulary.md       # 3-tier SDLC trigger word lists
  tests/acceptance.md
  schemas/receipt.schema.json
```

The actual algorithm lives in `_shared/scripts/inference-guard.py` (Wave 0).
The module shell calls the script. Module does not reimplement.

### Activation conditions (ALL required)
1. Active gateway is `gateway-security` OR task_type in: `security`, `pentest`, `red-team`, `vulnerability-analysis`, `threat-model`, `security-audit`
2. At least one trigger detected in inference input
3. Task card does not contain `inference_guard: false`

### Trigger tiers
**Tier 1 (light — always checked when active):**
`hack`, `exploit`, `bypass`, `crack`, `attack`, `penetrate`, `inject`, `override`, `disable`, `circumvent`, `evade`, `manipulate`

**Tier 2 (standard — adds to Tier 1):**
`malware`, `virus`, `trojan`, `payload`, `shellcode`, `rootkit`, `keylogger`, `backdoor`, `vulnerability`, `CVE`, `XSS`, `CSRF`, `SSRF`, `IDOR`, `RCE`, `LFI`, `SQLi`, `buffer overflow`, `privilege escalation`, `authentication bypass`, `directory traversal`

**Tier 3 (heavy — explicit opt-in only via task card flag `inference_guard_tier: heavy`):**
`weapon`, `explosive`, `poison`, `synthesize`, `phishing`, `impersonate`, `deceive`, `fraud`

**Excluded (not SDLC vocabulary):**
`nsfw`, `explicit`, `uncensored`, `unfiltered`, `unrestricted`, `jailbreak`, `ignore`, `disregard`, `forget`, `pretend`, `roleplay`, `act as`, `you are now`, `new identity`

**Default tier:** `standard` for Red protocol, `light` for general security tasks

### Receipt format
```json
{
  "module": "inference-guard",
  "activated": true,
  "gateway_condition": "gateway-security",
  "task_type": "red-team",
  "tier_applied": "standard",
  "technique": "leetspeak",
  "intensity": "medium",
  "triggers_detected": ["exploit", "payload"],
  "trigger_count": 2,
  "transformations": [
    { "original": "exploit", "transformed": "3xpl0it" },
    { "original": "payload", "transformed": "p4yl04d" }
  ],
  "input_length_before": 245,
  "input_length_after": 248,
  "timestamp": "ISO-8601"
}
```

Non-activation receipt: `{"module": "inference-guard", "activated": false, "reason": "gateway_inactive|no_triggers|suppressed"}`

### Files created
- `modules/l2/inference-guard/SKILL.md`
- `modules/l2/inference-guard/skill-rules.json`
- `modules/l2/inference-guard/rules/cold-start.md`
- `modules/l2/inference-guard/rules/activation-policy.md`
- `modules/l2/inference-guard/rules/trigger-vocabulary.md`
- `modules/l2/inference-guard/tests/acceptance.md`
- `modules/l2/inference-guard/schemas/receipt.schema.json`

### Files modified
- `framework.yaml` — register `inference-guard`, layer L2, tier core, receipt_required: true
- `modules/l2/model-router/SKILL.md` — add `inference_guard_eligible` to output contract
- `modules/l4/security/references/cycling/red-protocol.md` — note InferenceGuard activation in Red phase
- `modules/l4/security/references/cycling/blue-protocol.md` — note InferenceGuard suppression + `inference_guard: false`

### Acceptance criteria
1. Fires on Red task card containing "exploit SQL injection" — receipt shows triggers + transformations
2. Does NOT fire on code-generation task with "implement a delete function" — receipt shows `activated: false, reason: gateway_inactive`
3. Does NOT fire when task card includes `inference_guard: false`
4. Receipt written on EVERY execution, activation or not (I10)
5. No model names in any output (I6)
6. `validate-graph.py` passes after framework.yaml registration

---

## Wave 2 — ContextTuner (model-router AUGMENT)
**Processing path:** Synth → Blueprint → Augment → Benchmark → Forge
**Version target:** 0.8.1

### Purpose
Adds pre-generation context classification to model-router. Classifies task input into one of six WabbleSpec task types and selects optimized sampling parameters. Zero extra inference calls. Parameters appear in routing receipt and flow to the capability call.

### Six WabbleSpec context types

| Type | temp | top_p | top_k | freq | pres | rep |
|---|---|---|---|---|---|---|
| `spec-authoring` | 0.30 | 0.85 | 30 | 0.20 | 0.10 | 1.05 |
| `code-generation` | 0.20 | 0.80 | 25 | 0.20 | 0.00 | 1.05 |
| `security-review` | 0.50 | 0.90 | 50 | 0.20 | 0.20 | 1.08 |
| `planning` | 0.60 | 0.90 | 50 | 0.15 | 0.15 | 1.05 |
| `synthesis` | 0.80 | 0.92 | 60 | 0.30 | 0.30 | 1.10 |
| `administrative` | 0.20 | 0.85 | 25 | 0.10 | 0.00 | 1.05 |

No chaotic type. G0DM0D3's chaotic type has 66.7% precision and systematically misclassifies code tasks containing words like "delete" or "break".

### Detection patterns (WabbleSpec vocabulary)
Scoring: current message 3x, last 4 history messages 1x each.
Confidence = winner_score / total_score. If confidence < 0.6: blend with `planning` baseline.

- **spec-authoring:** `WHEN|THEN|SHALL|SHOULD|MUST|acceptance criteria|EARS|requirement|specification`
- **code-generation:** code blocks (``` backticks), `function|class|method|implement|refactor|def |const |import `
- **security-review:** `vulnerability|CVE|threat|attack surface|pentest|red team|exploit|OWASP|injection|XSS`
- **planning:** `wave plan|task card|decompose|architecture|dependency|phase|milestone|rollback|checkpoint`
- **synthesis:** `summarize|generate|changelog|document|report|draft|compile|aggregate|from.*receipts`
- **administrative:** `version|bump|archive|receipt|CHANGELOG|INDEX|framework.yaml|seed run|witness`

### New model-router receipt fields
```json
{
  "context_classification": {
    "detected_type": "code-generation",
    "confidence": 0.82,
    "context_scores": [
      { "type": "code-generation", "score": 12, "pct": 0.82 },
      { "type": "planning", "score": 2, "pct": 0.14 }
    ],
    "pattern_matches": ["code_block_detected", "implement_keyword"],
    "parameters_selected": { "temperature": 0.20, "top_p": 0.80, "top_k": 25 },
    "blended": false
  }
}
```

### Benchmark gate
- **Fixture set:** 90 labeled task inputs (15 per type), stratified: 10 clear / 4 medium / 1 hard
- **Threshold:** >= 80% accuracy on held-out set (AUGMENT parity gate)
- **Control arm:** flat keyword scoring without 3x message weighting
- **Script:** `_shared/scripts/context-tuner.py --test` runs the fixture eval

### Files created
- `modules/l2/model-router/scripts/context-tuner-eval.py` (fixture runner, imports `_shared/scripts/context-tuner.py`)
- `modules/l2/model-router/fixtures/` (90 labeled inputs + `split.json`)

### Files modified
- `modules/l2/model-router/SKILL.md` — add ContextTuner section, update output contract
- `modules/l2/model-router/rules/task-shapes.md` — replace with 6-type context taxonomy

---

## Wave 3 — STM Pipeline (Polish + Clean AUGMENT)
**Processing path:** Synth → Blueprint → Augment → Benchmark → Forge
**Version target:** 0.8.2

### Purpose
Implements the sequential pure-function transform pipeline pattern from G0DM0D3 in Polish and Clean modules. Each transform is independently togglable and version-stamped. Applications are logged in receipts.

### Five transforms

| Module | Type | Patterns | Purpose |
|---|---|---|---|
| `hedge_reducer` | Port from G0DM0D3 | 11 regex | Remove "I think", "perhaps", "maybe" etc. |
| `direct_mode` | Port from G0DM0D3 | 10 regex | Remove "Sure,", "Of course," preambles |
| `spec_mode` | WabbleSpec-specific | 5 rules | Normalize modals: "might" → "SHOULD", "will" → "SHALL" |
| `receipt_mode` | WabbleSpec-specific | 8 rules | Strip first-person from receipts, capitalize PASS/FAIL/WARN |
| `casual_mode` | Port from G0DM0D3 | 22 subs | "However"→"But", "Utilize"→"Use" (off by default) |

### STM receipt field
```json
{
  "stm_applied": ["hedge_reducer", "direct_mode"],
  "char_count_before": 1420,
  "char_count_after": 1389,
  "reduction_pct": 2.2
}
```

### Polish default config: `["hedge_reducer", "direct_mode"]`
### Clean default config: `["receipt_mode", "direct_mode"]`

### Benchmark gate
- **Fixture set:** 77 cases (26 hedge_reducer, 21 direct_mode, 30 spec_mode + receipt_mode)
- **Threshold:** 100% precision and recall (deterministic regex modules)
- **Negative cases required:** 30 cases that must NOT be transformed

### Files created
- `_shared/scripts/stm-pipeline.py` (Wave 0 — already written)
- `modules/l6/polish/rules/stm-config.json`
- `modules/l1/clean/rules/stm-config.json`
- `modules/l6/polish/fixtures/` (77 STM test cases + split.json)

### Files modified
- `modules/l6/polish/SKILL.md` — add STM pipeline section
- `modules/l1/clean/SKILL.md` — add STM receipt_mode integration

---

## Wave 4 — Red/Blue/Purple Integration (gateway-security AUGMENT)
**Processing path:** Synth → Blueprint → Augment → Benchmark → Forge
**Version target:** 0.8.3

### Purpose
Wire InferenceGuard (Wave 1) and STM (Wave 3) explicitly into the Red/Blue cycling protocols. Add inference quality as a 9th Purple scoring component.

### Red protocol changes
1. Add pre-step: confirm InferenceGuard is active before Red phase begins
2. Add inference_refusal tracking: if PoC generation is refused/truncated, flag `inference_refusal: true` in finding
3. ContextTuner profile for Red tasks: `security-review` (temperature=0.50)
4. New Red receipt field: `inference_guard_summary` with activation count + trigger tier breakdown

### Blue protocol changes
1. Apply `hedge_reducer` + `direct_mode` STM transforms to all defense findings before receipt write
2. ContextTuner profile: `security-review` for analysis, `code-generation` for implementation
3. Required task card flag: `inference_guard: false` (Blue works with explicit vulnerability names)

### Purple scoring — 9th component
```
Component: Inference quality (5% weight)
Score 10: Zero inference_refusal flags in Red findings
Score 5–9: 1–3 inference_refusal flags; findings mostly complete
Score 0–4: 4+ inference_refusal flags; Red findings likely incomplete
```

Existing 8 components retain their logic; weights reduced ~0.5% each to accommodate the new 5%.

### New security profile fields
```yaml
inference_guard_tier: light|standard|heavy    # default: standard
inference_guard_technique: leetspeak|unicode|mixedcase|random  # default: leetspeak
```

### Files modified
- `modules/l4/security/references/cycling/red-protocol.md`
- `modules/l4/security/references/cycling/blue-protocol.md`
- `modules/l4/security/references/cycling/cycle-protocol.md` — 9th scoring component
- `modules/l4/security/references/cycling/security-profile.md` — inference_guard fields
- `modules/l4/security/SKILL.md` — reference InferenceGuard

---

## Wave 5 — ParamLearner (Feedback AUGMENT)
**Processing path:** Synth → Blueprint → Augment → Benchmark → Forge
**Version target:** 0.9.0
**Gate:** Requires 50+ curated receipt corpus (mempalace Phase 5 gate)

### Purpose
Extends Feedback module with EMA-based parameter adaptation. Receipt pass/fail is the learning signal. Learned profiles adjust ContextTuner parameter selections over time. Profiles persist in `.wabblespec/memory/learned-params/`.

### EMA constants (from G0DM0D3 paper, validated)
```
EMA_ALPHA = 0.3           # converges within ~19 signals
MIN_SAMPLES = 3           # no adjustments until 3 receipts per context type
MAX_WEIGHT = 0.5          # learned adjustments never exceed 50% of base profile
SAMPLES_FOR_MAX = 20      # reach max weight at 20 samples
```

### Learning signal mapping
| WabbleSpec signal | EMA rating |
|---|---|
| Verifier PASS receipt | +1 |
| Verifier FAIL receipt | -1 |
| I4 REVISE cycle triggered | -1 (strong signal) |
| Attestation required | -1 with context note |
| Archive receipt written | +1 |

### Persistence format
`_wabblespec/memory/learned-params/learned-params-{context_type}.json`
```json
{
  "context_type": "code-generation",
  "sample_count": 12,
  "positive_count": 9,
  "negative_count": 3,
  "positive_params": { "temperature": 0.19, "top_p": 0.79 },
  "negative_params": { "temperature": 0.23, "top_p": 0.82 },
  "adjustments": { "temperature": -0.018, "top_p": -0.014 },
  "last_updated": "ISO-8601",
  "freshness": "FRESH"
}
```

### New Feedback mode
`feedback --learn --receipt <path> --context-type <type>`

### Files created
- `_shared/scripts/param-learner.py` (Wave 0 — already written)
- `.wabblespec/memory/learned-params/` (directory, gitignored entries)

### Files modified
- `modules/l8/feedback/SKILL.md` — add `--learn` mode
- `modules/l2/model-router/SKILL.md` — read learned-params/ when outputting ContextTuner results

---

## Wave 6 — Benchmark Axis Decomposition (Benchmark AUGMENT)
**Processing path:** Synth → Blueprint → Augment → Benchmark → Forge
**Version target:** 0.8.4

### Purpose
Formalizes WabbleSpec-specific scoring axes for all L8 benchmark gates. Every blueprint must define quality metric as a named-axis decomposition. Adds degradation analysis requirement.

### WabbleSpec scoring axes (replacing G0DM0D3's biased axes)

| Axis | Points | Operationalization |
|---|---|---|
| Spec-compliance | 0–25 | Output fulfills declared EARS requirements in task card |
| Receipt completeness | 0–20 | All schema-required fields present and non-empty |
| Invariant adherence | 0–20 | Output avoids I1/I4/I6/I10/I11 violations |
| Verification gate pass | 0–20 | Would output pass Verifier without REVISE cycle |
| Language precision | 0–15 | Modals correct (SHALL/SHOULD/MAY), hedging absent |

**G0DM0D3 axes NOT adopted:**
- Length bias (46.7% effective weight) — WabbleSpec values concision, not verbosity
- Anti-refusal axis (26.1%) — jailbreak metric, has no place in SDLC evaluation

### Degradation analysis protocol (new requirement in benchmark-discipline.md)
Before any composite blueprint gate is accepted:
1. Run candidate against full fixture set, record total + per-axis scores
2. Zero each axis one at a time, record total drop
3. Confirm hierarchy: spec-compliance drop > receipt-completeness drop etc.
4. If ordering is wrong, adjust weights and repeat
5. Document in blueprint as `axis_calibration_run: true` with per-axis deltas

### Files modified
- `modules/l8/benchmark/rules/benchmark-discipline.md` — add axis decomposition + degradation protocol
- `modules/l8/benchmark/schemas/benchmark.schema.json` — add `axes` array to benchmark_gate

---

## Implementation Sequence

```
Wave 0  ──► scripts written + tested standalone
  ├── Wave 1  (InferenceGuard NEW module)
  │     └── Wave 4  (Red/Blue integration — depends on Wave 1 + Wave 3)
  ├── Wave 2  (ContextTuner AUGMENT — L8 chain)
  │     └── Wave 5  (ParamLearner — depends on Wave 2 context types)
  ├── Wave 3  (STM Pipeline AUGMENT — L8 chain)
  │     └── Wave 4  (Blue STM integration)
  └── Wave 6  (Benchmark axes — independent)
```

Waves 1, 2, 3, 6 can start in parallel after Wave 0 completes.
Wave 4 depends on Waves 1 AND 3.
Wave 5 is separately gated on the 50+ receipt corpus condition.

---

## Invariant Compliance

| Invariant | Risk | Mitigation |
|---|---|---|
| I1 (spec is truth) | All waves | Wave 0 scripts are the spec for algorithm behavior. Blueprint locks spec before Augment. |
| I4 (verification explicit) | InferenceGuard | Acceptance criteria declared in Wave 1 SKILL.md before execution. |
| I6 (vendor-neutral) | ContextTuner, InferenceGuard | No model names anywhere. Parameters are generic API fields. Trigger vocab has no model names. |
| I8 (evidence chain) | All AUGMENT waves | Every augment: Synth → Blueprint → Augment → Benchmark → Forge. No skips. |
| I10 (receipts) | InferenceGuard | Receipt on every execution AND every non-execution. Zero implied completions. |
| I11 (framework/product separation) | Learned params | All new files in `modules/` or `.wabblespec/memory/`. Nothing in `project/repo/`. |

---

## What Is Explicitly Excluded

- GODMODE system prompt — not adapted
- Anti-refusal scoring axis — jailbreak metric
- OpenRouter dependency — I6 prohibits it
- ULTRAPLINIAN model tier lists — model names, I6 violation
- Chaotic context type — 66.7% precision attractor
- AutoTune confidence as hard gate — anti-calibrated (incorrect predictions average 76.4% confidence vs 65.2% for correct)
- Parseltongue Tier 3 terms `nsfw`, `explicit`, `uncensored`, etc.
