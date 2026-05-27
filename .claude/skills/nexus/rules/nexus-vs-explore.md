# Nexus vs Explore

When a question can be answered by reading the current codebase, use Explore. When it requires reasoning across time, sessions, or the Memory graph, use Nexus.

## Use Explore when

- The answer is in current files: a function signature, a config value, an import path
- The question is "where is X defined?" or "which files use Y?"
- No cross-session knowledge is needed
- Memory has fewer than 10 drawers (Nexus graph has insufficient density)

## Use Nexus when

- "Why was X designed this way?" — requires decision history across sessions
- "What will break if I change Y?" — blast radius through module dependency graph
- "Have we seen this problem before?" — pattern matching across historical sessions
- "What changed in area Z recently?" — multi-session change timeline
- The question spans more than one module and more than one session
- Explicit `/nexus` command

## Boundary test

Ask: "Could a developer answer this by reading only the current files open in their editor?"

- Yes → Explore
- No (requires knowledge of past decisions, cross-session history, or module relationships not visible in code) → Nexus

## Never use Nexus when

- Memory has 0–9 drawers: graph too sparse, traversal produces noise
- The question is purely implementation: "How do I implement X?" — that is Executor's domain
- The codebase is fresh and has no history to traverse
