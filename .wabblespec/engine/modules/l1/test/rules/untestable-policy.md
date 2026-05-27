# Untestable Requirements Policy — Test

## Untestable requirements are flagged, not skipped

A requirement that cannot be tested in the project's CI environment is not silently omitted. It is flagged with the UNTESTABLE marker and written to the not-tested compilation.

## UNTESTABLE marker format

```markdown
<!-- UNTESTABLE: <specific reason> -->
```

The reason must be specific. Accepted reasons:

| Reason category | Example |
|---|---|
| Hardware dependency | "Requires physical NFC reader not available in CI" |
| External service | "Requires live third-party payment gateway — cannot mock without invalidating the test" |
| Timing constraint | "Requires real-time clock drift over 72+ hours" |
| Regulatory | "Requires human audit sign-off — not automatable" |
| Observability gap | "System behavior is not externally observable in this environment" |

Vague reasons are not accepted: "too hard", "not applicable", "N/A". If the reason cannot be stated specifically, the requirement is not untestable — generate a stub with what is known.

## Not-tested compilation

Write all UNTESTABLE requirements to `.wabblespec/state/plans/test-plan-<spec-id>.md` in the Untestable Requirements section. Archive reads this compilation.

## Review by Reviewer

If more than 20% of requirements in a spec artifact are flagged UNTESTABLE, route the compilation to Reviewer before writing the test plan. This threshold signals either genuine platform limitations (valid) or under-specified requirements that need Interview.
