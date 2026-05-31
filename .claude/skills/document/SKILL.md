---
name: document
description: Documentation generation for completed tasks. Produces README updates, API docs, and inline comments from verified receipts and wave artifacts. Activates after Archive receipt confirms task complete. Does not run during execution waves. For reference-type outputs, enforces a cross-references section before writing the document receipt.
promoted_from: cross-link-document-required-section-v1
promoted_at: 2026-05-25T09:14:00+00:00
---

# Document

You produce documentation from completed, receipted work. You read the receipt chain and wave artifacts — you do not re-infer what was built.

## What this skill does

Documentation generation for completed tasks. Produces README updates, API docs, and inline comments from verified receipts and wave artifacts. Activates after Archive receipt confirms task complete. Does not run during execution waves. When the task declares a reference-type documentation deliverable, verifies the produced file contains a cross-references section with at least one entry before writing the document receipt.

## When to use

- After Archive receipt exists (task is done)
- When documentation deliverable is declared in the task spec card
- When a major module or API surface is newly built

**Do not activate:**
- During execution waves (documentation is a post-completion step)
- When no Archive receipt exists (cannot document unverified work)

## Reference Routing

| Situation | Reference |
|---|---|
| Document receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Output contract

| Output | When | Content source |
|---|---|---|
| README section | API/module is newly public | Task spec card + Executor artifacts |
| Inline code comments | Complex logic with non-obvious invariants | Executor wave artifacts |
| CHANGELOG entry | Any completed task | Archive receipt (module, phase, wave summary) |
| API reference | API/Service target with OpenAPI declared | OpenAPI spec + Verifier receipt |
| Audio narration / podcast | Documentation deliverable declares audio output type | Document text + `~~tts-generator` capability |

## Rules

**Document only verified facts.** If the receipt says the feature PASS, document it. If PARTIAL, document what passed and note what did not.

**No speculation.** Document what the code does now, not what it will do when extended.

**CHANGELOG format:** Conventional Commits mapping (feat/fix/chore → Added/Fixed/omitted). See engineering gateway build-standards.md.

**Inline comments:** Only for non-obvious WHY. Never for what. See WabbleSpec guiding principles on comments.

**Reference-type outputs require a cross-references section.** When the task-card declares a documentation deliverable of type `reference` — any file destined for `.wabblespec/engine/shared/references/` or explicitly typed `reference` in the task-card — Document must inspect its own output before writing the document receipt.

The inspection check:
```
if deliverable.type == "reference" OR destination starts with ".wabblespec/engine/shared/references/":
    if output_file contains neither "## Cross-references" nor "## See also":
        emit CROSS_LINK_MISSING
        do not write document-receipt
        surface: "Reference document at {path} has no cross-references section.
                  Add a '## Cross-references' or '## See also' section with at
                  least one entry linking to a related module, schema, or SKILL.md."
    elif cross_references_section has zero real entries (empty or comment-only):
        emit CROSS_LINK_MISSING
        do not write document-receipt
        surface same message
    else:
        proceed — write document-receipt with cross_link_verified: true
```

Non-reference outputs (README, inline comments, CHANGELOG, API reference) are not subject to this check. `cross_link_verified` is `null` for non-reference deliverables.

A cross-references section must contain at least one real entry. An empty section header or a section containing only HTML comments does not satisfy the requirement.

## Receipt

Document writes a receipt to `.wabblespec/state/receipts/document-{timestamp}.json` confirming:
- Which artifacts were documented
- Which outputs were produced
- Whether all declared documentation deliverables are complete
- `cross_link_verified`: `true` if reference-type output passed cross-reference check; `null` if not applicable

## Audio Output

When the task declares an audio output type, produce the narration or podcast using this 5-step workflow:

1. **Extract document text** — Read the source document into plain prose. Strip headers-as-structure into topic transitions in the script.
2. **Generate conversation script** — Write a two-host dialogue as a JSON array. Host 1 leads and introduces topics; Host 2 reacts, analyzes, and asks questions. Each turn under 4000 characters. Vary turn lengths — mix short reactions with longer explanations. Include a brief intro and outro. Do not read verbatim; discuss and interpret.
3. **Write script to disk** — Save to `/tmp/podcast_script.json`:
   ```json
   [
     {"speaker": "host1", "text": "..."},
     {"speaker": "host2", "text": "..."}
   ]
   ```
4. **Generate audio** — Call `~~tts-generator` with the script file and declared output path.
5. **Clean up** — Remove the temp script file after successful audio generation.

For single-voice narration: write clean prose to `/tmp/tts_input.md`, then call `~~tts-generator` with `--file`. Default output location: `~/Downloads/`.

## LLM-optimized output format

When the documentation target will be consumed by agents or LLMs (reference docs, API docs, module overviews), apply these five constraints:

**Token-efficient writing.** No redundant explanations. State what the thing does and where to find it. One sentence per concept is the target; never repeat information already expressed by a heading or identifier name.

**Concrete file references.** Every claim about a module, function, or script includes the specific file path. When a line number helps locate a key section, include it. "The main entry point" is not a reference. `engine/shared/scripts/receipt-writer.py:42` is.

**No duplication.** Each piece of information appears in exactly one output file. When two doc files would overlap, one owns the content and the other links to it: "See [docs/build-system.md](docs/build-system.md) for build targets." Duplicated content diverges silently.

**Parallel agent dispatch.** When producing multi-section documentation (architecture, build, testing, development, deployment, files catalog), issue section tasks in parallel. Each section agent reads the relevant source files independently. Sequencing doc sections through a single thread wastes wall-clock time and produces no quality benefit.

**Timestamp header.** Generated documentation files start with an HTML comment timestamp. This signals when the snapshot was taken and lets readers judge staleness without opening a git log. Format:
```
<!-- Generated: YYYY-MM-DD HH:MM:SS UTC -->
```

## Common failure modes

**Suppressing CROSS_LINK_MISSING to ship faster.** A reference document with no cross-references is navigation-dead — humans and downstream modules citing it cannot find related artifacts. The loop-back to add at least one cross-reference link is not optional.

**Treating the section header as satisfying the requirement.** An empty `## Cross-references` heading does not pass the check. At least one real entry (link, module reference, or schema pointer) must appear under the heading. HTML comments do not count.

**Applying the check to non-reference outputs.** README updates, inline comments, and CHANGELOG entries follow different conventions. The cross-references check applies only to `.wabblespec/engine/shared/references/` documents or task-card-typed `reference` deliverables.

## Not tested

The check assumes `deliverable.type` is declared in the task-card. Task cards that do not explicitly declare deliverable type use path-based detection (destination starts with `.wabblespec/engine/shared/references/`). Benchmark validated 8 held-out fixture cases (stale_evidence_rate = 0.0).
