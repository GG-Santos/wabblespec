# L1 — Analysis and Planning

The largest layer. L1 modules do the analytical and planning work that turns a recipe into an executable wave plan. Most L1 modules run inside the pipeline; some are standalone tools invoked directly.

## Modules

### Core pipeline modules
| Module | Role |
|--------|------|
| `scope-frame` | Bounds the task: what is in, what is out, constraints, success criteria. Locks scope for the run. |
| `specify` | Produces the technical specification using the active platform package. Input to Decompose. |
| `decompose` | Breaks the spec into an ordered wave plan with checkpoints and rollback targets. Writes `wave-current.md`. |
| `apply` | Routing engine. Reads platform package and capability gateways, assembles multi-module context. Produces delta proposals. |

### Input refinement
| Module | Role |
|--------|------|
| `enhance` | Resolves vague input before ScopeFrame. Extracts intent across 9 dimensions. Asks at most 3 clarifying questions. Auto-triggered by Recipe when `input_vague = true`. |
| `sharpen` | Narrows broad input to a specific actionable target. Reduces scope ambiguity without asking questions. |
| `brainstorm` | Generates multiple solution options before Specify commits to an approach. |
| `plan` | Produces a structured approach plan for complex tasks before Decompose. |
| `triage` | Classifies and prioritizes incoming tasks by urgency, complexity, and dependency. |
| `interview` | Structured question-gathering from human. Used when Enhance questions are insufficient. |

### Code and repo analysis
| Module | Role |
|--------|------|
| `analyze` | Root cause analysis, code investigation, failure diagnosis. |
| `explore` | Open-ended codebase exploration and discovery. |
| `api` | API contract analysis and documentation. |
| `deps` | Dependency analysis, SBOM generation, vulnerability surface mapping. |
| `perf` | Performance profiling, baseline measurement, bottleneck identification. |
| `flag` | Marks code regions, decisions, or spec sections for human review. Writes a manifest. |

### Code transformation
| Module | Role |
|--------|------|
| `clean` | Targeted surface cleanup: dead code removal, formatting normalization, identifier renaming. Scope always explicitly declared. BREAKING changes halt. |
| `migrate` | Guides migration across framework versions, language versions, or API changes. |
| `shift` | Compatibility analysis between current and target state. Produces a diff and compatibility report. |
| `sync` | Synchronizes two diverged codebases, configs, or spec documents. |
| `organize` | Restructures file layout, module grouping, or directory organization. |

### Reference
| Module | Role |
|--------|------|
| `reference-load` | Loads external reference material into context on demand. |
| `propose` | Drafts a formal change proposal for human review before committing to a direction. |
| `test` | Generates or runs tests for a specified target. |

## Layer rules

- L1 modules may read from L0 receipts
- L1 modules do not call Executor directly — they produce inputs for L2
- `apply` is the routing engine; it reads platform packages (L3) and gateway rules (L4)
- `clean` never produces BREAKING changes — halts and routes to Executor if a BREAKING change is detected
- `enhance` asks at most 3 questions, never more
