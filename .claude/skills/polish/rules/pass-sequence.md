# Polish — Pass Sequence

Passes run in order. Earlier passes do not depend on later ones. A declared subset runs only the specified passes.

| Pass | Name | Scope | Blocks on failure? |
|---|---|---|---|
| 1 | Register enforcement | Register consistency per Homowabian state | Yes — fix before proceeding |
| 2 | Redundancy removal | Repeated content, filler, empty headers | Yes — fix before proceeding |
| 3 | Structural consistency | Tables, code blocks, heading hierarchy, internal links | Yes — fix before proceeding |
| 4 | Spec compliance | Prose claims vs. spec artifacts, canonical names, deprecated terms | No — flag only |
| 5 | Proofread | Readability, factual accuracy, internal consistency (via Proofread module) | No — findings surfaced; verdict propagated |
| 6 | Markdown formatting | Obsidian/agentskills format, frontmatter, wikilinks, callouts (via Markdown module) | No — auto-applied; non-destructive |

Passes 5 and 6 are optional. They activate when:
- Pass 5 (Proofread): caller declares `--proofread` flag, OR artifact content type is one of `technical-doc | marketing-copy | legal-doc | blog-post`
- Pass 6 (Markdown): caller declares `--markdown` flag, OR artifact target is an Obsidian vault path

## Declaring a subset

Caller can declare a specific pass: `/polish <artifact> --pass 3` runs Pass 3 only. All passes run by default when no subset is declared.

`/polish <artifact> --proofread --markdown` runs all 6 passes.
`/polish <artifact> --pass 1,2,3` runs only passes 1, 2, and 3.

## Pass 1 priority override

Regardless of active Homowabian register, Pass 1 enforces normal register on:
- Security warnings
- Irreversible action confirmations
- Attestation content

These sections cannot use lite, full, or ultra compression — only normal.

## Pass 4 severity

Pass 4 flags violations in the diff record. It does not change the polished artifact for spec compliance issues — human review required. This matches the principle that spec corrections require human attestation, not automated rewrite.
