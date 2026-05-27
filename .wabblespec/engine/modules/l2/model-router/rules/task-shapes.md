# Task Shapes and Context Types

Two classification systems operate in model-router: **task shapes** (capability routing) and **context types** (ContextTuner parameter selection). Both run on every routing pass.

---

## Task shapes (capability routing)

Maps the current wave's work to required capability descriptors.

| Task shape | Required capabilities | Notes |
|---|---|---|
| code | code-generation | Implementation, refactoring, completion |
| review | analysis | Code review, audit, defect detection |
| research | synthesis, analysis | Multi-source information gathering |
| spec | instruction-following, synthesis | Writing structured spec artifacts |
| debug | analysis, reasoning | Root cause investigation |
| plan | reasoning, synthesis | Decomposition, wave planning |
| test | code-generation, analysis | Test generation, test analysis |
| document | synthesis, instruction-following | Documentation generation |
| visual | vision | Any task with image/screenshot input |
| multi-target | code-generation + platform-specific | Task spanning multiple build targets |
| agent | tool-use, reasoning | Agent loop execution |

### Classification rules

1. Read the current wave declaration from Decompose output
2. Match wave outputs and acceptance criteria to task shapes
3. If wave has mixed outputs (code + docs), select the dominant shape
4. If equally mixed: use `multi-target` shape — may trigger Ensemble

### Fallback selection

| Primary capability | Fallback |
|---|---|
| code-generation | synthesis (for documentation-heavy waves) |
| reasoning | analysis |
| synthesis | instruction-following |
| vision | none — declare unavailable |
| embedding | none — declare unavailable |

---

## Context types (ContextTuner parameter selection)

Six WabbleSpec context types, replacing the four task-shape buckets previously used for parameter selection. ContextTuner scores the current message (3x) and last four history messages (1x each). Winner is selected by score ratio; blended with `planning` baseline if confidence < 0.6.

**No chaotic type.** G0DM0D3's chaotic type attractor has 66.7% precision and systematically misclassifies code tasks containing delete/break/crash vocabulary.

### Detection patterns

| Type | Detection patterns |
|---|---|
| `spec-authoring` | `WHEN`, `THEN`, `SHALL`, `SHOULD`, `MUST`, `acceptance criteria`, `EARS`, `requirement`, `specification` |
| `code-generation` | Code blocks (``` backticks), `function`, `class`, `method`, `implement`, `refactor`, `def `, `const `, `import ` |
| `security-review` | `vulnerability`, `CVE`, `threat`, `attack surface`, `pentest`, `red team`, `exploit`, `OWASP`, `injection`, `XSS` |
| `planning` | `wave plan`, `task card`, `decompose`, `architecture`, `dependency`, `phase`, `milestone`, `rollback`, `checkpoint` |
| `synthesis` | `summarize`, `generate`, `changelog`, `document`, `report`, `draft`, `compile`, `aggregate`, `from.*receipts` |
| `administrative` | `version`, `bump`, `archive`, `receipt`, `CHANGELOG`, `INDEX`, `framework.yaml`, `seed run`, `witness` |

### Sampling parameters by context type

| Type | temp | top_p | top_k | freq | pres | rep |
|---|---|---|---|---|---|---|
| `spec-authoring` | 0.30 | 0.85 | 30 | 0.20 | 0.10 | 1.05 |
| `code-generation` | 0.20 | 0.80 | 25 | 0.20 | 0.00 | 1.05 |
| `security-review` | 0.50 | 0.90 | 50 | 0.20 | 0.20 | 1.08 |
| `planning` | 0.60 | 0.90 | 50 | 0.15 | 0.15 | 1.05 |
| `synthesis` | 0.80 | 0.92 | 60 | 0.30 | 0.30 | 1.10 |
| `administrative` | 0.20 | 0.85 | 25 | 0.10 | 0.00 | 1.05 |

### Context type to task shape mapping

| Context type | Closest task shape |
|---|---|
| `spec-authoring` | spec |
| `code-generation` | code |
| `security-review` | review |
| `planning` | plan |
| `synthesis` | research / document |
| `administrative` | document |

Context type classification is independent of task shape selection. Both are written to the routing receipt.
