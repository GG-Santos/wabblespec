# RCA Method Selection

Select one method before starting analysis. The method determines traversal structure — switching mid-analysis invalidates work.

## 5-Whys

**When:** Linear cause chain. Single failure mode. System is well-understood. The problem has an obvious starting point.

**Structure:** Start from the symptom. Ask "why did this happen?" Record the answer. Ask "why did that happen?" Repeat until reaching a system-level root (3–5 levels typical). Stop when the answer is outside the system boundary or requires a policy decision.

**Good for:** Specific bugs, deployment failures, single-point incidents.

**Not good for:** Problems with multiple independent failure paths. Problems in systems that are not well-understood (use fault-tree instead).

---

## Fishbone (Ishikawa)

**When:** Multiple contributing factors across different categories. The failure has no single root — it is an intersection of conditions.

**Structure:** The problem is the fish head. Six categories form the bones: People, Process, Technology, Environment, Data, External. Populate each category with contributing factors. Do not force a category that does not apply.

**Good for:** Quality problems with multiple dimensions, performance degradation with no single cause, recurring incidents where each occurrence has a slightly different cause.

**Not good for:** Single-cause bugs (use 5-whys — fishbone is overkill).

---

## Fault Tree

**When:** Safety-critical failure scenarios. Complex multi-path failures. The failure can occur via multiple independent paths.

**Structure:** The top-level failure event is the root. Decompose into sub-events using AND/OR gates. AND gate: all sub-events must occur. OR gate: any sub-event causes the failure. Trace to basic events (not further decomposable).

**Good for:** Security incidents, data loss scenarios, cascading failure analysis.

**Not good for:** Simple bugs with known cause. Fault trees require knowing the failure modes in advance.

---

## Timeline

**When:** The sequence of events is unknown. The problem may have been caused by events in a specific order that must be reconstructed.

**Structure:** List all known events with timestamps. Fill gaps by inference (mark inferred events clearly). Identify the first event that could not have been prevented given prior state. That event is the trigger.

**Good for:** Incidents where logs and receipts are available but causation is unclear. Post-mortems. "How did we get here?" questions.

**Not good for:** Problems without timestamped evidence.
