---
name: blueprint
description: Converts a Synth candidate into a formal promotion proposal. Names before/after behavior, defines benchmark gates, lists affected targets. Requires Attestation (human sign-off) before Augment or Factory may proceed.
layer: L8
---

# Blueprint

You define what "done" looks like before anyone writes code.

## What this skill does

Blueprint reads a `candidate.json` from Synth, reads the current SKILL.md of the affected module, and produces a `blueprint.json` that specifies: the exact before/after behavior change, the benchmark gate that must pass, the build targets affected, and the verification mode required at Forge. Blueprint is the last human checkpoint before experimental implementation begins.

Blueprint does not write implementations. It does not modify modules. It produces the spec that Augment or Factory works from.

## When to use

Blueprint activates when:
1. A `candidate.json` exists in `.wabblespec/experiments/candidates/` with `status: pending`
2. Human explicitly invokes Blueprint with the candidate ID
3. The affected module's SKILL.md is readable

## Inputs

| Input | Path | Required |
|---|---|---|
| Candidate | `.wabblespec/experiments/candidates/{id}.candidate.json` | Yes |
| Module SKILL.md | `modules/{layer}/{module}/SKILL.md` | Yes — read before/after states from here |
| Module skill-rules.json | `modules/{layer}/{module}/skill-rules.json` | Yes — verification_mode and authority |
| Framework manifest | `framework.yaml` | Yes — confirms module ID and layer |

## Decision logic

1. Read `candidate.json` fully.
2. Read the affected module's SKILL.md. Identify the specific section that describes the behavior to be changed.
3. State `before_behavior`: quote or paraphrase the current SKILL.md description of the behavior.
4. State `after_behavior`: what the SKILL.md should say after the change.
5. Determine if this is AUGMENT (modifying existing module) or NEW (net-new module). This routes to Augment vs Factory.
6. Define `benchmark_gates`: minimum one gate with a metric, threshold, and developer outcome link. Use benchmark.schema.json fields.
7. Identify `affected_targets`: which L3 platform packages are affected by this change. List them explicitly.
8. Determine `verification_mode` for Forge: always Attestation for self-modification. Review or Demonstration for other changes.

Surface open questions to the human before writing if any of the above cannot be determined from the available inputs.

## Output contract

**One file:** `.wabblespec/experiments/blueprints/{candidate-id}.blueprint.json`

```json
{
  "blueprint_id": "matches candidate_id",
  "candidate_ref": "path to source candidate.json",
  "change_type": "AUGMENT | NEW",
  "affected_module": "module-id",
  "before_behavior": "Quoted or paraphrased current SKILL.md description of the behavior.",
  "after_behavior": "What the SKILL.md will say after the change.",
  "benchmark_gates": [
    {
      "metric": "rate | count | latency_ms | boolean",
      "threshold": 0.8,
      "direction": "lower_is_better | higher_is_better",
      "developer_outcome": "false_completion | missed_test | stale_evidence | rework",
      "rationale": "Why this threshold was chosen."
    }
  ],
  "affected_targets": ["cli", "web"],
  "verification_mode": "Attestation | Review | Demonstration",
  "attestation_required": true,
  "created_at": "ISO-8601",
  "status": "awaiting-attestation"
}
```

After writing, request human Attestation. Blueprint status changes from `awaiting-attestation` to `approved` only after human signs off in writing. Augment and Factory must not proceed before status is `approved`.

## Failure modes

**Before/after ambiguity** — before_behavior or after_behavior is vague ("module will work better"). Fix: quote specific SKILL.md lines for before; write exact replacement text for after.

**Benchmark theater** — benchmark_gates lists a metric with no developer_outcome link. Fix: every gate must name one of the four developer outcomes from benchmark-discipline.md.

**Scope creep at Blueprint** — blueprint changes more than one behavior. Fix: one blueprint per candidate. Multiple behavior changes require multiple Synth candidates.

## Not tested

Blueprint cannot verify that the after_behavior is implementable or that the benchmark threshold is achievable. Augment implements; Benchmark validates. Blueprint's job is precision of specification.
