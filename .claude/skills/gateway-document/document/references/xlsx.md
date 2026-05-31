# XLSX Production Reference

Production rules for creating and editing Excel workbooks (.xlsx) using Python.

## Library Selection

| Task | Best tool |
|---|---|
| Data analysis, bulk export | `pandas` |
| Formulas, formatting, charts | `openpyxl` |
| Formula recalculation (mandatory after formula write) | `scripts/recalc.py` |

## Setup

```bash
pip install openpyxl pandas
```

## Critical Rules

| Rule | Why |
|---|---|
| Use Excel formulas, not Python-calculated hardcoded values | Spreadsheet must recalculate when data changes |
| Run `scripts/recalc.py` after writing any formula | openpyxl writes formula strings — values are not calculated until recalculated |
| Zero formula errors before delivery | #REF!, #DIV/0!, #VALUE!, #N/A, #NAME? are audit gate failures |
| Use `data_only=False` when loading for editing | `data_only=True` saves calculated values and loses formulas permanently |

## Formula vs Hardcode (CRITICAL)

```python
# WRONG — hardcoding Python-calculated values
total = df['Sales'].sum()
sheet['B10'] = total               # hardcodes 5000

# CORRECT — Excel formula
sheet['B10'] = '=SUM(B2:B9)'      # recalculates when data changes
sheet['C5'] = '=(C4-C2)/C2'       # growth rate as formula
sheet['D20'] = '=AVERAGE(D2:D19)' # average as formula
```

## Creating New Workbooks

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Sheet1"

# Data
ws['A1'] = 'Revenue'
ws['B1'] = 'Costs'
ws.append(['2024', 1000, 800])

# Formula
ws['C2'] = '=B2-C2'

# Formatting
ws['A1'].font = Font(bold=True, color='FFFFFF')
ws['A1'].fill = PatternFill('solid', start_color='2E75B6')
ws['A1'].alignment = Alignment(horizontal='center')
ws.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

## Financial Model Color Coding (industry standard)

Apply when producing financial models or budget trackers:

| Text color | RGB | Meaning |
|---|---|---|
| Blue | (0, 0, 255) | Hardcoded inputs — numbers users will change for scenarios |
| Black | (0, 0, 0) | ALL formulas and calculations |
| Green | (0, 128, 0) | Cross-sheet links (same workbook) |
| Red | (255, 0, 0) | External file links |
| Yellow background | (255, 255, 0) | Key assumptions needing attention |

```python
from openpyxl.styles import Font, PatternFill

# Hardcoded input cell (blue)
ws['B5'].font = Font(color='0000FF')

# Formula cell (black — default, explicit for clarity)
ws['C5'].font = Font(color='000000')
ws['C5'] = '=B5*(1+$D$2)'

# Assumption cell needing attention (yellow background)
ws['D2'].fill = PatternFill('solid', start_color='FFFF00')
```

## Number Formatting Standards

```python
from openpyxl.styles import numbers

ws['B5'].number_format = '$#,##0'           # currency
ws['C5'].number_format = '0.0%'             # percentage (one decimal)
ws['D5'].number_format = '0.0x'             # valuation multiple
ws['E5'].number_format = '#,##0;(#,##0);-'  # with zero as dash, negatives in parens
ws['A1'].number_format = '@'                # text (for years: "2024" not 2,024)
```

## Formula Recalculation (MANDATORY)

```bash
python scripts/recalc.py output.xlsx
```

Check the JSON output:
```json
{
  "status": "success",        // or "errors_found"
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {          // only present if errors_found
    "#REF!": { "count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"] }
  }
}
```

Fix all errors and recalculate again. Do not deliver a workbook with formula errors.

## Editing Existing Files

```python
from openpyxl import load_workbook

# IMPORTANT: data_only=False preserves formulas
wb = load_workbook('existing.xlsx')       # data_only defaults to False — correct
ws = wb.active

ws['A1'] = 'Updated'
ws.insert_rows(2)
ws.delete_cols(3)

wb.save('modified.xlsx')
# Then: python scripts/recalc.py modified.xlsx
```

**Warning:** `load_workbook('file.xlsx', data_only=True)` saves calculated values and permanently loses formulas if you then save. Only use `data_only=True` for read-only analysis.

## Source Documentation for Hardcoded Values

Add a comment or adjacent cell note for any hardcoded value:
```
Source: [System/Document], [Date], [Specific Reference], [URL if applicable]

Examples:
  Source: Company 10-K, FY2024, Page 45, Revenue Note
  Source: Bloomberg Terminal, 2026-05-31, AAPL US Equity
```

## Row/Column Indexing

- openpyxl is 1-indexed: row=1, column=1 → cell A1
- `get_column_letter(64)` → "BL" (not "BK")
- DataFrame row 5 → Excel row 6 (1-indexed offset)

## Dependencies

```bash
pip install openpyxl pandas
# LibreOffice for recalculation: via scripts/recalc.py (auto-configured)
```
