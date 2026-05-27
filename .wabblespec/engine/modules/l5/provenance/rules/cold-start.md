# Cold-Start Behavior — Provenance

Defines what Provenance does when its ledger or upstream artifacts are absent.

## Absent: provenance ledger

Condition: `memory/provenance/ledger.json` does not exist.
Detection: File read returns 404.
Action: Initialize empty ledger — `{"entries": [], "version": 1}`. Write immediately. Log: "Provenance ledger initialized."
Do NOT: Block other modules because the ledger is absent. An empty ledger is valid.

## Absent: specific provenance entry requested

Condition: Another module queries provenance for a fact ID that has no ledger entry.
Detection: Ledger scan returns no match for the requested fact ID.
Action: Return: `{"status": "not_found", "fact_id": "[id]"}`. Not an error.

## Absent: memory store to check against

Condition: `memory/` empty when Provenance attempts contradiction detection.
Detection: Index read returns empty.
Action: No contradictions possible with empty memory store. Return empty contradiction report.

## Absent: reverse-drift-policy.md

Condition: `rules/reverse-drift-policy.md` missing.
Detection: File read returns 404.
Action: Apply SKILL.md policy inline. Log: "reverse-drift-policy.md missing — using SKILL.md defaults."

## Absent: cascade-policy.md or contradiction-policy.md

Condition: Either policy file missing.
Detection: File read returns 404.
Action: Apply SKILL.md policy inline for the missing file. Log which file is absent.

## Default state on cold start

| Field | Default |
|---|---|
| `ledger_initialized` | true after first write |
| `entry_count` | 0 |
| `contradiction_mode` | active — any new write is checked against existing drawers |
| `cascade_depth` | 3 (maximum ripple depth for updates) |
| `reverse_drift_detection` | active — new assertions checked against prior session outputs |
