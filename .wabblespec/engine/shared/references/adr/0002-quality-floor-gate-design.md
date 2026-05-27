# ADR-0002 — Quality Floor: Two Gates Instead of One

- **Status**: Accepted
- **Date**: 2026-05-26
- **Script**: `.wabblespec/engine/shared/scripts/quality-floor-check.py`
- **Registry field**: `quality_floor_passed: true` in `framework.yaml`
- **Reviewers**: Derivable from quality-floor-gates.md and the check script implementation

---

## Context

WabbleSpec's module registry (`framework.yaml`) tracks a `quality_floor_passed` boolean for each of the 99 modules. This flag gates module promotion: a module cannot enter the active evolution chain (Synth → Blueprint → Augment) unless it passes the quality floor.

The quality floor must catch two different failure classes:

1. **Structural failures** — the module file set is incomplete or malformed. SKILL.md absent. `skill-rules.json` missing required fields. `authority.owns` empty. `receipt_required` not a boolean. These are machine-detectable in under 1ms per module and catch authoring accidents.

2. **Content failures** — the module exists structurally but its prompt content is too thin to be useful. SKILL.md body under 200 characters. Missing `## What this skill does` heading. Missing `## When to use` heading. No output contract signal. Frontmatter `description:` under 20 characters. These require text inspection and catch low-effort or generated content that would not actually route correctly at runtime.

Combining both into a single gate produces a gate that is expensive to run (always does text parsing even for structurally broken files) and hard to diagnose (a single failure code does not tell the author whether the problem is structural or content-level).

---

## Decision

Two sequential gates, both required for `quality_floor_passed: true`:

**Gate 1 — `quick_validate`** (8 structural checks):
1. `SKILL.md` exists and is UTF-8 parseable
2. `skill-rules.json` exists and is valid JSON
3. `skill-rules.json` contains required fields: `module`, `layer`, `tier`, `activators`, `authority`, `verification_mode`, `receipt_required`
4. `authority.owns` is non-empty (module must declare at least one owned path)
5. `receipt_required` is a boolean (not a string, not null)
6. `activators` is an array (may be empty for gated modules like instinct)
7. `rules/cold-start.md` exists
8. `tests/acceptance.md` exists

Gate 1 exits immediately on first failure. Text parsing never happens if the JSON is malformed. This keeps CI fast: 97 modules pass Gate 1 in under 2 seconds.

**Gate 2 — `lint_prompts`** (6 content checks, runs only if Gate 1 passes):
1. `SKILL.md` has YAML frontmatter with `name:` field
2. `SKILL.md` has YAML frontmatter with `description:` field of at least 20 characters
3. `SKILL.md` body contains `## What this skill does` heading
4. `SKILL.md` body contains `## When to use` heading
5. `SKILL.md` body contains at least one output contract signal (`## Output`, `## Outputs`, `## Produces`, `## Receipt`, `## Writes`, `output contract`)
6. `SKILL.md` body is at least 200 characters

Modules tagged `security`, `enforcement`, `receipt`, or `gate` in their `skill-rules.json` must also contain the word `adversarial` somewhere in their SKILL.md (warning-level check, not a gate fail — it signals that adversarial input handling was considered during authoring).

---

## Alternatives Considered

### Single combined gate — Rejected

One gate with all 14 checks produces compound failures that mix structural and content problems. An author who forgets `authority.owns` sees the same gate fail as an author who writes a 10-character description. The two problems have completely different fixes. Separate gates produce separate, actionable error messages.

### Full NLP scoring (cosine similarity, embedding-based quality) — Rejected

Embedding-based content scoring was proposed to catch "AI slop" — structurally valid SKILL.md files that contain syntactically correct but semantically empty descriptions. The approach was rejected for three reasons: (1) requires an API call or local model, making the quality floor non-deterministic and environment-dependent; (2) adds 1-3 seconds per module when run across all 99; (3) the L8 evolution chain (Instinct → Synth → Blueprint → Benchmark) already provides the semantic quality gate — a module promoted through that chain with empirical benchmark results is semantically validated. The quality floor is a pre-promotion structural gate, not a replacement for the evolution chain.

### Single structural gate only (Gate 1 only) — Rejected

A module can pass all 8 structural checks while having a 15-character SKILL.md description that says "does stuff." Such a module would receive `quality_floor_passed: true` and become eligible for promotion. Gate 2 exists specifically to prevent this. The 6 content checks are the minimum set that distinguishes a real module from a skeleton.

### Per-module quality thresholds — Rejected

Different minimum body length or description length per layer was proposed (L8 modules are more complex, requiring longer descriptions). Rejected because it produces inconsistent expectations across the codebase and requires per-module configuration that the `framework.yaml` structure does not cleanly support. The 200-character minimum is achievable by any module that actually explains what it does; modules that cannot reach 200 characters are not ready for promotion.

---

## Consequences

### Positive

- Gate 1 failures are fast and actionable: "missing required JSON field" is a 5-minute fix.
- Gate 2 failures are content-specific and actionable: "missing `## When to use` heading" tells the author exactly what to add.
- CI runtime for full quality floor across 97 modules: ~2 seconds (Gate 1) + ~0.5 seconds (Gate 2 text parsing) = ~2.5 seconds total. No API dependency.
- The `--write` flag on `quality-floor-check.py` patches `framework.yaml` with the current gate result, making the registry self-updating after module fixes.

### Negative

- A module can game Gate 2 by writing a 200-character SKILL.md with all required headings but no useful content. The evolution chain (Benchmark gate) is the backstop for this case.
- Gate 2 does not detect routing-hostile language (forbidden tokens per the ADR-0002 rubric from context-mode). The `activator-audit.py` script fills this gap for the routing-sensitive sections.

### Neutral

- Modules with `activators: []` (e.g., `instinct`, gated L8 modules) still pass Gate 1 — an empty activators array is valid. They activate only via explicit command or precondition, not by keyword match.
- The adversarial-word check for security/enforcement modules is a warning, not a gate fail. It surfaces during `--verbose` runs but does not block promotion. It is a human reminder, not an automated guard.
