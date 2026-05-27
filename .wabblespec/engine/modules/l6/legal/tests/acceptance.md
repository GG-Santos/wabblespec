# Acceptance Tests — Legal (L6)

## AT-LEGAL-01: Verdict is always DRAFT

**Given** any Legal invocation regardless of input quality or completeness
**When** Legal produces output
**Then** `verdict` is hardcoded `DRAFT` — no Legal output is ever marked PASS or complete

---

## AT-LEGAL-02: legal_review_required is always true

**Given** any Legal output
**When** the receipt is inspected
**Then** `legal_review_required: true` is hardcoded — this value is never false regardless of document type or content

---

## AT-LEGAL-03: Four document types supported

**Given** a Legal invocation
**When** document type is declared
**Then** the following are supported:
- `privacy-policy`
- `terms-of-service`
- `gdpr-data-processing`
- `disclaimer`

---

## AT-LEGAL-04: [REVIEW REQUIRED] markers for unpopulated clauses

**Given** a Legal document with clauses that require jurisdiction-specific or organization-specific information
**When** Legal generates the document
**Then** every unpopulated clause is marked with `[REVIEW REQUIRED]` — no clause is left blank or silently skipped

---

## AT-LEGAL-05: Every output includes legal disclaimer text

**Given** any Legal output document
**When** the document is inspected
**Then** a legal disclaimer is present stating the document is a draft requiring qualified legal review; this disclaimer is not optional

---

## AT-LEGAL-06: Receipt contains required fields

**Given** a completed Legal run
**Then** the receipt at `.wabblespec/receipts/legal-{timestamp}.json` contains:
- `document_type`
- `output_path`
- `review_required_markers_count`
- `verdict` (always "DRAFT")
- `legal_review_required` (always true)
