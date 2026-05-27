# Information Architecture

## Navigation Depth

Maximum 3 levels deep for primary navigation. Users reach any primary destination in 3 clicks or fewer from the home state. If more than 3 levels are needed, IA requires restructuring — not a deeper nav.

## Labeling

Content labels derived from:
- User research vocabulary (what users call things)
- Domain vocabulary (accepted industry terms)
- Not internal jargon (team names, code names, backend model names)

Every label reviewed against user vocabulary at P1. Technical labels appearing in the UI are flagged for user vocabulary review.

## Search and Filter

Required when content exceeds 20 items in a list or grid:

```markdown
**Search required at:** 20 items
**Filter required at:** 20 items
**Both required at:** 50+ items or multi-dimensional content
```

Threshold declared in spec. At least one of search or filter required at threshold — both not required unless content is multi-dimensional.

## Audit Gates

- [ ] Primary navigation depth <= 3 levels
- [ ] All labels reviewed against user vocabulary (no internal jargon)
- [ ] Search/filter threshold declared in spec
- [ ] Search or filter implemented when content exceeds 20 items
