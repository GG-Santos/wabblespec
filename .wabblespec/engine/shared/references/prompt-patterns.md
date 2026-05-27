# Prompt Failure Patterns

35 named patterns across 6 categories. Factory checks all SKILL.md workflow sections against these before promotion. Each pattern includes: symptom, detection signal, fix.

---

## Category 1: Task Patterns (T)

### T1 — Goal Inflation
**Symptom:** Instruction describes multiple deliverables as one task.
**Detection:** Goal sentence contains "and" connecting two distinct outcomes.
**Fix:** Split into separate task cards, one per deliverable.

### T2 — Implicit Precondition
**Symptom:** Module assumes upstream artifact exists without checking.
**Detection:** SKILL.md workflow reads a file without a "check existence" step first.
**Fix:** Add explicit precondition check; surface DEPENDENCY error if absent.

### T3 — Scope Creep Invite
**Symptom:** Instruction ends with "and anything else that seems relevant."
**Detection:** Open-ended scope language in "when to use" or trigger conditions.
**Fix:** Replace open scope with explicit enumeration of what is and is not in scope.

### T4 — Negative Goal
**Symptom:** Goal stated as what NOT to do rather than what to produce.
**Detection:** Goal sentence contains "don't", "avoid", "prevent" without a positive outcome.
**Fix:** Restate as positive outcome. "Avoid X" → "Produce Y that does not contain X."

### T5 — Missing Failure Path
**Symptom:** Workflow only describes happy path; no error handling declared.
**Detection:** No "if ... then emit [error type]" branches in workflow steps.
**Fix:** Add explicit error branches per error-taxonomy.md for each step that can fail.

### T6 — Unbounded Iteration
**Symptom:** Workflow loop has no stated termination condition.
**Detection:** "Repeat until done" or "continue until complete" without defined done condition.
**Fix:** Declare max iterations, exit condition, or escalation path if condition not met.

---

## Category 2: Context Patterns (C)

### C1 — Evidence-Free Assertion
**Symptom:** Module output states facts without citing source artifacts.
**Detection:** SKILL.md output section makes claims without referencing drawer IDs or file paths.
**Fix:** Every factual claim must cite a drawer ID, file path, or receipt.

### C2 — Stale Context Loading
**Symptom:** Module loads all context upfront regardless of task.
**Detection:** "Load all [X] files before beginning" instruction in SKILL.md.
**Fix:** Load only what the current wave declares. Reference Economy placement rules.

### C3 — Context Pollution
**Symptom:** Module mixes constraints, references, and active task in arbitrary order.
**Detection:** Workflow does not follow Constraints → References → Active Task placement.
**Fix:** Restructure context assembly per Economy placement rules (constraints top, task end).

### C4 — Missing Not-Tested Declaration
**Symptom:** Module claims completion without declaring what could not be verified.
**Detection:** Output contract has no `not_tested` field; receipt schema lacks it.
**Fix:** Add `not_tested` array to receipt schema and output contract.

### C5 — Unsourced Default
**Symptom:** Module uses a default value without declaring its source or justification.
**Detection:** Hardcoded values (timeouts, thresholds, counts) with no citation in SKILL.md.
**Fix:** Cite source for each default; make overridable via declared config.

### C6 — Trust Level Omission
**Symptom:** External reference loaded without declared trust level.
**Detection:** ReferenceLoad call in workflow with no HIGH/MEDIUM/LOW declaration.
**Fix:** Declare trust level at load time per reference-load trust level table.

---

## Category 3: Format Patterns (F)

### F1 — Prose Where Table Needed
**Symptom:** Structured comparison presented as running prose.
**Detection:** Three or more parallel items described in consecutive sentences without a table.
**Fix:** Convert to table with consistent columns.

### F2 — Missing Language Identifier
**Symptom:** Code block has no language identifier.
**Detection:** Fenced code block opens with ``` only, no language tag.
**Fix:** Add language identifier: ```json, ```python, ```yaml, etc.

### F3 — Heading Hierarchy Skip
**Symptom:** Document jumps from H2 to H4, skipping H3.
**Detection:** Heading level increases by more than 1 in a single step.
**Fix:** Insert intermediate heading level; restructure content hierarchy.

### F4 — Trailing Summary Repetition
**Symptom:** Section ends with a paragraph that restates what was just said.
**Detection:** Last paragraph of a section begins with "In summary," "To recap," "As noted above."
**Fix:** Remove trailing summary. Let the content speak. If summary needed, move to top.

### F5 — Empty Section Header
**Symptom:** Section header exists but section body is empty or says "TBD."
**Detection:** Header followed by nothing or by "TBD"/"TODO"/"Coming soon."
**Fix:** Fill section or remove header. Placeholder headers signal incomplete spec.

### F6 — Ambiguous Pronoun Reference
**Symptom:** "It", "this", "they" reference unclear antecedent in technical instruction.
**Detection:** Pronoun appears in a step instruction where the referent could be multiple things.
**Fix:** Replace pronoun with explicit noun: "the receipt" not "it", "the module" not "this."

---

## Category 4: Scope Patterns (S)

### S1 — Authority Boundary Absent
**Symptom:** Module SKILL.md does not declare what files it can and cannot write.
**Detection:** No "writes" / "never writes" section in SKILL.md or skill-rules.json.
**Fix:** Add explicit write authority declaration to skill-rules.json.

### S2 — Scope Collapse
**Symptom:** Module takes on responsibilities belonging to a downstream module.
**Detection:** SKILL.md describes actions that match another module's authority (e.g., Specify writing code).
**Fix:** Remove out-of-scope steps; add handoff instruction to correct module.

### S3 — Over-narrow Trigger
**Symptom:** Module never activates because trigger condition is too specific.
**Detection:** skill-rules.json trigger requires exact file name or exact phrase that never appears.
**Fix:** Broaden trigger to pattern match or capability signal; test against real inputs.

### S4 — Self-Verification
**Symptom:** Module verifies its own output rather than routing to Verifier.
**Detection:** SKILL.md says "verify that the output is correct" as a final step owned by the module itself.
**Fix:** Replace with "write receipt and route to Verifier." Modules do not self-verify.

### S5 — Silent Scope Expansion
**Symptom:** Module quietly expands scope mid-execution without declaring the expansion.
**Detection:** Workflow step says "if you notice X while doing Y, also fix X."
**Fix:** Replace with explicit error route: surface as SPEC_VIOLATION, do not silently expand.

### S6 — Missing Boundary Condition
**Symptom:** Module handles the happy path but not the boundary (empty input, null, zero).
**Detection:** Workflow steps have no branch for empty/null/zero inputs.
**Fix:** Add explicit boundary handling step for each workflow input.

---

## Category 5: Reasoning Patterns (R)

### R1 — Confidence Without Evidence
**Symptom:** Module output states high confidence claim with no cited evidence.
**Detection:** confidence field > 0.7 with no evidence_files or drawer_refs populated.
**Fix:** Confidence must match evidence quality. No evidence = confidence ≤ 0.4.

### R2 — Circular Dependency
**Symptom:** Module A depends on Module B which depends on Module A.
**Detection:** framework.yaml depends_on graph has a cycle.
**Fix:** Break cycle by introducing a shared artifact or restructuring dependency direction.

### R3 — Inference Passed as Fact
**Symptom:** Module presents inferred conclusions as verified facts in output.
**Detection:** Output uses "is", "has", "contains" for things that were inferred, not read from files.
**Fix:** Use hedged language for inferences: "appears to", "likely", "based on X." Or verify before asserting.

### R4 — Contradiction Suppression
**Symptom:** Module encounters contradicting evidence and silently picks one version.
**Detection:** No contradiction_with field populated when two drawers disagree on same topic.
**Fix:** Flag contradiction explicitly. Route to Dream for resolution. Do not silently resolve.

### R5 — Threshold Without Calibration
**Symptom:** Module uses a numeric threshold (confidence > 0.8, score < 3) with no stated calibration basis.
**Detection:** Threshold value appears in SKILL.md with no "calibrated from" or "derived from" note.
**Fix:** Document threshold source. If arbitrary, flag as provisional and note what would calibrate it.

### R6 — Premature Conclusion
**Symptom:** Module produces a final verdict before processing all inputs.
**Detection:** Workflow step writes receipt before all workflow steps are complete.
**Fix:** Move receipt write to final step, after all evidence is gathered and checked.

---

## Category 6: Agentic Patterns (A)

### A1 — Missing Human Gate
**Symptom:** Irreversible action (delete, deploy, promote) executed without Attestation.
**Detection:** SKILL.md action touches irreversible operations with no Attestation step.
**Fix:** Insert Attestation verification mode before any irreversible action (I3).

### A2 — Unbounded Tool Call
**Symptom:** Module calls a tool with no declared maximum invocation count or scope limit.
**Detection:** Workflow loop calls tool without max_iterations or stop condition.
**Fix:** Declare max invocations; emit CONTEXT_EXHAUSTION error if limit reached.

### A3 — Spawn Without Scope
**Symptom:** Module spawns a sub-agent without declaring the sub-agent's authority boundary.
**Detection:** Spawn instruction has no cannot_touch list and no explicit scope.
**Fix:** All spawned sub-agents must have cannot_touch declarations and explicit scope (I11, TeamPlan).

### A4 — Receipt Chain Gap
**Symptom:** Module advances to next phase without checking upstream receipt.
**Detection:** Workflow step begins execution without "check upstream receipt exists" as first step.
**Fix:** Add upstream receipt check as step 0. DEPENDENCY error if absent (I10).

### A5 — Rollback Omission
**Symptom:** Destructive wave has no rollback checkpoint declared.
**Detection:** Wave plan touches destructive operations (schema migration, file deletion, deploy) with no checkpoint.
**Fix:** Add rollback checkpoint before every destructive operation (I4 — verification gates everything).

### A6 — Context Window Ignore
**Symptom:** Module does not check or manage context budget during long operations.
**Detection:** Long workflow with no Economy compression or CONTEXT_EXHAUSTION error route.
**Fix:** Add context budget check at each major step; emit CONTEXT_EXHAUSTION at 90% threshold.

### A7 — Self-Modification Without Double Attestation
**Symptom:** Evolution module modifies its own SKILL.md or skill-rules.json without double Attestation.
**Detection:** Forge promotion targets an Evolution module without two separate Attestation events.
**Fix:** Require double Attestation for self-modification (I8 self-modification rule).
