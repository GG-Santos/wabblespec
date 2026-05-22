# Portability Check

Use this reference when the user asks whether a skill works across agent
runtimes or model families.

## Checks

1. Inspect the produced SKILL.md for provider coupling:
   - vendor names in core instructions
   - CLI-specific commands presented as universal
   - environment variables required without a fallback
   - tool names that only exist in one runtime
2. Run trigger or output evals with `scripts/cross_model_test.py` when
   provider access is available.
3. Compare pass-rate variance across providers. Treat large variance as
   a portability finding, even when one provider performs well.
4. Keep runtime-specific details in a clearly marked optional section or
   handoff note, not in the core universal instructions.

## Report Shape

```markdown
## Portability

- Core neutrality: pass / warn / fail
- Runtime-specific isolation: pass / warn / fail
- Cross-model variance: measured / not measured
- Blocking issue:
- Recommended fix:
```

### Thresholds

**Core neutrality**
- `pass` — no vendor names, no runtime-specific tool names, no hardcoded env vars in core SKILL.md or runtime-neutral references
- `warn` — one or two tool names that have runtime-specific connotations but capability language is present nearby
- `fail` — vendor names, CLI binaries, or env vars embedded in the core instruction path with no fallback

**Runtime-specific isolation**
- `pass` — all runtime-specific content is in a clearly marked optional section or handoff note; removing it leaves the skill functional
- `warn` — runtime-specific content bleeds into a section that claims to be general
- `fail` — runtime-specific content is load-bearing; the skill won't work without it on another runtime

**Cross-model variance**
- `measured` — `cross_model_test.py` ran on ≥2 provider/model pairs; pass-rate delta reported
- `not measured` — provider access unavailable; static sweep only. Name the missing check explicitly.
- Variance > 15 percentage points on the same eval set is a portability finding even when the best provider passes.

If provider access is unavailable, report the static sweep and name the
missing dynamic check explicitly.
