# Defect Patterns

Named defect patterns for Guard, Reviewer, and Triage. Each pattern includes symptom, detection method, fix-forward path, and test anchor.

Referenced by: `modules/l2/guard/rules/`, `modules/l2/reviewer/rules/`, `modules/l1/triage/rules/`

---

## DP-01 — Port Drift

**Symptom:** A value, constant, or config originally declared in module A is re-declared independently in module B, causing divergence over time.

**Detection:** Two or more files declare the same semantic constant with different values; or a module reads a config key that another module writes without going through the owner.

**Fix-forward:** Delete the duplicate. Route all reads through the canonical owner declared in `state-protocol.md`.

**Test anchor:** Grep all files for the constant name; count should be 1 (definition) + N (reads). Any additional definition is DP-01.

---

## DP-02 — State Trample

**Symptom:** Module B overwrites state written by module A without authority, causing A's output to be lost.

**Detection:** A state file's `exclusive writer` (per `state-protocol.md`) is not the last commit author for that file path. Or two receipts claim to have written the same field in the same artifact.

**Fix-forward:** Remove unauthorized write from B. Route through A's write path or the owning module.

**Test anchor:** `state-protocol.md` exclusive writer list vs. actual file-write operations in wave receipts.

---

## DP-03 — Receipt Orphan

**Symptom:** A receipt exists in `.wabblespec/state/receipts/` with no corresponding task card entry or wave it belongs to.

**Detection:** Receipt filename does not match any wave ID or task slug in the active task card. Or receipt `task_id` field references a deleted task.

**Fix-forward:** Archive the orphan receipt to `_archive/orphaned-receipts/`. Do not delete — Provenance ledger may reference it.

**Test anchor:** Join receipt filenames against task card wave list. Unmatched receipts = orphans.

---

## DP-04 — Scope Creep Silent

**Symptom:** A wave modifies files outside the declared scope without triggering a SPEC_VIOLATION, because the scope check was skipped or the file wasn't listed in scope.md out-of-scope.

**Detection:** Post-wave diff includes files not listed in `scope.md` in-scope section. Guard Layer 2 receipt shows SKIP.

**Fix-forward:** Add explicit out-of-scope entries for files that must not be touched. Re-run Guard Layer 2.

**Test anchor:** Diff wave output against `scope.md` in-scope list. Any non-matching write path = DP-04.

---

## DP-05 — Cascade Blind

**Symptom:** A change in a low-layer module (L0–L1) breaks a high-layer module (L5–L8) that depends on it, but no downstream check catches it because integration tests only cover the immediate output.

**Detection:** Verifier or Reviewer finds a high-layer module output inconsistent with a low-layer module's changed contract.

**Fix-forward:** Add a cross-layer invariant check. Trace the changed contract through all downstream consumers in `framework.yaml`.

**Test anchor:** Module dependency graph (from `framework.yaml` `depends_on` fields). Walk dependents after any L0–L2 change.

---

## DP-06 — Authority Leak

**Symptom:** A module writes to a file it does not own (per `skill-rules.json` `authority.owns`), either directly or by injecting content through a shared utility.

**Detection:** Guard Layer 4 HARD error. Or post-wave audit finds a file modified whose declared owner is a different module.

**Fix-forward:** Move write to the owning module. If the writing module needs to influence the file, it submits a change request to the owner.

**Test anchor:** `skill-rules.json` `authority.owns` vs. actual file writes in wave receipt. Any write outside owns list = DP-06.

---

## DP-07 — Staleness Blindness

**Symptom:** A module uses evidence (research, receipts, prior outputs) past its declared TTL without flagging it as EXPIRED, producing outputs based on stale data.

**Detection:** Guard Layer 3 I9 check. Or Reviewer finds a receipt `evidence_expires_at` timestamp in the past.

**Fix-forward:** Quarantine the expired evidence. Re-run the producing module to refresh it before proceeding.

**Test anchor:** All `evidence_expires_at` fields in wave inputs vs. current timestamp. Any past timestamp = DP-07.

---

## DP-08 — Ground Skip

**Symptom:** A module's output contains hallucinated file paths, function names, or API signatures that do not exist in the project, because Ground validation was not run.

**Detection:** Ground module cross-reference check fails post-execution. Or Reviewer finds references to non-existent symbols.

**Fix-forward:** Run Ground on the output. Replace hallucinated references with verified ones or mark as NEEDS_VERIFICATION.

**Test anchor:** Ground receipt `hallucination_count` > 0. Any non-zero count after a wave = DP-08.

---

## DP-09 — Drift Inversion

**Symptom:** A module designed to detect drift (Provenance, reverse-drift-detector) produces a clean result when drift is present, because its reference baseline is itself out of date.

**Detection:** Provenance ledger shows no drift events despite a known change that should trigger one. Reverse-drift-detector baseline file predates the change.

**Fix-forward:** Refresh the baseline file. Re-run the detector. If detector logic is wrong, escalate to Reviewer.

**Test anchor:** Provenance ledger entry timestamps vs. last known change timestamp. Baseline older than change = DP-09.

---

## DP-10 — Spec Inflation

**Symptom:** A spec document grows to include implementation details, rationale, and edge cases that belong in code comments or ADRs, making it too large to validate and too slow to parse.

**Detection:** Guard Layer 3 I12 check (criteria count exceeds complexity threshold). Or Reviewer flags spec document exceeding size limit.

**Fix-forward:** Strip implementation detail from spec. Move rationale to ADR. Keep spec to declarative requirements only.

**Test anchor:** Criteria count per task card stage vs. I12 threshold. Any stage exceeding threshold = DP-10.

---

## DP-11 — Wave Sequence Break

**Symptom:** Wave N executes before Wave N-1's receipt is written, breaking the I10 chain guarantee.

**Detection:** Guard Layer 3 I10 check fails. Prior wave receipt missing in `.wabblespec/state/receipts/`.

**Fix-forward:** Pause execution. Recover Wave N-1 receipt or re-run Wave N-1.

**Test anchor:** Receipt filenames in `.wabblespec/state/receipts/` form an unbroken sequence 0…N-1 before Wave N runs.

---

## DP-12 — Cold-Start Assumption

**Symptom:** A module assumes its expected upstream artifacts exist (recipe.json, specs/, AGENT.md) and proceeds without them, producing undefined behavior on first run.

**Detection:** Module output contains null or placeholder values. Or module errors mid-run when a file read returns 404.

**Fix-forward:** Apply cold-start policy from the module's `rules/cold-start.md`. Either detect from scratch or surface DEPENDENCY error.

**Test anchor:** Remove upstream artifact. Run module. Module must either recover gracefully or return a typed DEPENDENCY error.

---

## DP-13 — Misactivation

**Symptom:** A module activates on a project type it was not designed for (e.g., a game module activates on a CLI project) because Recipe selected it based on a generic `["ALL"]` activator.

**Detection:** Guard Layer 4 `misactivation_risk: true` warning (file_path_patterns produced no matches on wave files).

**Fix-forward:** Narrow the module's `file_path_patterns` in `skill-rules.json`. Or deactivate it for this recipe target.

**Test anchor:** Module `skill-rules.json` `file_path_patterns` vs. actual project file list. Zero matches = DP-13 risk.

---

## DP-14 — Receipt Schema Drift

**Symptom:** A module writes a receipt with fields that no longer match the base receipt schema or the module's declared extension schema, causing downstream consumers to silently ignore required fields.

**Detection:** Guard Layer 1 schema validation failure on receipt fields. Or Verifier finds missing expected fields in receipts.

**Fix-forward:** Update the module's receipt writer to match current schema. Run schema validation on all existing receipts.

**Test anchor:** Validate all receipts in `.wabblespec/state/receipts/` against `.wabblespec/engine/shared/schemas/base-receipt.schema.json` + module extension schema.

---

## DP-15 — Complexity Undercount

**Symptom:** Recipe declares Low complexity for a task that requires 3+ integration points, causing collapse_eligible: true and skipping a necessary review cycle.

**Detection:** Post-execution Verifier finds integration failures that would have been caught by a Guard + Reviewer cycle.

**Fix-forward:** Re-run Recipe with corrected complexity. Invalidate the collapsed execution. Re-run with full cycle.

**Test anchor:** Integration point count in task card vs. complexity threshold table in Recipe SKILL.md.

---

## DP-16 — Authority Matrix Stale

**Symptom:** A new module is added without updating its `skill-rules.json` authority declaration, causing Guard to block it with a HARD error on first use.

**Detection:** Guard Layer 4 HARD error: "Module has no skill-rules.json".

**Fix-forward:** Create or update `skill-rules.json` with `authority.owns` for the module. Register module in `framework.yaml`.

**Test anchor:** All entries in `framework.yaml` `modules` list have a corresponding `skill-rules.json` file. Any missing = DP-16.

---

## DP-17 — Provenance Gap

**Symptom:** A change is applied to the project without a corresponding Provenance ledger entry, making it impossible to trace the change's origin.

**Detection:** `git diff` shows changes not referenced in `ledger.md`. Or Archive receipt references a wave with no ledger entry.

**Fix-forward:** Add a retroactive ledger entry with best-available evidence. Flag as RECONSTRUCTED.

**Test anchor:** Every wave receipt ID appears in `ledger.md` within 24 hours of the wave completing.

---

## DP-18 — Invariant Override

**Symptom:** A module explicitly bypasses an invariant (I1–I12) by setting a flag or ignoring the check, producing a technically-passing result that violates the system contract.

**Detection:** Reviewer finds `skip_invariant` flags or guard receipts with invariants listed as SKIP rather than PASS.

**Fix-forward:** Remove the override. Fix the underlying condition that made the invariant inconvenient. Escalate to Reviewer if invariant needs formal amendment.

**Test anchor:** Guard receipts must not contain any invariant result of SKIP. Only PASS or typed-error are valid.

---

## DP-19 — Dream Decay Overcorrect

**Symptom:** Dream's decay function reduces tracker.json weights too aggressively on a pattern that appeared idle, causing Instinct to stop surfacing a valid recurring pattern.

**Detection:** Instinct receipt shows a known pattern as absent. tracker.json weight for that pattern has dropped below activation threshold despite recent activity.

**Fix-forward:** Inspect Dream's decay log. If the pattern had activity within its expected recurrence window, restore weight manually and adjust decay rate.

**Test anchor:** tracker.json weight vs. pattern recurrence period. Weight should not drop below 0.2 for patterns with activity in the last 2× recurrence period.

---

## DP-20 — Spec Binding Miss

**Symptom:** Research-log writes a session-level receipt but no feature-scoped `research/{feature-slug}/research.md`, because `spec_binding` was present but the feature-slug extraction failed silently.

**Detection:** Research-log receipt shows `spec_binding` populated but no corresponding file under `research/`.

**Fix-forward:** Re-derive feature-slug from `spec_binding.spec_artifact_path`. Write the missing file. Update INDEX.md.

**Test anchor:** Any receipt with `spec_binding` populated must have a corresponding `research/{slug}/research.md` file.

---

## DP-21 — Benchmark Metric Without Outcome

**Symptom:** A Benchmark eval case declares metrics (accuracy, latency, precision) without first declaring the developer outcome being measured, making the metric uninterpretable.

**Detection:** Benchmark rules/outcome-requirement.md check. Eval case lacks `outcome` field.

**Fix-forward:** Add `outcome: "Did [X] produce [Y result] for [who]?"` to the eval case before any metric claim.

**Test anchor:** All eval cases in Benchmark runs must have `outcome` field populated. Missing = DP-21 SPEC_VIOLATION.

---

## DP-22 — Model Name Leak

**Symptom:** A wave input, receipt, or task card contains a specific model name (e.g., "claude-sonnet-4-6") instead of a capability descriptor (e.g., "high-reasoning"), violating I6.

**Detection:** Guard Layer 3 I6 check. Or Grep for known model name patterns in wave inputs.

**Fix-forward:** Replace model name with the appropriate capability descriptor from `runtime-state.json`.

**Test anchor:** Grep all wave inputs for model name patterns. Zero matches required.

---

## DP-23 — Rollback Without Worktree

**Symptom:** Rollback executes against the main working tree instead of an isolated worktree, risking corruption of uncommitted changes if rollback fails mid-operation.

**Detection:** Rollback receipt shows `worktree_path` as null or equal to the main project path.

**Fix-forward:** Re-run Rollback with worktree isolation per `modules/l2/rollback/rules/worktree-policy.md` Type 4.

**Test anchor:** Rollback receipt `worktree_path` must differ from project root for any Type 3 or Type 4 operation.

---

## DP-24 — Interview Skipped on High Complexity

**Symptom:** A High-complexity task proceeds directly to Specify without an Interview, leaving requirement gaps that surface as defects in later waves.

**Detection:** Task card shows complexity: High but no interview receipt in `.wabblespec/state/receipts/`.

**Fix-forward:** Run Interview. Merge findings into the spec before re-running Specify.

**Test anchor:** Any task card with `complexity: High` must have a corresponding `interview-receipt.json`.

---

## DP-25 — Scope Frame Not Updated After Pivot

**Symptom:** `scope.md` reflects the original task scope but the actual work has pivoted (new files, new integration points), causing Guard Layer 2 false negatives on the new scope.

**Detection:** Post-wave diff includes files not in scope.md, but Guard passed because scope.md was not updated after the pivot.

**Fix-forward:** Re-run ScopeFrame with the pivoted requirements. Update scope.md before the next wave.

**Test anchor:** scope.md `in_scope` list must be updated whenever task card stage changes.
