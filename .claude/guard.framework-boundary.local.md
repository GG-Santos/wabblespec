---
name: guard-framework-boundary
enabled: true
event: file
action: block
conditions:
  - field: file_path
    operator: regex_match
    pattern: ^\.wabblespec/
---

HARD BLOCK: Attempted write to .wabblespec/ framework space from a product-space task.

This violates I11 (Framework and Product Never Mix). Framework files are read-only during product-space execution.

If you intended to update a framework module: this must be an explicit framework-authoring task, not a product task. Start a new Recipe session with the framework module as the build target.

WabbleSpec guard rule — I11 enforcement.
