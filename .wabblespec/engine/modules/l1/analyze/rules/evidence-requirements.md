# Evidence Requirements

Root cause claims require evidence. A root cause without evidence is a hypothesis. Analyze distinguishes these explicitly.

## Evidence quality tiers

### Tier 1 — Verified (confidence ≥ 0.7)

Evidence is directly observable and reproducible.

- A test that reproduces the failure
- A log entry that shows the exact failure state
- A receipt that records the failing check
- A code path traceable to the failure without inference

A Tier 1-backed root cause is **confident**. State it as fact.

---

### Tier 2 — Probable (confidence 0.4–0.69)

Evidence is indirect or partially reproducible.

- A pattern across multiple sessions that suggests (but does not confirm) a root cause
- A Nexus drawer that records a similar past failure
- A code path that would cause the failure if certain conditions hold
- Log output that is consistent with the root cause but not conclusive

A Tier 2-backed root cause is **probable**. State it as "probable root cause: X" with confidence score.

---

### Tier 3 — Speculative (confidence < 0.4)

Evidence is absent or extremely indirect.

- Reasoning by elimination (all other causes ruled out but this one unverified)
- Single-session anomaly with no corroboration
- Inference from architecture without log or code evidence

A Tier 3-backed root cause is **speculative**. Mark it as "hypothesis requiring verification." Do not treat as confirmed.

---

## Minimum evidence per root cause claim

Each root cause identified in the RCA report must cite:
1. At least one evidence source (log path, receipt path, test result, drawer ID, code path)
2. The tier of that evidence
3. If Tier 2 or Tier 3: what additional evidence would confirm or refute it

---

## Nexus as evidence

If Nexus is queried and returns drawer evidence of a prior similar failure, that is Tier 2 evidence — it corroborates but does not confirm the current root cause. Record `nexus_queried: true` and cite the specific drawer IDs returned.

---

## Evidence exclusions

Do not cite as evidence:
- Personal memory or session-prior knowledge not backed by a drawer or file
- "This is commonly how this kind of failure works" — that is category knowledge, not evidence
- Absence of evidence ("there is no log entry showing it succeeded") — absence is weak; confirm absence by checking that the log path exists and was searched
