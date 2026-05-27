# Capability Descriptors

Eight vendor-neutral descriptors used throughout WabbleSpec. No model names. No provider names. These are the only terms used to describe runtime capability.

## Descriptor definitions

| Descriptor | Definition | ModelRouter uses when |
|---|---|---|
| `code-generation` | Writes, completes, refactors code across common languages | Task shape: code, implementation, refactor |
| `analysis` | Analyzes code, data, documents for patterns, defects, compliance | Task shape: review, audit, debug |
| `synthesis` | Synthesizes information from multiple sources into structured artifacts | Task shape: summarize, consolidate, research |
| `instruction-following` | Follows multi-step structured instructions reliably | Task shape: checklist execution, recipe following |
| `reasoning` | Reasons through multi-step problems with visible intermediate steps | Task shape: complex decision, decomposition |
| `tool-use` | Invokes declared tools with structured input/output | Task shape: any task requiring external tools |
| `vision` | Processes images, screenshots, diagrams | Task shape: visual input required |
| `embedding` | Produces vector embeddings for semantic similarity | Task shape: semantic search, similarity matching |

## Confidence thresholds

| Confidence | Interpretation |
|---|---|
| >= 0.9 | High confidence — capability reliably available |
| 0.7–0.9 | Medium confidence — capability available with occasional gaps |
| 0.5–0.7 | Low confidence — capability available but unreliable |
| < 0.5 | Very low — treat as unavailable for planning purposes |

ModelRouter treats capabilities with confidence < 0.5 as unavailable when selecting lanes.

## What never appears in framework files

Model-specific identifiers, provider names, version strings, platform API names. If you encounter these in a framework file, it is an I6 violation — file a SPEC_VIOLATION error.
