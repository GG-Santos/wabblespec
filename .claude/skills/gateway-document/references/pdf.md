# PDF Production Reference

Production rules for generating and processing PDF files using Python libraries.

## Library Selection

| Task | Best tool |
|---|---|
| Create new PDF | `reportlab` (Platypus for complex layouts, Canvas for precise positioning) |
| Merge / split / rotate | `pypdf` |
| Extract text with layout | `pdfplumber` |
| Extract tables | `pdfplumber` |
| OCR scanned PDFs | `pytesseract` + `pdf2image` |
| Fill PDF forms | `pypdf` or `pdf-lib` (see FORMS guidance below) |
| Command-line merge | `qpdf` |

## Setup

```bash
pip install pypdf pdfplumber reportlab
pip install pytesseract pdf2image  # for OCR
```

## Critical Rules

| Rule | Why |
|---|---|
| Never use Unicode subscript/superscript in ReportLab | Built-in fonts lack those glyphs — renders as black boxes |
| Declare page size explicitly | Default varies by OS locale |
| Use Platypus flowables for multi-page documents | Canvas is for single-page precise layouts only |

## Creating PDFs with ReportLab

### Simple document (Platypus)

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

doc = SimpleDocTemplate("output.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph("Title", styles['Title']))
story.append(Spacer(1, 12))
story.append(Paragraph("Body text paragraph.", styles['Normal']))
story.append(PageBreak())
story.append(Paragraph("Page 2", styles['Heading1']))

doc.build(story)
```

### Subscripts and Superscripts (CRITICAL: never use Unicode)

```python
# WRONG — Unicode subscript characters render as black boxes in built-in fonts
bad = Paragraph("H₂O", styles['Normal'])

# CORRECT — use ReportLab XML markup tags
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])
squared  = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

### Tables

```python
data = [['Header 1', 'Header 2', 'Header 3'],
        ['Row 1a', 'Row 1b', 'Row 1c'],
        ['Row 2a', 'Row 2b', 'Row 2c']]

table = Table(data, colWidths=[150, 150, 150])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))
story.append(table)
```

### Precise positioning (Canvas — for diagrams and charts)

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("precise.pdf", pagesize=letter)
width, height = letter

c.setFont("Helvetica-Bold", 16)
c.drawString(100, height - 100, "Title")
c.line(100, height - 110, 500, height - 110)
c.save()
```

## Merging and Splitting with pypdf

```python
from pypdf import PdfReader, PdfWriter

# Merge
writer = PdfWriter()
for path in ["doc1.pdf", "doc2.pdf"]:
    reader = PdfReader(path)
    for page in reader.pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)

# Split
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    w = PdfWriter()
    w.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as f:
        w.write(f)
```

## Extracting Text and Tables

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

## OCR for Scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf")
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
```

## Command-Line Operations

```bash
# Merge (qpdf)
qpdf --empty --pages doc1.pdf doc2.pdf -- merged.pdf

# Split pages 1-5
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf

# Rotate page 1 by 90°
qpdf input.pdf output.pdf --rotate=+90:1

# Remove password
qpdf --password=pw --decrypt encrypted.pdf decrypted.pdf
```

## Watermark

```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)
with open("watermarked.pdf", "wb") as f:
    writer.write(f)
```

## Dependencies

```bash
pip install pypdf pdfplumber reportlab
pip install pytesseract pdf2image  # OCR only
# poppler-utils for pdftotext, pdfimages (system package)
```
