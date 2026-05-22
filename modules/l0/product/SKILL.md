---
name: product
description: Captures product goals, user segments, success metrics, and business constraints before P1 spec work begins. Product context is upstream of ScopeFrame and Interview — it captures the "why" before Interview captures the "what." Activates once per major product initiative or on /product command. Writes product-context.md to .wabblespec/plans/.
---

# Product

You run before spec work begins. Your output anchors every downstream decision — Interview resolves ambiguity against it, ScopeFrame declares boundaries from it, and Specify populates requirements within it.

## When to activate

- New project or major product initiative
- `/product` command
- ScopeFrame or Interview signal missing product context

Do not run mid-execution. Product context is set before planning begins, not updated mid-wave.

## What to capture

### Product goals

The purpose the product serves. Stated as outcomes, not features.

```markdown
## Goals

- <outcome 1: what improves for whom>
- <outcome 2>
```

No feature lists here. If the user gives features, ask what outcome each enables. Record the outcome.

### User segments

Declared user types with characteristics relevant to the product:

```markdown
## User Segments

### <Segment name>

**Who:** <brief description>
**Context:** <how and where they use the product>
**Primary need:** <what they need from the product>
**Known constraints:** <technical, accessibility, time, literacy>
```

Minimum 1 segment. Maximum: as many as exist with meaningfully different needs. If two segments have identical needs and constraints, they are one segment.

### Success metrics

Measurable indicators that the product is achieving its goals:

```markdown
## Success Metrics

| Metric | Target | Measurement method |
|---|---|---|
| <metric name> | <threshold> | <how measured> |
```

Each metric must be measurable. "User satisfaction" is not measurable. "SUS score >= 75 at 3-month review" is measurable.

### Business constraints

Hard constraints the product must operate within:

```markdown
## Business Constraints

- **Budget:** <if declared>
- **Timeline:** <if declared>
- **Compliance:** <regulatory requirements — GDPR, HIPAA, PCI-DSS, etc.>
- **Platform requirements:** <target OS, browser, device constraints>
- **Integration requirements:** <must-connect systems>
```

### Open questions

Ambiguities that Interview must resolve:

```markdown
## Open Questions

- <question 1 — what remains undefined that Interview should clarify>
```

Interview reads this section before generating its own question set.

## Standards discovery

Before writing product-context.md, scan the target project for existing conventions. This is a lightweight pattern read — not an interactive session. Write each discovered standard to Memory as a FRESH drawer before writing product-context.md.

**What to look for:**

| Category | Signals |
|---|---|
| Naming | File naming pattern, variable naming, folder structure conventions |
| API shape | Response envelope structure, error format, versioning scheme |
| Error handling | Error codes, exception boundaries, logging pattern |
| Testing | Test file location, naming convention, assertion style |
| Data | Schema migration pattern, model naming, primary key convention |
| Build | Toolchain choices, lint/format config, lockfile policy |

**What counts as a standard worth capturing:**
- Pattern appears in 3+ files (consistent, not accidental)
- Pattern is non-obvious (a new developer wouldn't infer it from the framework defaults)
- Pattern could produce a defect or rework if violated

**What to skip:** Framework defaults, obvious conventions (e.g., "use camelCase in JS"), one-off patterns.

**Drawer format per discovered standard:**

```json
{
  "id": "std-<category>-<slug>-<date>",
  "title": "<short name of the standard>",
  "content": "<one-paragraph description: what the standard is, why it exists, how to apply it, what breaks if violated>",
  "category": "project-standard",
  "criticality": "critical | high | advisory",
  "evidence_paths": ["<file1>", "<file2>"],
  "source": "product-discovery"
}
```

**Criticality assignment:**
- `critical` — Violation causes integration failure, security gap, or data corruption. Guard should enforce. ScopeFrame must cite.
- `high` — Violation causes rework or spec mismatch. ScopeFrame should cite.
- `advisory` — Useful context, but violation is recoverable. Loaded on demand.

Write to Memory before writing product-context.md. Cite the drawer IDs in the product-context.md Standards section.

**If no standards found** (new project, empty codebase): skip discovery. Write product-context.md with an empty Standards section noting "no existing codebase conventions detected."

## Output

Write `product-context.md` to `.wabblespec/plans/`.

Format:

```markdown
# Product Context

**Product name:** string
**Initiative:** string (what specific effort this context covers)
**Written at:** ISO 8601
**Written by:** product module

## Goals
[...]

## User Segments
[...]

## Success Metrics
[...]

## Business Constraints
[...]

## Open Questions
[...]

## Project Standards

| Standard | Criticality | Drawer ID | Evidence |
|---|---|---|---|
| <standard name> | critical\|high\|advisory | std-<id> | <one file path> |
```

## What not to do

- Do not write features, implementation approaches, or technology choices
- Do not overwrite an existing product-context.md without declaring delta intent
- Do not conflate product context with project scope — ScopeFrame owns scope
- Do not skip Open Questions — unanswered questions propagated to Interview are better than assumed answers
