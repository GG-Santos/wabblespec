# Rule File Authoring Template

Standard format for individual rule files in a skill's `rules/` or `references/` subdirectory. Derived from the react-best-practices-build schema (types.ts Rule interface).

## Frontmatter Schema

```yaml
---
title: Short imperative phrase describing what to do (not what to avoid)
impact: CRITICAL | HIGH | MEDIUM-HIGH | MEDIUM | LOW-MEDIUM | LOW
impactDescription: Optional quantified benefit, e.g. "2-10× improvement"
tags: [category-prefix, topic, concern]
---
```

**impact values in priority order:**
1. CRITICAL — blocks correctness or causes data loss
2. HIGH — significant performance or security impact
3. MEDIUM-HIGH — meaningful improvement, noticeable to users
4. MEDIUM — standard best practice, expected in production code
5. LOW-MEDIUM — micro-optimization, apply opportunistically
6. LOW — polish; apply when reviewing mature code

## Body Structure

```markdown
## Title

Brief explanation of WHY this rule matters (1-3 sentences). Name the specific cost of not following it.

**Incorrect:**

[code block showing the wrong approach]

Optional explanation of why this is wrong.

**Correct:**

[code block showing the right approach]

Optional explanation of what makes this correct.

Reference: [url](url)
```

## Label Convention

Use `**Incorrect:**` and `**Correct:**` as the standard label pair — not Before/After (temporal), Bad/Good (evaluative), or ❌/✅ (emoji). Exact case: `**Incorrect:**` and `**Correct:**`.

## Naming Convention

Rule file names use `category-specific-concern.md`:
- `async-parallel.md` — async category, parallel concern
- `bundle-barrel-imports.md` — bundle category, barrel imports concern
- `rerender-memo.md` — rerender category, memoization concern

Prefix `_` for non-rule files in the same directory: `_template.md`, `_sections.md`.

## Section Metadata (`_sections.md`)

```markdown
## 1. Section Title (section-id)

**Impact:** CRITICAL

**Description:** One sentence on what this section covers and why it's ordered here.
```

## Example Rule File

```markdown
---
title: Use Promise.all for Independent Operations
impact: CRITICAL
impactDescription: 2-10× improvement
tags: [async, parallelism, performance]
---

## Use Promise.all for Independent Operations

Sequential awaits add full network latency per operation. When operations have no dependency on each other, run them in parallel.

**Incorrect:**

```typescript
const user = await fetchUser()
const posts = await fetchPosts()
const comments = await fetchComments()
```

Three round trips where one is sufficient.

**Correct:**

```typescript
const [user, posts, comments] = await Promise.all([
  fetchUser(),
  fetchPosts(),
  fetchComments()
])
```

Reference: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all
```
