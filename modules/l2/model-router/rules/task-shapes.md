# Task Shapes

Task shape classification maps the current wave's work to required capability descriptors.

| Task shape | Required capabilities | Notes |
|---|---|---|
| code | code-generation | Implementation, refactoring, completion |
| review | analysis | Code review, audit, defect detection |
| research | synthesis, analysis | Multi-source information gathering |
| spec | instruction-following, synthesis | Writing structured spec artifacts |
| debug | analysis, reasoning | Root cause investigation |
| plan | reasoning, synthesis | Decomposition, wave planning |
| test | code-generation, analysis | Test generation, test analysis |
| document | synthesis, instruction-following | Documentation generation |
| visual | vision | Any task with image/screenshot input |
| multi-target | code-generation + platform-specific | Task spanning multiple build targets |
| agent | tool-use, reasoning | Agent loop execution |

## Classification rules

1. Read the current wave declaration from Decompose output
2. Match wave outputs and acceptance criteria to task shapes
3. If wave has mixed outputs (code + docs), select the dominant shape
4. If equally mixed: use `multi-target` shape — may trigger Ensemble

## Fallback selection

For each task shape, fallback capability is the next-highest confidence capability that partially covers the task:

| Primary capability | Fallback |
|---|---|
| code-generation | synthesis (for documentation-heavy waves) |
| reasoning | analysis |
| synthesis | instruction-following |
| vision | none — declare unavailable |
| embedding | none — declare unavailable |
