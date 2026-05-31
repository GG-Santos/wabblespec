# Session Scope

**target:** Framework
**complexity:** Medium
**locked_at:** 2026-05-31T09:45:00Z
**session_id:** html-slides-20260531

## In Scope

- Create .wabblespec/engine/shared/scripts/generate-slide.py with embedded 161-palette color lookup and chart-type mappings; outputs self-contained Chart.js HTML presentation
- Create .wabblespec/engine/shared/scripts/slide-token-validator.py validating generated HTML for raw hex/rgb/px violations
- Embed spacing tokens (--space-xs through --space-3xl) and shadow tokens (--shadow-sm through --shadow-xl) as constants in generate-slide.py
- Update .wabblespec/engine/modules/l7/present/SKILL.md with HTML Slide Output section
- Mirror present SKILL.md update to .claude/skills/present/SKILL.md in the same operation

## Out of Scope

- Runtime calls to core.py or design_system.py — token data is embedded
- Gemini API / AI logo + CIP generation (separate Tier 7)
- Modifying colors.csv, charts.csv, or any reference directory file
- Daemon/stop-hook wiring for generate-slide.py
- PowerPoint (.pptx) output path — unchanged
- New module registration in wabblespec.yaml

## Assumptions

- Python 3 available; no third-party pip packages required beyond standard library
- Chart.js loaded from CDN in generated HTML — no local install
- Color palettes embedded from colors.csv as Python dict (161 entries) — no runtime CSV read
- Chart type mappings embedded from charts.csv — no runtime CSV read
- present SKILL.md update is strictly additive; existing .pptx workflow unchanged
- I11: both scripts go to .wabblespec/engine/shared/scripts/ (framework space only)

## Scope Change Log

| timestamp | change | triggered_by |
|---|---|---|
