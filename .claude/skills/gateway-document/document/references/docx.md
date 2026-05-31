# DOCX Production Reference

Production rules for generating Word documents (.docx) via the `docx` npm package (docx-js).

## Setup

```bash
npm install -g docx
# or local: npm install docx
```

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        ImageRun, Header, Footer, AlignmentType, PageOrientation,
        LevelFormat, ExternalHyperlink, InternalHyperlink, Bookmark,
        FootnoteReferenceRun, TableOfContents, HeadingLevel,
        BorderStyle, WidthType, ShadingType, VerticalAlign,
        PageNumber, PageBreak, Column, SectionType } = require('docx');
const fs = require('fs');
```

## Critical Rules (violation = audit gate failure)

| Rule | Why |
|---|---|
| Always declare page size explicitly | docx-js defaults to A4; US documents need Letter |
| Never use `\n` for line breaks | Use separate Paragraph elements |
| Never use unicode bullet characters | Use `LevelFormat.BULLET` with numbering config |
| Always use `WidthType.DXA` for tables | `WidthType.PERCENTAGE` breaks in Google Docs |
| Tables require dual widths | `columnWidths` array AND `width` on each cell |
| `columnWidths` must sum to table width | Exact match required in DXA units |
| Use `ShadingType.CLEAR` for table shading | `ShadingType.SOLID` renders as black fill |
| `ImageRun` requires `type` field | Omitting it produces invalid XML |
| `PageBreak` must be inside a Paragraph | Standalone PageBreak creates invalid XML |

## Units

- 1440 DXA = 1 inch
- US Letter: 12240 × 15840 DXA (8.5" × 11")
- A4 (default, avoid): 11906 × 16838 DXA
- Content width at 1" margins (US Letter): 12240 − 2880 = 9360 DXA
- EMU (for images): 914400 EMU = 1 inch

## Page Setup

```javascript
sections: [{
  properties: {
    page: {
      size: { width: 12240, height: 15840 },  // US Letter
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
    }
  },
  children: [/* content */]
}]
```

**Landscape:** pass portrait dimensions and set `orientation: PageOrientation.LANDSCAPE` — docx-js swaps width/height internally.

## Styles

```javascript
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 } },
    ]
  }
})
```

Use exact built-in IDs ("Heading1", "Heading2") to override default styles. Include `outlineLevel` for TOC.

## Lists (never use unicode bullets)

```javascript
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    children: [
      new Paragraph({ numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Bullet item")] }),
    ]
  }]
});
```

Same reference = continues numbering. Different reference = restarts numbering.

## Tables

```javascript
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

new Table({
  width: { size: 9360, type: WidthType.DXA },
  columnWidths: [4680, 4680],           // MUST sum to table width
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: 4680, type: WidthType.DXA },  // MUST match columnWidths entry
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },  // CLEAR not SOLID
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun("Cell")] })]
        })
      ]
    })
  ]
})
```

## Images

```javascript
new Paragraph({
  children: [new ImageRun({
    type: "png",                          // Required: png / jpg / jpeg / gif / bmp / svg
    data: fs.readFileSync("image.png"),
    transformation: { width: 200, height: 150 },
    altText: { title: "Title", description: "Desc", name: "Name" }
  })]
})
```

## Headers, Footers, Page Numbers

```javascript
sections: [{
  properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
  headers: {
    default: new Header({ children: [new Paragraph({ children: [new TextRun("Header")] })] })
  },
  footers: {
    default: new Footer({ children: [new Paragraph({
      children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })]
    })] })
  },
  children: [/* content */]
}]
```

## Save

```javascript
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("output.docx", buffer);
});
```

## Validation

```bash
python scripts/office/validate.py output.docx
```

Fix any validation errors before delivery. Common errors: missing relationships, malformed XML nesting, invalid RSIDs.

## Editing Existing Documents

```bash
# Unpack
python scripts/office/unpack.py document.docx unpacked/

# Edit XML in unpacked/word/document.xml using Edit tool
# Use smart quote entities: &#x2019; (') &#x201C; (") &#x201D; (")

# Repack
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```

Use `Edit` tool for string replacement — never write Python scripts for XML edits.

## Dependencies

- `docx` npm package: `npm install -g docx`
- LibreOffice (for PDF conversion): via `scripts/office/soffice.py`
- pandoc (for text extraction): `pandoc --track-changes=all doc.docx -o output.md`
