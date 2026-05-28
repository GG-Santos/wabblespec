---
id: framework-maintenance
layer: L2
tier: 2
type: authority
build_status: built
---

# framework-maintenance

Authority module for WabbleSpec framework self-build tasks. Owns shared infrastructure paths so Framework-target sessions pass Guard Layer 4 without requiring per-wave attestations after this bootstrap.

## Purpose

When a task targets `Framework` and must write to shared infrastructure — `engine/shared/`, hooks, scripts, the Guard module, CLAUDE.md, daemon-config, receipt-index, memory artifacts, or `.claude/skills/` — no standard L2 module has authority over those paths. This module closes that governance gap by declaring permanent ownership of the shared-infra surface.

## Activation

Activates automatically for any wave whose `--module` flag resolves to `framework-maintenance`. Executor passes `--module framework-maintenance` whenever the active task card has `target: Framework` and the wave writes to paths in `authority.owns`.

## Authority scope

Covers exactly the paths declared in `authority.owns` within `skill-rules.json`. No product-space writes. I11 applies: framework-maintenance never writes to product space.

## Not-tested / limitations

- Does not enforce its own writes — that is Guard's job.
- Bootstrap attestation (Wave 1 only) is the single one-time exception to normal Guard Layer 4 flow; all subsequent waves run Guard normally under this module.
- Promoting doctor Guard layer to blocking is out of scope (advisory-first per non-goal).
