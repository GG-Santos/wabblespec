# Wave Plan

**task_card:** .wabblespec/state/plans/task-card.md
**target:** Framework
**complexity:** Medium
**collapse_eligible:** false
**session_id:** html-slides-20260531
**generated_at:** 2026-05-31T09:52:00Z

## Waves

### Wave 1: slide-token-validator.py

**inputs:** [task-card.md (AC3, AC4), scope.md (token violation rules: raw hex, rgb(), px in style context)]
**outputs:** [.wabblespec/engine/shared/scripts/slide-token-validator.py]
**checkpoint:** slide-token-validator.py exists, exits 0 on token-clean HTML, exits non-zero with line number on raw hex or rgb() violation
**verification_command:** `python .wabblespec/engine/shared/scripts/slide-token-validator.py --help && python -c "import tempfile,os; f=tempfile.NamedTemporaryFile(suffix='.html',delete=False,mode='w'); f.write('<html><style>:root{background:var(--color-background);}</style></html>'); f.close(); r=os.system('python .wabblespec/engine/shared/scripts/slide-token-validator.py '+f.name); os.unlink(f.name); exit(r)" && python -c "import tempfile,os,sys; f=tempfile.NamedTemporaryFile(suffix='.html',delete=False,mode='w'); f.write('<html><style>:root{background:#2563EB;}</style></html>'); f.close(); r=os.system('python .wabblespec/engine/shared/scripts/slide-token-validator.py '+f.name); os.unlink(f.name); sys.exit(0 if r!=0 else 1)" && echo AC3+AC4 PASS`
**rollback_to:** null
**verification_mode:** Test

---

### Wave 2: generate-slide.py

**inputs:** [task-card.md (AC1, AC2, AC5, AC6), .wabblespec/engine/shared/scripts/slide-token-validator.py (Wave 1 output), colors.csv embedded palette data (161 entries from reference source), charts.csv embedded chart-type mappings (25 types from reference source)]
**outputs:** [.wabblespec/engine/shared/scripts/generate-slide.py]
**checkpoint:** generate-slide.py exists; running with --query 'Analytics Dashboard' produces HTML containing Chart.js CDN link, all 16 color token CSS vars, spacing tokens, shadow tokens; slide-token-validator.py exits 0 on the output; unknown query falls back to SaaS (General) without crashing
**verification_command:** `python .wabblespec/engine/shared/scripts/generate-slide.py --query "Analytics Dashboard" --chart-type bar --output /tmp/ws-test-slide.html && python .wabblespec/engine/shared/scripts/slide-token-validator.py /tmp/ws-test-slide.html && grep -q 'cdn.jsdelivr.net/npm/chart.js' /tmp/ws-test-slide.html && grep -q -- '--color-primary' /tmp/ws-test-slide.html && grep -q -- '--space-xs' /tmp/ws-test-slide.html && grep -q -- '--shadow-sm' /tmp/ws-test-slide.html && python .wabblespec/engine/shared/scripts/generate-slide.py --query "Nonexistent Product XYZ 999" --output /tmp/ws-fallback-slide.html && echo AC1+AC2+AC3+AC5+AC6 PASS`
**rollback_to:** Wave 1 checkpoint
**verification_mode:** Test

---

### Wave 3: present SKILL.md HTML Slide Output section

**inputs:** [task-card.md (AC7, AC8), .wabblespec/engine/modules/l7/present/SKILL.md (existing file to patch), .claude/skills/present/SKILL.md (mirror target)]
**outputs:** [.wabblespec/engine/modules/l7/present/SKILL.md (patched with HTML Slide Output section), .claude/skills/present/SKILL.md (identical patch applied)]
**checkpoint:** Both present/SKILL.md files contain an HTML Slide Output section documenting generate-slide.py usage, token compliance requirement, and CDN dependency; both files are byte-identical for that section
**verification_command:** `grep -q 'HTML Slide Output' .wabblespec/engine/modules/l7/present/SKILL.md && grep -q 'HTML Slide Output' .claude/skills/present/SKILL.md && grep -q 'generate-slide.py' .wabblespec/engine/modules/l7/present/SKILL.md && grep -q 'cdn.jsdelivr.net' .wabblespec/engine/modules/l7/present/SKILL.md && echo AC7+AC8 PASS`
**rollback_to:** Wave 2 checkpoint
**verification_mode:** Observation

---

## Rollback Map

| Wave | Rollback target | Trigger condition |
|---|---|---|
| Wave 1 fails | null (Wave 1 — no prior checkpoint) | HARD error or BLOCKED after 3 REVISE cycles |
| Wave 2 fails | Wave 1 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |
| Wave 3 fails | Wave 2 checkpoint | HARD error or BLOCKED after 3 REVISE cycles |
