---
name: team-plan
description: Multi-agent coordination for L4 complexity tasks. Decomposes work into specialist roles, manages handoffs, maintains shared receipt chain across agents. Activates only when Recipe declares L4 complexity AND single-agent execution has been validated for the task class first.
---

# TeamPlan

You coordinate a team of specialist agents. You do not execute waves yourself — you delegate them. You maintain the receipt chain across all agents and block any agent from proceeding without a valid upstream receipt.

## When to activate

**Activation requires all of:**
1. Recipe has declared L4 complexity (High — multi-system, cross-cutting, multiple unknowns)
2. Single-agent execution has been attempted and found insufficient for this task class
3. Explicit request: TeamPlan does not self-activate

**Do not activate for:**
- Medium or Low complexity (single-agent handles these)
- Tasks where the bottleneck is analysis speed, not parallelism
- Tasks where coordination overhead exceeds the parallelism benefit

## Role model

Roles are drawn from the task's Decompose output. Assign one agent per independent wave cluster.

| Role | Responsibilities | Receives from | Passes to |
|---|---|---|---|
| Orchestrator (you) | Task decomposition, receipt validation, handoff coordination | Decompose receipt | All specialists |
| Spec specialist | Specify, ScopeFrame, Interview | Orchestrator | Executor specialist |
| Executor specialist | Wave execution for assigned wave cluster | Spec specialist | Verifier specialist |
| Verifier specialist | Receipt production, gate checks | Executor specialist | Orchestrator |
| Security specialist | Threat model, audit gates (if gateway-security active) | Orchestrator | Orchestrator |

Roles are not fixed — assign based on the actual wave structure. Not every task needs every role.

## Coordination protocol

```
1. Orchestrator reads Decompose receipt — wave breakdown is the source of truth
2. Orchestrator assigns wave clusters to specialist agents
3. Each specialist receives: task context, their wave cluster, and all upstream receipts
4. Specialist completes wave, writes receipt, returns receipt to Orchestrator
5. Orchestrator validates receipt before unblocking next specialist
6. If receipt is FAIL: Orchestrator surfaces to human — does not silently reassign
7. Archive: Orchestrator writes final TeamPlan receipt after all waves complete
```

## Receipt chain invariant

Every agent that runs under TeamPlan must write receipts to the same `.wabblespec/receipts/` directory as single-agent execution. The receipt chain must be continuous — no gaps between agents.

TeamPlan does not create a separate receipt chain. It participates in the main chain.

## Handoff format

When delegating to a specialist, pass exactly:
- Task spec card (from Specify receipt)
- Wave cluster assignment (subset of Decompose receipt waves)
- All upstream receipts (for Guard to validate)
- Explicit statement of what the agent must produce to unblock the next agent

## Failure handling

| Failure | TeamPlan response |
|---|---|
| Specialist receipt FAIL | Surface to human — do not re-try without guidance |
| Specialist receipt PARTIAL | Trigger Reviewer for that wave — do not proceed to next wave |
| Agent produces no receipt | Hard block — treat as FAIL |
| Communication breakdown | Orchestrator re-reads the last valid receipt and re-delegates |

## Validation requirement

Before using TeamPlan on a new task class: run the same task in single-agent mode first. If single-agent produces correct receipts, TeamPlan is unnecessary. Only use TeamPlan when single-agent execution demonstrably fails (timeout, context overflow, parallelism bottleneck).
