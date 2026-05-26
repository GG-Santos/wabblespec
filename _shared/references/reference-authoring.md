# Reference Authoring Standards

How to write `_shared/references/` and `_shared/dev/` files for WabbleSpec. Consumers: skill-factory, any framework author.

---

## When this applies

When creating or editing any file in `_shared/references/` or `_shared/dev/`. These files are read by modules during cold-start with no prior session context. Every authoring decision affects how reliably a cold agent can find, load, and apply the file.

---

## Core rules

**Lead with the rule.** State what to do first. Explain why second — and only if the why is non-obvious or changes how to apply the rule.

**Use code examples.** Show, don't tell. An inline code example is worth three sentences of prose.

**Skip the obvious.** Do not document what the schema, code, or module name already makes clear. If a reader can infer it from the context they already have, omit it.

**One concept per file.** If a file covers two unrelated patterns, split it. A reference file that tries to cover too much will either be skipped (too long to load) or misapplied (wrong section loaded).

**Bullet points over paragraphs.** Scannable beats readable for AI consumption. Paragraphs are for narrative; reference files are for lookup.

**Minimum "when this applies" clause.** Every reference file must open with a brief statement of what it covers and when a module should load it. One to three sentences. This lets a cold agent decide whether to load the file at all without reading the whole thing.

---

## Length discipline

If a reference file exceeds 80 lines, ask:
- Does it cover more than one concept? If yes, split.
- Does it repeat information available in another reference? If yes, cut and cross-reference.
- Does it contain narrative explanation that could be a bullet? If yes, compress.

Short files are not under-documented files. They are well-targeted files.

---

## Good vs bad examples

**Bad — paragraph-first:**
```markdown
When an error occurs in our application, we have established a consistent pattern
for how errors should be formatted. This pattern helps maintain consistency across
all modules and makes it easier for downstream consumers to handle errors correctly.
The key thing to understand is that all errors must include both a type and a message.
```

**Good — rule-first:**
```markdown
## Error event format

All error events must include `type` and `message`. See `error-event.schema.json`.

- `type`: one of SOFT | HARD | DEPENDENCY | CONTEXT_EXHAUSTION | SPEC_VIOLATION | STALENESS_VIOLATION | COMMAND_RISK
- `message`: human-readable, states what failed and what to do next
```

---

**Bad — over-explaining the obvious:**
```markdown
The FRESH state means that the evidence was recently verified and can be trusted
fully. When evidence is in the FRESH state you can use it without any caveats or
additional verification steps.
```

**Good — rule only:**
```markdown
| FRESH | Recently verified. Use freely. |
```

---

## Cross-referencing

When a concept in one reference file is covered in detail elsewhere, cite the other file rather than duplicating:

```markdown
Full rules: `_shared/references/staleness-states.md`
Schema: `_shared/schemas/drawer.schema.json`
```

Never copy content from one reference into another. Update the source; reference it everywhere else.

---

## Cold-start safety

Reference files may be loaded by a module that has no memory of prior turns. Write them as if the reader has:
- The current task card
- The module's own SKILL.md
- Nothing else

Do not assume the reader knows which session they are in, which prior waves ran, or which other references have been loaded. If an example uses a variable or path that needs to be understood, define it inline.
