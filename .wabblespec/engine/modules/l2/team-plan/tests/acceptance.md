# TeamPlan — Acceptance Criteria

## BLOCK: complexity below L4

Given Recipe declares complexity below L4 (High — multi-system),
When TeamPlan is considered for activation,
Then TeamPlan does not activate.
Then single-agent Executor handles execution.
Then no TeamPlan receipt is written.

## BLOCK: single-agent not validated first

Given the task class has not been attempted in single-agent mode,
When TeamPlan activation is requested,
Then TeamPlan blocks and surfaces: "TeamPlan requires single-agent execution to be validated first for this task class."
Then TeamPlan does not activate until single-agent has been attempted and found insufficient.

## BLOCK: no explicit activation request

Given TeamPlan is not explicitly requested by the user or Autopilot command,
When TeamPlan is considered,
Then TeamPlan does not self-activate.
Then Autopilot only activates TeamPlan when complexity > 0.9 AND explicit command is present.

## Happy path: activation requirements met

Given Recipe declares L4 complexity, single-agent was validated and found insufficient, and explicit activation is present,
When TeamPlan activates,
Then Orchestrator reads the Decompose receipt as the wave breakdown source of truth.
Then Orchestrator assigns wave clusters to specialist agents.
Then each specialist receives: task context, their wave cluster, and all upstream receipts.

## Orchestrator validates each receipt before unblocking next specialist

Given a specialist completes a wave and writes a receipt,
When Orchestrator validates the receipt,
Then Orchestrator checks the receipt before unblocking the next specialist.
Then if the receipt is FAIL, Orchestrator surfaces to human — it does not silently reassign.
Then if the receipt is PARTIAL, Orchestrator triggers Reviewer for that wave before proceeding.
Then if no receipt is produced, the wave is treated as HARD FAIL.

## Receipt chain continuity

Given multiple specialist agents run under TeamPlan,
When each agent writes receipts,
Then all receipts are written to the same `.wabblespec/receipts/` directory as single-agent execution.
Then the receipt chain has no gaps between agents.
Then TeamPlan does not create a separate receipt chain.

## Handoff format completeness

Given Orchestrator delegates to a specialist,
When the handoff is issued,
Then the handoff contains: task spec card (from Specify receipt), wave cluster assignment, all upstream receipts, and an explicit statement of what the agent must produce to unblock the next agent.
Then no handoff is issued without all four elements.

## Communication breakdown recovery

Given a communication breakdown occurs between Orchestrator and a specialist,
When Orchestrator recovers,
Then Orchestrator re-reads the last valid receipt and re-delegates.
Then Orchestrator does not abandon the wave without surfacing the failure to human.

## Parallelism benefit gate

Given the task bottleneck is analysis speed rather than parallelism,
When TeamPlan evaluates activation,
Then TeamPlan does not activate — the overhead exceeds the benefit.
Then the user is informed that single-agent is sufficient.

## Do NOT

Given any TeamPlan run,
Then TeamPlan does not execute waves directly — it delegates to specialists.
Then TeamPlan does not silently re-try a FAIL specialist receipt without human guidance.
Then TeamPlan does not produce separate receipt chains outside `.wabblespec/receipts/`.
Then TeamPlan does not activate for Medium or Low complexity tasks.
Then TeamPlan does not activate when coordination overhead exceeds parallelism benefit.

## Missing-rules fallback

Given `rules/` directory or role definitions are absent,
When TeamPlan is activated,
Then TeamPlan derives roles from the Decompose receipt wave structure.
Then TeamPlan logs: "Role definitions absent — deriving from Decompose receipt wave clusters."

## Receipt fields

Given any successful TeamPlan run,
Then a final TeamPlan receipt is written to `.wabblespec/receipts/` after all waves complete.
Then the receipt contains: orchestrator identity, total agents coordinated, waves completed, waves failed, receipt chain integrity status.
