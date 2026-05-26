# Acceptance Tests — Polish (L6)

## AT-POLISH-01: Code files, schemas, receipts, Memory drawers are never touched

**Given** a Polish run on a project with code files, schemas, receipts, and Memory drawers in scope
**When** the four core passes execute
**Then** none of those file categories are modified; only documentation and spec files are touched

---

## AT-POLISH-02: Four core passes execute in order

**Given** a Polish invocation without optional flags
**When** execution runs
**Then** passes execute in order: Register -> Redundancy -> Structural -> Spec; no pass is skipped

---

## AT-POLISH-03: Pass 5 Proofread activates only on flag or doc type

**Given** a Polish invocation
**When** neither `--proofread` flag is set nor the target is a doc type
**Then** Pass 5 (Proofread) is not run

**Given** `--proofread` flag is set or target is a doc type
**When** Polish runs
**Then** Pass 5 runs after the four core passes

---

## AT-POLISH-04: Pass 6 Markdown activates only on flag or Obsidian path

**Given** a Polish invocation without `--markdown` flag and non-Obsidian path
**When** Polish runs
**Then** Pass 6 (Markdown) is not run

---

## AT-POLISH-05: Diff is mandatory

**Given** a Polish run that modifies any file
**When** execution completes
**Then** a diff of all changes is produced; Polish does not complete without surfacing what changed

---

## AT-POLISH-06: Writes in place

**Given** a Polish run targeting a file at a given path
**When** Polish applies changes
**Then** it modifies the file at its existing path; it does not write to a separate output location
