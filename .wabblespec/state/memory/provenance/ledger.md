# Provenance Ledger

Append-only. Never edit existing rows. New entries at bottom only.

| timestamp | event | drawer_id | actor | detail |
|---|---|---|---|---|
| 2026-05-19T09:00:00Z | WRITTEN | receipt-schema-design-20260519 | memory | source=_shared/schemas/receipt.base.schema.json |
| 2026-05-19T09:15:00Z | WRITTEN | hook-enforcement-pattern-20260519 | memory | source=hooks/pre-tool-use-receipt-check.py |
| 2026-05-21T09:00:00Z | WRITTEN | memory-drawer-structure-20260521 | memory | source=internal-computation |
| 2026-05-21T09:15:00Z | WRITTEN | drawer-staleness-states-20260521 | memory | source=internal-computation |
| 2026-05-21T09:30:00Z | WRITTEN | wabblespec-kill-criteria-20260521 | memory | source=internal-computation |
| 2026-05-21T12:15:00Z | WRITTEN | receipt-schema-design-20260521 | memory | source=_shared/schemas/receipt.base.schema.json |
| 2026-05-21T12:15:00Z | SUPERSEDED | receipt-schema-design-20260519 | provenance | superseded_by=receipt-schema-design-20260521 |
| 2026-05-23T00:00:00Z | CASCADE | receipt-schema-design-20260521 | provenance | change_class=BREAKING hop=1 source=.wabblespec/plans/receipt-schema-spec-v1.md affected_drawers=1 affected_specs=none |
| 2026-05-23T00:00:00Z | STALENESS_TRANSITION | receipt-schema-design-20260521 | provenance | FRESH -> NEEDS_REVERIFICATION reason=BREAKING cascade from receipt-schema-spec-v1.md |
| 2026-05-25T16:52:35Z | WRITTEN | smoke-test-drawer-20260526 | memory | source=_shared/references/invariants.md confidence=0.9 |
| 2026-05-28T23:15:27Z | DELETED | receipt-schema-design-20260519 | forget | reason=SUPERSEDED by receipt-schema-design-20260521; confidence 0.0005; closet archive retained by=forget |
