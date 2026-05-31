# C4 Mermaid Syntax Reference

Mermaid's C4 diagram support maps directly to the C4 model's four levels.

## Supported Shape Types

### People
```
Person(alias, label, description)          # internal person
Person_Ext(alias, label, description)      # external person
```

### Systems
```
System(alias, label, description)          # internal system
System_Ext(alias, label, description)      # external system
System_Db(alias, label, description)       # database system
System_Queue(alias, label, description)    # queue system
```

### Containers
```
Container(alias, label, tech, description)
ContainerDb(alias, label, tech, description)
ContainerQueue(alias, label, tech, description)
```

### Components
```
Component(alias, label, tech, description)
ComponentDb(alias, label, tech, description)
ComponentQueue(alias, label, tech, description)
```

### Boundaries
```
System_Boundary(alias, label) { ... }
Container_Boundary(alias, label) { ... }
Enterprise_Boundary(alias, label) { ... }
```

### Relationships
```
Rel(from, to, label)
Rel(from, to, label, technology)
BiRel(from, to, label)
Rel_Back(from, to, label)
Rel_Neighbor(from, to, label)       # hint: draw adjacent
Rel_D(from, to, label)              # explicit direction: down
Rel_U(from, to, label)              # up
Rel_L(from, to, label)              # left
Rel_R(from, to, label)              # right
```

### Layout hints
```
UpdateLayoutConfig($c4ShapeInRow, $c4BoundaryInRow)
  # e.g. UpdateLayoutConfig("3", "2") — 3 shapes per row, 2 boundaries per row
```

## Level 1 — Context Example

```mermaid
C4Context
  title System Context Diagram
  UpdateLayoutConfig("3", "1")

  Person(developer, "Developer", "Uses Claude Code in the project")
  Person_Ext(ops, "Ops", "Manages deployments")

  System_Boundary(sb, "WabbleSpec") {
    System(wabblespec, "WabbleSpec", "Spec-driven SDLC framework with receipt-gated execution")
  }

  System_Ext(claude, "Claude Code", "AI runtime — executes skills, calls tools")
  System_Ext(git, "Git", "Version control and commit history")

  Rel(developer, wabblespec, "Runs tasks via")
  Rel(ops, wabblespec, "Reviews receipts from")
  Rel(wabblespec, claude, "Delegates execution to")
  Rel(wabblespec, git, "Reads/writes commits")
```

## Level 2 — Container Example

```mermaid
C4Container
  title Container Diagram — WabbleSpec Engine

  Person(developer, "Developer")

  System_Boundary(ws, "WabbleSpec") {
    Container(skills, "Skill Layer (.claude/skills/)", "Markdown+YAML", "117 SKILL.md files loaded on demand by Claude Code")
    Container(engine, "Engine (engine/modules/)", "Python+Markdown", "Canonical module definitions and scripts")
    ContainerDb(state, "State Store (.wabblespec/state/)", "JSON files", "Receipts, session state, memory drawers, wave plans")
    Container(hooks, "Hooks (engine/hooks/)", "Node.js", "SessionStart, UserPromptSubmit, Statusline")
  }

  Rel(developer, skills, "Activates via Claude Code prompts")
  Rel(skills, state, "Reads receipts, writes receipts")
  Rel(engine, skills, "Syncs canonical sources to", "wabblespec-sync-skills.py")
  Rel(hooks, state, "Reads session flag, emits invariant context")
```

## Level 3 — Component Example (Engine Modules)

```mermaid
C4Component
  title Component Diagram — Engine L2 Modules

  Container_Boundary(l2, "L2 Modules (Orchestration)") {
    Component(executor, "executor", "SKILL.md", "Wave execution engine — runs Guard, Apply, Verifier per wave")
    Component(modelRouter, "model-router", "SKILL.md+scripts", "Routes tasks to capability lanes, runs ContextTuner")
    Component(inferenceGuard, "inference-guard", "SKILL.md", "OPSEC noise check before high-risk tool calls")
    Component(reviewer, "reviewer", "SKILL.md", "Peer review gate for SKILL.md authoring quality")
    Component(autopilot, "autopilot", "SKILL.md", "Meta-orchestrator — owns meta.md, manages L0-L4 phases")
    Component(audit, "audit", "SKILL.md", "Security audit gateway for framework changes")
  }

  Rel(autopilot, executor, "Delegates waves to")
  Rel(executor, modelRouter, "Calls before each wave")
  Rel(modelRouter, inferenceGuard, "Signals eligibility to")
  Rel(executor, reviewer, "Invokes for SKILL.md changes")
```

## Common Mistakes

- Alias must be alphanumeric+underscore — no hyphens: use `model_router` not `model-router`
- `Rel` direction follows argument order: `Rel(A, B, label)` draws A → B
- Boundaries must wrap with `{ }` on separate lines — inline is not supported
- `C4Code` level uses class diagram syntax, not C4 shapes
- All strings with spaces must be quoted: `"My Label"` not `My Label`
