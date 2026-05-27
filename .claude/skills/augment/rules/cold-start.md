# Cold-Start Behavior — Augment

Defines what Augment does when its corpus gate or source module are absent.

## Absent: L8 corpus gate

Condition: Receipt count < 100 PASS.
Action: BLOCK. Surface: "Augment requires L8 corpus gate (100+ PASS receipts)."

## Absent: target module to augment

Condition: Augment invoked without declaring which module to augment.
Action: Surface: "Augment requires a target module ID."
Do NOT: Augment without a declared target.

## Absent: source module SKILL.md

Condition: Target module ID specified but `modules/[layer]/[name]/SKILL.md` not found.
Detection: File read returns 404.
Action: BLOCK Augment. Surface: "SKILL.md for module '[id]' not found. Cannot augment a non-existent module."

## Absent: augmentation specification

Condition: Target module exists but no augmentation spec declared (what capability to add, what to change).
Action: Surface: "Specify the augmentation: what capability is being added or modified, and why."

## Absent: prior Augment receipt for this module

Condition: No prior augment receipt for this module.
Action: Treat as first augmentation. Capture baseline SKILL.md content before modifying.

## Default state on cold start

| Field | Default |
|---|---|
| `activation_gate` | L8 corpus gate |
| `baseline_captured` | Required before any modification |
| `scope` | Single module only — no cross-module augmentation in single run |
| `validation` | validate-graph.py must pass after augmentation |
| `diff_required` | true — before/after diff captured in receipt |
