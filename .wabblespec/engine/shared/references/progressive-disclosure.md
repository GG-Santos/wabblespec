# Progressive Disclosure

Index-first retrieval and on-demand hydration patterns. Prevents context flooding. Consumers: memory-search, nexus, reference-load, explore.

## Pattern

Load a summary (index card) first. Load the full content only if the summary is insufficient for the current decision.

### Three-level retrieval

**Level 1 — Index** (always load)
A one-line summary or project-map card. Answers "does this exist and is it relevant?" without loading content.

**Level 2 — Summary** (load if Level 1 indicates relevance)
Key facts, decisions, and constraints from the artifact. 200–500 tokens. Answers "what does this say?" without loading the full text.

**Level 3 — Full content** (load only if Level 2 is insufficient)
The complete file. Required when: the exact wording matters (EARS requirements, schema fields, receipt contracts), the question requires reasoning over the whole document.

## Implementation by module

### Memory-Search
- Level 1: drawer topic + tags (always in response)
- Level 2: drawer body excerpt (load if query matches Level 1)
- Level 3: full drawer (load only if Level 2 excerpt doesn't answer query)

### Nexus
- Level 1: graph node label + drawer_count
- Level 2: drawer topics for connected nodes
- Level 3: specific drawer bodies (only for evidence chain)

### ReferenceLoad
- Level 1: project-map card (always load first)
- Level 2: section headings and summary paragraphs
- Level 3: full file content (only if section-level is insufficient)

### Explore
- Level 1: file paths matching glob
- Level 2: first 50 lines of matched files
- Level 3: full file (only if 50-line excerpt doesn't answer question)

## Hydration rules

Load Level 3 only when:
- The exact text (not its meaning) is required
- The decision cannot be made from the summary
- A quoted constraint or requirement must be verified verbatim

Do not load Level 3:
- To "be thorough" — thoroughness from summaries is sufficient for most decisions
- To verify a belief already confident from Level 2
- Speculatively — load when needed, not before

## Anti-patterns

| Anti-pattern | Cost | Fix |
|---|---|---|
| Loading all files in scope | Context flood — signal buried in noise | Load index, then by relevance |
| Loading full file when a section answers the question | Wasted context tokens | Request specific section by heading |
| Hydrating every search result | 10× context use for 1× improvement | Load top 2 results fully, skim rest |
| Re-loading context from a prior turn | Wasted tokens — already in context | Reference by path, do not re-load |
