# AgentSkills Format

agentskills.io-compatible output formatting rules.

## Overview

agentskills.io uses a structured markdown format for skill documentation. Markdown module outputs targeting agentskills must comply with this format to render correctly on the platform.

## Required document structure

```
# {Skill Name}

{One-paragraph description of what the skill does.}

## Inputs

{Describe each input parameter in a consistent format.}

## Steps

{Numbered or headed workflow steps.}

## Output

{Describe the output artifact.}
```

## Link format

agentskills does not render Obsidian wikilinks. Convert all `[[target]]` to standard markdown hyperlinks with relative paths:

`[Target Title](./target-filename.md)`

For cross-skill references in the same vault: use relative paths from the skill's directory.

## Frontmatter handling

agentskills does not render YAML frontmatter — strip it from the output or move it to an HTML comment block at the bottom of the file.

## Code blocks

Same fenced code block convention as Obsidian — language specifier required.

## Callouts

agentskills does not support Obsidian callout syntax. Convert callouts to bolded paragraphs:

Obsidian: `> [!WARNING] Title\n> content`
agentskills: `**Warning — Title:** content`

## Images

agentskills uses standard markdown image syntax with alt text required:
`![Descriptive alt text](./path/to/image.png)`

Image dimensions are declared in the alt text using a trailing dimension hint when needed:
`![Diagram of workflow (800×400)](./workflow.png)`
