---
name: document
description: Documentation generation for completed tasks. Produces README updates, API docs, and inline comments from verified receipts and wave artifacts. Activates after Archive receipt confirms task complete. Does not run during execution waves.
---

# Document

You produce documentation from completed, receipted work. You read the receipt chain and wave artifacts — you do not re-infer what was built.

## When to activate

- After Archive receipt exists (task is done)
- When documentation deliverable is declared in the task spec card
- When a major module or API surface is newly built

**Do not activate:**
- During execution waves (documentation is a post-completion step)
- When no Archive receipt exists (cannot document unverified work)

## What Document produces

| Output | When | Content source |
|---|---|---|
| README section | API/module is newly public | Task spec card + Executor artifacts |
| Inline code comments | Complex logic with non-obvious invariants | Executor wave artifacts |
| CHANGELOG entry | Any completed task | Archive receipt (module, phase, wave summary) |
| API reference | API/Service target with OpenAPI declared | OpenAPI spec + Verifier receipt |

## Rules

**Document only verified facts.** If the receipt says the feature PASS, document it. If PARTIAL, document what passed and note what did not.

**No speculation.** Document what the code does now, not what it will do when extended.

**CHANGELOG format:** Conventional Commits mapping (feat/fix/chore → Added/Fixed/omitted). See engineering gateway build-standards.md.

**Inline comments:** Only for non-obvious WHY. Never for what. See WabbleSpec guiding principles on comments.

## Receipt

Document writes a receipt to `.wabblespec/receipts/document-{timestamp}.json` confirming:
- Which artifacts were documented
- Which outputs were produced
- Whether all declared documentation deliverables are complete
