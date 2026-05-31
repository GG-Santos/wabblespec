# Document Gateway — Audit Gates

Verifier registers these gates when Document gateway activates. All HARD gates must PASS for gateway receipt to be PASS.

---

## Universal Gates (all formats)

| Gate | Severity | Check |
|---|---|---|
| DOC-1 | HARD | Output file written and non-zero bytes |
| DOC-2 | HARD | Runtime dependencies present and importable before production starts |
| DOC-3 | HARD | Professional font used (not system default where avoidable) |
| DOC-4 | SOFT | Output opened or validated by format-specific tool after production |

---

## DOCX Gates

| Gate | Severity | Check |
|---|---|---|
| DX-1 | HARD | Page size declared explicitly — docx-js defaults to A4; US Letter = 12240 × 15840 DXA |
| DX-2 | HARD | Zero `\n` characters used for spacing — separate Paragraph elements only |
| DX-3 | HARD | Zero unicode bullet characters (`•`, `•`) — LevelFormat.BULLET with numbering config only |
| DX-4 | HARD | All table widths use `WidthType.DXA` — no `WidthType.PERCENTAGE` (breaks Google Docs) |
| DX-5 | HARD | Tables have both `columnWidths` array AND individual cell `width` — dual widths required |
| DX-6 | HARD | `columnWidths` sum equals table width exactly (DXA units) |
| DX-7 | HARD | Table shading uses `ShadingType.CLEAR` — never `ShadingType.SOLID` (causes black fill) |
| DX-8 | HARD | `ImageRun` has explicit `type` field (png / jpg / gif / bmp / svg) |
| DX-9 | HARD | `PageBreak` wrapped in `Paragraph` — standalone produces invalid XML |
| DX-10 | HARD | Document validated with `python scripts/office/validate.py` or equivalent before delivery |
| DX-11 | SOFT | Cell margins declared (recommended: top: 80, bottom: 80, left: 120, right: 120) |
| DX-12 | SOFT | Heading styles override built-in IDs exactly: "Heading1", "Heading2" — not custom names |
| DX-13 | SOFT | TOC headings use `HeadingLevel` enum with `outlineLevel` field (required for TOC navigation) |

**DX-4/5/6 method:** Inspect generated XML or JS code for WidthType.PERCENTAGE; ensure columnWidths array is present and sums to declared table width.

---

## PDF Gates

| Gate | Severity | Check |
|---|---|---|
| PD-1 | HARD | No Unicode subscript/superscript characters in ReportLab output — use `<sub>` / `<super>` tags in Paragraph objects |
| PD-2 | HARD | Page size declared explicitly in ReportLab canvas or SimpleDocTemplate |
| PD-3 | SOFT | Multi-page documents use Platypus flowables (Paragraph, Spacer, PageBreak) — not raw canvas for complex layouts |
| PD-4 | SOFT | pypdf used for merge/split operations; reportlab for creation; pdfplumber for extraction |

**PD-1 method:** Search generated code for Unicode subscript/superscript codepoints (₀-₉, ⁰-⁹). Any occurrence fails.

---

## XLSX Gates

| Gate | Severity | Check |
|---|---|---|
| XL-1 | HARD | Zero formula errors in output: #REF!, #DIV/0!, #VALUE!, #N/A, #NAME? — run `python scripts/recalc.py <file>.xlsx` |
| XL-2 | HARD | Calculated values use Excel formulas, not Python-computed hardcoded values |
| XL-3 | HARD | `scripts/recalc.py` run after any formula is written — formulas are strings until recalculated |
| XL-4 | SOFT | Financial model color coding applied if financial content present: Blue=hardcoded inputs, Black=formulas, Green=cross-sheet links |
| XL-5 | SOFT | Hardcoded values have source comment: "Source: [System], [Date], [Reference]" |
| XL-6 | SOFT | Years formatted as text strings ("2024") not numbers (2,024) |

**XL-1 method:** Run `python scripts/recalc.py output.xlsx` — check JSON output for `status: "errors_found"`. Fix all errors before delivery.

---

## PPTX Gates

| Gate | Severity | Check |
|---|---|---|
| PP-1 | HARD | Slide dimensions declared explicitly: 16:9 = 9144000 × 5143500 EMU; 4:3 = 9144000 × 6858000 EMU |
| PP-2 | HARD | All measurements in EMU (914400 EMU = 1 inch) — no pixel values |
| PP-3 | HARD | Presentation saved and file is non-zero bytes |
| PP-4 | SOFT | Title placeholder populated on every slide that has one |
| PP-5 | SOFT | Font sizes consistent across slides of the same type |
| PP-6 | SOFT | LibreOffice conversion verified if PDF export of pptx is needed: `python scripts/office/soffice.py --headless --convert-to pdf presentation.pptx` |
