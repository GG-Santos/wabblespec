# Acceptance Tests — Writer (L6)

## AT-WRITER-01: Goal is required — no goal means no proceed

**Given** a Writer invocation with no `goal` declared
**When** Writer checks required inputs
**Then** Writer does not proceed — it surfaces the missing goal requirement and stops

---

## AT-WRITER-02: All four required inputs checked

**Given** a Writer invocation
**When** input validation runs
**Then** Writer verifies that `content_type`, `goal`, `audience`, and `topic` are all present before generating any output

---

## AT-WRITER-03: Verdict WARN when key points missing

**Given** a Writer run that completes but the output is missing key points declared in the goal
**When** the verdict is determined
**Then** verdict is `WARN` with the missing key points listed

---

## AT-WRITER-04: Verdict PASS when all required points covered

**Given** a Writer run where the output covers all points declared in the goal
**When** the verdict is determined
**Then** verdict is `PASS`

---

## AT-WRITER-05: Receipt contains required fields

**Given** a completed Writer run
**Then** the receipt at `.wabblespec/receipts/writer-{timestamp}.json` contains:
- `content_type`
- `goal`
- `audience`
- `topic`
- `output_path`
- `verdict`
