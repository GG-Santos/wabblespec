# Cold-Start Behavior — Research Log

Defines what Research Log does when its storage directory or spec binding are absent.

## Absent: research/ directory

Condition: `research/` directory does not exist.
Detection: Directory read returns 404.
Action: Create `research/` on first write. This is normal on fresh projects.
Do NOT: Fail because the directory is absent — creating it is the expected behavior.

## Absent: spec binding

Condition: Research log invoked without a `spec_binding` (no link to the spec this research supports).
Detection: No spec ID or spec path in invocation.
Action: Log research to `research/general/research.md` (unbound). Surface to user: "No spec binding declared — logging to research/general/. Bind to a spec with spec_binding=<spec-id> to associate this research."
Do NOT: Block the log. Unbound research is valid.

## Absent: prior research for this spec binding

Condition: `research/[slug]/research.md` does not exist for the declared spec binding.
Detection: File read returns 404.
Action: Create the file with the current research entry as the first entry.

## Absent: web search capability

Condition: Research log invoked but web search tools are unavailable.
Detection: Search tool returns unavailable.
Action: Log: "Web search unavailable — logging offline research notes only. Mark entries with source: offline."
Do NOT: Fabricate research results.

## Default state on cold start

| Field | Default |
|---|---|
| `spec_binding` | null — unbound unless declared |
| `output_path` | `research/[slug]/research.md` if bound; `research/general/research.md` if unbound |
| `entry_format` | Timestamped entries with source, query, and findings |
| `verified_only` | true — only log verified facts; mark uncertain claims as [UNVERIFIED] |
| `max_entries_per_session` | No limit, but each entry must have a distinct question/query |
