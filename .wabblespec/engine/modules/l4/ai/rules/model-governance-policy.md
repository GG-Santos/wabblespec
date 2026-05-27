# Gateway AI — Model Governance Policy

Rules enforced by gateway-ai Phase B verdict. Applies to any production system using LLM models, agent architectures, or eval-gated AI pipelines. Violations produce FLAG or BLOCK verdicts.

---

## Rule M1: Model Version Pinning

**Requirement:** No production LLM call may use an unpinned or `latest` model identifier.

| Requirement | Details |
|---|---|
| Explicit version | All model identifiers in production code must be explicit version strings (e.g., `claude-sonnet-4-6`, `gpt-4o-2024-11-20`) |
| No `latest` alias | `latest`, `current`, or any symbolic alias that resolves dynamically = BLOCK |
| Fallback model declared | Every primary model call must declare a fallback model for unavailability or rate-limit scenarios |
| Version bump procedure | Model version changes require: eval suite re-run, regression check, spec update, PR review |

**Failure modes:**
- Any production model call using `latest` or non-version-pinned identifier = BLOCK
- No fallback model declared for any primary model call = FLAG
- Model version changed without eval suite re-run = BLOCK

---

## Rule M2: Eval Suite Before Model or Prompt Version Bump

**Requirement:** Every model version bump and every system prompt version change must pass an eval suite before deployment.

**Minimum eval suite requirements:**

| Eval type | Requirement |
|---|---|
| Regression fixtures | At least 10 golden input/output pairs per capability; all must PASS after bump |
| Capability coverage | Evals cover all declared capabilities of the LLM feature (not just happy path) |
| Adversarial fixtures | At least one prompt injection attempt per input surface |
| Latency baseline | P95 latency measured and within declared budget |
| Cost baseline | Average token cost per call measured and within declared budget |

**Failure modes:**
- Model version bump deployed without eval suite run = BLOCK
- Eval suite passes with < 10 fixtures per capability = FLAG
- No adversarial fixture in eval suite for user-facing LLM feature = FLAG
- Eval suite results not recorded in receipt or version control = FLAG

---

## Rule M3: Agent Loop Bounds

**Requirement:** Any agent loop (an LLM that can invoke tools and observe results across multiple turns) must declare explicit termination conditions.

| Bound type | Requirement |
|---|---|
| Maximum iterations | Hard limit declared in code; loop terminates and escalates to human when reached |
| Maximum tool invocations | Hard limit per session; prevents runaway tool use |
| Irreversible tool call gate | Any tool call classified as irreversible (delete, send, purchase, deploy) requires Attestation before execution |
| Cycle detection | Agent must detect and break infinite loops (same tool call with same args twice in a row) |

**Iteration limits (defaults — override requires spec justification):**

| Use case | Default max iterations |
|---|---|
| Single-task agent | 10 |
| Research/exploration agent | 20 |
| Multi-step workflow agent | 50 |
| No limit declared | Not permitted — must be declared |

**Failure modes:**
- Agent loop with no iteration limit = BLOCK
- Irreversible tool call without Attestation gate = BLOCK
- No cycle detection = FLAG
- Maximum iterations exceeded without escalation to human = BLOCK

---

## Rule M4: Chain Step Contracts

**Requirement:** Every step in an LLM chain (sequential prompt pipeline) must declare its input schema, output schema, and failure handling.

| Contract element | Requirement |
|---|---|
| Input schema | Declared for each chain step; validated before step invocation |
| Output schema | Declared for each chain step; validated before passing to next step |
| Failure handling | Each step declares what happens on: model error, schema validation failure, timeout |
| Context isolation | Each step receives only the context it needs — full conversation history not passed unless required |

**Failure modes:**
- Chain step with undeclared input or output schema = FLAG
- Chain step that passes full prior context without pruning = FLAG
- No failure handling declared for any chain step = BLOCK (failure in one step must not silently corrupt downstream steps)

---

## Rule M5: Red-Team Coverage Requirement

**Requirement:** Any user-facing LLM feature that processes arbitrary user input must undergo adversarial coverage before production launch.

**Minimum red-team surface coverage:**

| Attack vector | Must be tested |
|---|---|
| Prompt injection (direct) | Yes |
| Prompt injection (indirect — via loaded content) | Yes |
| Role-play / persona override | Yes |
| Data exfiltration via prompt | Yes |
| Jailbreak pattern resistance | Yes — current top-5 public jailbreak patterns |

**Acceptable coverage methods:** Automated red-team tools (Garak, Promptfoo adversarial mode, or equivalent), or manual adversarial testing with documented scenarios.

**Failure modes:**
- User-facing LLM feature launched without any adversarial coverage = BLOCK
- Red-team coverage documented but no findings reviewed = FLAG
- Coverage only for happy path with no adversarial scenarios = FLAG
