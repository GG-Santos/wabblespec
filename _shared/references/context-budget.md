# Context Budget

Session context health tiers. Consumers: executor, autopilot, economy.

Cross-references: `context-engineering.md` (what to load), `context-optimization.md` (compaction techniques), `staleness-states.md` (evidence age — orthogonal axis).

---

## What this reference is

Context-engineering.md defines load priority. Context-optimization.md defines compaction techniques. This file defines when to change strategy based on context window health. The four tiers drive the decision of which technique to invoke and when.

---

## Tier Model

| Tier | Definition | Observable signal |
|---|---|---|
| PEAK | Full context window available. No summarization artifacts. All loaded content is reliable. | Tool calls return results that match loaded context. Cross-references resolve correctly. |
| GOOD | Moderate context consumed. Recent turns reliable. Earlier turns may be summarized by the runtime. | Receipts and task card still precise. Some speculative reference loads from early turns may no longer be in full context. |
| DEGRADING | Context budget under pressure. Summarization artifacts present. Speculative loads are unreliable. | Module references misfire or return truncated results. Earlier wave outputs partially collapsed. |
| POOR | Context at or near limit. Module behavior inconsistent with loaded spec. | Instruction-following errors increase. Task card or wave plan details inaccessible or contradicted. |

---

## Actions per tier

| Tier | Recommended action |
|---|---|
| PEAK | Operate normally. |
| GOOD | Load receipts rather than full prior-wave outputs. Do not carry speculative reference files forward. |
| DEGRADING | Invoke Economy compaction. Increase receipt density (write receipts more frequently). Drop all speculative context loads. Confirm task card and active wave plan are still in clean context. |
| POOR | Invoke Recipe checkpoint detection. Cold-start from last checkpoint. Do not attempt to continue the current wave — the context integrity required for receipt-accurate execution is not present. |

---

## Relationship to other references

**context-engineering.md** — use that reference to decide what to load. Use this reference to decide when the current load strategy needs to change.

**context-optimization.md** — use that reference for the specific compaction/masking/partitioning technique once DEGRADING tier is confirmed. This reference tells you when to trigger it.

**staleness-states.md** — staleness is a property of evidence age. Context budget is a property of window capacity. A FRESH drawer in POOR context is still reliable evidence — it is the loading and retrieval that is unreliable, not the evidence itself.

---

## Tier detection heuristics

These are heuristics only — exact thresholds depend on the active runtime's context window size, which is not recorded in runtime-state.json (I6: no vendor specifics).

| Signal | Likely tier |
|---|---|
| All file reads return full content; no signs of truncation | PEAK or GOOD |
| A recently-loaded reference returns only a partial match | GOOD or DEGRADING |
| A receipt written in this session cannot be located by path | DEGRADING |
| Task card instructions produce inconsistent tool behavior | POOR |
| Guard layer results contradict prior Guard receipts in the same session | POOR |

When uncertain between DEGRADING and POOR: assume POOR. False-positive cold-start costs one checkpoint recovery. A false-negative (treating POOR as DEGRADING) risks silent spec drift.
