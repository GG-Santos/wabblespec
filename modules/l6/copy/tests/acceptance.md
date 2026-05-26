# Acceptance Tests — Copy (L6)

## AT-COPY-01: Six UI copy categories recognized

**Given** a Copy invocation
**When** category is declared
**Then** the following are supported:
- `label`
- `error`
- `tooltip`
- `empty-state`
- `security-warning`
- `confirmation`

---

## AT-COPY-02: Context is required

**Given** a Copy invocation with no context provided
**When** Copy checks required inputs
**Then** Copy does not proceed and requests context before generating any string

---

## AT-COPY-03: "Something went wrong" is never acceptable

**Given** a Copy invocation for an error message
**When** Copy evaluates the proposed error string
**Then** any string equivalent to "Something went wrong" (or equally vague) is rejected and a specific error description is required

---

## AT-COPY-04: Security warnings require acknowledgment action

**Given** a Copy invocation for a `security-warning` category
**When** Copy produces the copy
**Then** the output includes a required user acknowledgment action — a warning with no acknowledgment path is not acceptable output

---

## AT-COPY-05: Receipt records copy produced

**Given** a completed Copy run
**Then** the receipt at `.wabblespec/receipts/copy-{timestamp}.json` contains:
- `category`
- `context`
- `strings_produced`
- `verdict`
