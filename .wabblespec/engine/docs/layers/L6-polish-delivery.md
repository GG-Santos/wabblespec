# L6 — Polish and Delivery

Output quality layer. L6 modules refine and finalize content before it is delivered or published. They run after Executor has produced the primary output and before Archive closes the run.

## Modules

### Content quality
| Module | Role |
|--------|------|
| `polish` | Orchestrates the full polish pipeline. Runs up to 6 passes: Proofread, Markdown, Copy, Writer (core), Legal, Translate (optional). Entry point for all L6 polish work. |
| `proofread` | Grammar, spelling, punctuation, and style consistency. First pass in the polish pipeline. |
| `markdown` | Markdown structure, heading hierarchy, table formatting, code block fencing. Second pass. |
| `copy` | Copywriting: clarity, tone, voice, word choice. Third pass. |
| `writer` | Full prose rewrite when copy-level changes are insufficient. Not idempotent — each run may produce a different result. |
| `homowabian` | Specialized linguistic transformation module. Handles register shifts, dialect adaptation, and formality calibration. |

### Specialized
| Module | Role |
|--------|------|
| `legal` | Legal language review: disclaimers, IP claims, liability language, regulatory compliance. Adds required disclosures. |
| `translate` | Language translation. Produces a translated artifact alongside the source. Does not overwrite source. |
| `document` | Technical documentation generation. Produces user-facing docs from spec and code artifacts. |
| `research-log` | Structured research capture. Writes research findings to `research/{feature-slug}/research.md` when `spec_binding` is present. |

### Go-to-market
| Module | Role |
|--------|------|
| `market` | Go-to-market positioning. Produces positioning statements, elevator pitches, competitive differentiation. Not idempotent. |
| `optimize` | Discoverability and SEO optimization. Idempotent — safe to re-run. |

## Polish pipeline

```
Polish (orchestrator)
  Pass 1: Proofread
  Pass 2: Markdown
  Pass 3: Copy
  Pass 4: Writer     ← core rewrite
  Pass 5: Legal      ← optional (flag --legal)
  Pass 6: Translate  ← optional (flag --translate=<lang>)
```

Polish is the only entry point. Do not invoke sub-passes directly unless debugging a specific pass.

## Key behaviors

**Writer** is not idempotent. Running Writer twice on the same content may produce two different outputs. Use it deliberately, not as a default.

**Legal** adds required disclosures — it does not remove content flagged as legally problematic. For removal, escalate to human review.

**Market** requires three declared inputs: product name, target audience, and competitive alternatives. Missing any of these causes the module to halt and request the missing input.

**Research-log** writes to `research/{feature-slug}/research.md` only when a `spec_binding` is declared. Without spec_binding, research is ephemeral — session-only, not persisted.

## Layer rules

- Polish sub-passes (proofread, markdown, copy, writer, legal, translate) do not write receipts independently — Polish orchestrator writes one receipt covering all passes run
- Writer is not idempotent — declare this in the receipt when Writer runs
- Legal additions are additive — never remove existing content without human review
- Translate never overwrites the source artifact — always produces a separate translated file
