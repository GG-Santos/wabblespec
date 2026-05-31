---
name: gateway-document
description: Document output gateway. Routes any request to produce a Word document, PDF, Excel workbook, or PowerPoint presentation to the correct format handler with cross-cutting quality rules. Activates when archive, document, writer, report, present, visualize, or specify requests a binary document output. Summonable by any skill that needs to produce a stakeholder-ready deliverable.
---

# Gateway: Document

Cross-cutting document production layer. Routes output requests to the correct format handler and enforces shared quality standards across all binary document formats: Word (.docx), PDF, Excel (.xlsx), and PowerPoint (.pptx).

This gateway does not generate content — it applies format-specific production rules and quality gates to content provided by the calling skill.

## What this skill does

| Concern | Covered by calling skill | Covered by Document gateway |
|---|---|---|
| Content to put in the document | Yes (calling skill) | — |
| Format routing (docx / pdf / xlsx / pptx) | Request declares | Yes |
| Production rules per format | No calling skill | Yes — per-format reference |
| Library selection for the target format | No calling skill | Yes |
| Validation / zero-error guarantee | No calling skill | Yes |
| Professional typography baseline | No calling skill | Yes |
| Cross-format quality audit | No calling skill | Yes |

## When to use

- `archive` requests a delivery receipt as a Word document or PDF
- `document` requests a README, spec, or reference as PDF or docx
- `writer` requests long-form content output as docx
- `specify` requests a task card exported as PDF
- `report` generates a 3P update or stakeholder status
- `present` generates a slide deck from archive data
- `visualize` generates a PDF chart or diagram
- Explicit `/gateway-document` command

## When NOT to use

- The output is Markdown only — gateway-document is for binary format output
- The calling skill has already handled format production — do not double-apply
- The format requested is HTML/web artifacts (use platform-web or web-artifacts-builder pattern instead)

## Format routing

Determine the output format from the caller's request before loading any reference:

| Requested output | Format | Reference to load |
|---|---|---|
| `.docx`, Word document, Word export | DOCX | `references/docx.md` |
| `.pdf`, PDF export, PDF archive | PDF | `references/pdf.md` |
| `.xlsx`, `.csv → xlsx`, spreadsheet, workbook | XLSX | `references/xlsx.md` |
| `.pptx`, PowerPoint, slide deck, slides | PPTX | `references/pptx.md` |
| Ambiguous or multi-format | Ask or default to PDF | Both PDF + target format |

Load only the reference file for the requested format. Do not load all four unless multi-format output is explicitly requested.

## Activation sequence

### Phase A — Format selection and dependency check

```
1. Identify requested format from caller context
2. Load the matching format reference from references/
3. Check runtime dependencies:
   DOCX: node.js + docx npm package ("npm list -g docx" or "node -e require('docx')")
   PDF:  python + pypdf + reportlab ("python -c 'import pypdf, reportlab'")
   XLSX: python + openpyxl + pandas ("python -c 'import openpyxl, pandas'")
   PPTX: python + python-pptx ("python -c 'import pptx'")
4. If dependency missing: surface install command; do not proceed until resolved
5. Write gateway-spec-receipt (Phase A)
```

### Phase B — Quality audit after production

```
1. Run format-specific validation (declared in references/<format>.md Validation section)
2. Check all audit gates in audit-gates.md
3. Write gateway-verdict-receipt (Phase B: PASS / FLAG / BLOCK)
```

## Reference Routing

| Situation | Reference |
|---|---|
| DOCX production rules | `references/docx.md` |
| PDF production rules | `references/pdf.md` |
| XLSX production rules | `references/xlsx.md` |
| PPTX production rules | `references/pptx.md` |
| Document receipt write | `engine/shared/references/script-delegation-contract.md` → `receipt-writer.py --type gateway-spec` / `gateway-verdict` |

## Output contract

- Format validation report (zero-error confirmation or finding list)
- Dependency check result
- Typography baseline audit
- Gateway activation receipt with all gate results

## Files loaded by this module

```
modules/l4/document/
  audit-gates.md
  references/
    docx.md
    pdf.md
    xlsx.md
    pptx.md
```
