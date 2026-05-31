# PPTX Production Reference

Production rules for creating PowerPoint presentations (.pptx) using python-pptx.

## Setup

```bash
pip install python-pptx
```

## Units

- All measurements in EMU (English Metric Units)
- 914400 EMU = 1 inch
- 12700 EMU = 1 point

## Critical Rules

| Rule | Why |
|---|---|
| Declare slide dimensions explicitly | Defaults vary; 16:9 and 4:3 have different EMU sizes |
| Use EMU for all measurements | Pixels and points are not valid in python-pptx |
| Populate title placeholder when it exists | Untitled slides fail readability check |
| Save before delivery | Presentation object is in memory only until saved |

## Slide Dimensions

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu

prs = Presentation()

# 16:9 widescreen (standard modern)
prs.slide_width  = 9144000   # 10 inches
prs.slide_height = 5143500   # 7.5 inches

# 4:3 standard
# prs.slide_width  = 9144000
# prs.slide_height = 6858000
```

## Creating a Presentation

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width  = 9144000
prs.slide_height = 5143500

# Slide layouts: 0=title slide, 1=title+content, 5=blank, 6=title only
title_layout   = prs.slide_layouts[0]
content_layout = prs.slide_layouts[1]
blank_layout   = prs.slide_layouts[5]

# Title slide
slide = prs.slides.add_slide(title_layout)
slide.shapes.title.text = "Presentation Title"
slide.placeholders[1].text = "Subtitle"

# Content slide
slide2 = prs.slides.add_slide(content_layout)
slide2.shapes.title.text = "Section Title"
tf = slide2.placeholders[1].text_frame
tf.text = "First bullet"
tf.add_paragraph().text = "Second bullet"

prs.save("output.pptx")
```

## Adding Shapes and Images

```python
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE_TYPE

# Image
slide.shapes.add_picture(
    "image.png",
    left=Inches(1), top=Inches(1),
    width=Inches(4), height=Inches(3)
)

# Rectangle
from pptx.util import Pt
from pptx.dml.color import RGBColor

shape = slide.shapes.add_shape(
    1,  # MSO_SHAPE_TYPE.RECTANGLE
    left=Inches(1), top=Inches(1),
    width=Inches(3), height=Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x2E, 0x75, 0xB6)
shape.line.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
```

## Text Formatting

```python
from pptx.util import Pt
from pptx.dml.color import RGBColor

tf = slide.shapes.title.text_frame
para = tf.paragraphs[0]
run = para.runs[0]

run.font.bold = True
run.font.size = Pt(32)
run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
para.alignment = PP_ALIGN.CENTER
```

## Tables

```python
from pptx.util import Inches

rows, cols = 3, 3
left, top = Inches(1), Inches(2)
width, height = Inches(8), Inches(2)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths (EMU)
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(2)
table.columns[2].width = Inches(3)

# Fill cells
table.cell(0, 0).text = "Header 1"
table.cell(0, 1).text = "Header 2"
table.cell(1, 0).text = "Data"
```

## Editing Existing Presentations

```python
prs = Presentation("existing.pptx")

for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if "old text" in run.text:
                        run.text = run.text.replace("old text", "new text")

prs.save("modified.pptx")
```

## PDF Export via LibreOffice

```bash
python scripts/office/soffice.py --headless --convert-to pdf presentation.pptx
```

## Generating WabbleSpec Delivery Slides (pattern)

When `present` skill calls gateway-document for a delivery slide deck:

```python
# Standard slide structure for WabbleSpec Archive → PPTX
slides_to_create = [
    {"layout": 0, "title": f"Delivery: {task_goal}", "subtitle": f"v{version} · {date}"},
    {"layout": 1, "title": "What Was Built",    "bullets": completed_waves},
    {"layout": 1, "title": "Quality Floor",     "bullets": quality_gates},
    {"layout": 1, "title": "What Changed",      "bullets": changelog_entries},
    {"layout": 1, "title": "Next Steps",        "bullets": open_items},
]
```

## Dependencies

```bash
pip install python-pptx
# LibreOffice for PDF export: via scripts/office/soffice.py
```
