---
name: visualize
description: Generates visual artifacts — architecture diagrams, quality floor charts, receipt analytics, and data visualizations — as PNG or PDF output from WabbleSpec state and receipt data. Activates when a visual representation of framework state, metrics, or architecture is requested. Routes binary output through gateway-document.
layer: L6
---

# Visualize

You produce visual artifacts from WabbleSpec state. Charts, diagrams, and visualizations are produced from receipts, quality floor data, and session state. You do not invent data — every visual element traces to a source file or script output.

## What this skill does

Reads WabbleSpec state, receipt data, and structural metadata. Produces PNG or PDF visual artifacts using Python (matplotlib for charts, reportlab for PDF diagrams). Routes output through gateway-document.

## When to use

- Quality floor trends over multiple runs need a chart
- Architecture diagram of active modules requested
- Receipt analytics (pass rates, wave timing, quality scores) need visual format
- `/visualize` command

## When NOT to use

- A Markdown table suffices — visualize only when visual format is explicitly requested
- The data source is a live browser-rendered application (use platform-web instead)
- Creative/generative art is requested (use canvas-design pattern instead)

## Output types

| Type | Data source | Format |
|---|---|---|
| Quality floor chart | `quality-floor-check.py --format json` | PNG or PDF |
| Receipt timeline | DuckDB receipt-db.py or JSON receipts | PNG |
| Module architecture | `wabblespec.yaml` module list | PDF diagram |
| Wave pass rate | Wave receipt directory | PNG chart |
| Custom data chart | User-provided data | PNG or PDF |

## How to do it

### Step 1 — Load data

For quality floor chart:
```bash
python .wabblespec/engine/shared/scripts/quality-floor-check.py --format json
```

For receipt analytics:
```bash
python .wabblespec/engine/shared/scripts/receipt-db.py query "SELECT * FROM receipts ORDER BY created_at DESC LIMIT 50"
```

For architecture diagram: read `.wabblespec/wabblespec.yaml` modules section.

### Step 2 — Generate with matplotlib or reportlab

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json, os

# Quality floor example
data = json.load(open("qf-result.json"))
modules = [m['id'] for m in data['modules']]
scores  = [m['score'] for m in data['modules']]

fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#2E75B6' if s >= 4.0 else '#C00000' for s in scores]
ax.bar(modules, scores, color=colors)
ax.axhline(y=4.0, color='orange', linestyle='--', label='Floor (4.0)')
ax.set_xlabel('Module')
ax.set_ylabel('Quality Score')
ax.set_title('WabbleSpec Quality Floor')
ax.tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig('quality-floor.png', dpi=150, bbox_inches='tight')
```

### Step 3 — Invoke gateway-document for PDF output

If PDF requested:
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("visualization.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [
    Paragraph("WabbleSpec Quality Floor", styles['Title']),
    Image('quality-floor.png', width=500, height=250),
]
doc.build(story)
```

### Step 4 — Write receipt

```bash
python .wabblespec/engine/shared/scripts/receipt-writer.py \
  --type generic \
  --task-id <task-id> --session-id <session-id> \
  --status PASS \
  --summary "Visualize: <type> → <output path>" \
  --out .wabblespec/state/receipts/visualize-<timestamp>.json
```

## Reference Routing

| Situation | Reference |
|---|---|
| PDF output rules | `gateway-document/references/pdf.md` |
| Visualize receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type generic` |

## Dependencies

```bash
pip install matplotlib
# reportlab already available via gateway-document/references/pdf.md
```
