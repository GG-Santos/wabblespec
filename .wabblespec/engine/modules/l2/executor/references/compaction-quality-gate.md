# Compaction Quality Gate

After CONTEXT_EXHAUSTION fires and the structured summary is written, run this verification before resuming wave execution. A compaction that passes the structure check but loses artifact trail or decision rationale is worse than no compaction — the agent resumes with false confidence.

## When to load this reference

Load when: CONTEXT_EXHAUSTION has fired and a structured summary was produced. Do not load on normal wave execution.

## The Six Dimensions

Evaluate the compacted context against all six dimensions before marking the compaction complete:

| Dimension | What to check | Failure signal |
|---|---|---|
| **Accuracy** | File paths, function names, error codes are exact — not approximated or paraphrased | "the config file" instead of `config/redis.ts`; "the auth error" instead of "401 Unauthorized" |
| **Context Awareness** | Summary reflects current conversation state, not a prior snapshot | Task goal in summary doesn't match the current task card goal |
| **Artifact Trail** | Agent can enumerate which files were read, modified, created | "Files Modified" section is empty or says "various files" |
| **Completeness** | Summary addresses all active questions and in-progress work | An unresolved error from before compaction is absent from "Current State" |
| **Continuity** | Work can resume without re-fetching previously accessed information | "Next Steps" requires reading a file that was already read and summarized |
| **Instruction Following** | Active constraints and output format requirements are preserved | A constraint from the task card is absent from the summary |

## Four Probe Types

After producing the summary, run a spot-check with probes drawn from the compacted history. The probes must be answerable from the summary alone — without re-reading prior context.

### Recall probe

Ask: "What was the specific [error/value/condition] that triggered the current work?"

The summary must name the exact identifier (endpoint path, error code, function name) without requiring re-read of the original context. Acceptable: "The original error was 401 Unauthorized on `/api/auth/login`." Unacceptable: "There was an authentication error."

### Artifact probe

Ask: "Which files have been modified in this session, and what specifically changed in each?"

The summary must list file paths and describe the change at the function/line level. Acceptable: "`config/redis.ts`: updated connection pooling configuration." Unacceptable: "Several config files were updated."

### Continuation probe

Ask: "What is the next concrete action to take?"

The summary must identify a specific next step without requiring re-reading prior context. Acceptable: "Fix 2 remaining test failures in `tests/auth.test.ts` related to mock session service setup." Unacceptable: "Continue debugging."

### Decision probe

Ask: "What did we decide about [the most recent architectural or implementation decision]?"

The summary must capture the decision and its rationale. Acceptable: "Chose Redis connection pool over per-request connections because transient failures caused test failures." Unacceptable: "We made a decision about Redis."

## Scoring Protocol

For each of the six dimensions, assign pass (1) or fail (0). A dimension fails if any probe of that type returns an unacceptable response.

```
quality_score = passing_dimensions / 6
```

| Score | Action |
|---|---|
| 6/6 (1.0) | Compaction is clean — resume wave |
| 4–5/6 (0.67–0.83) | Compaction is marginal — identify failed dimensions and add explicit content before resuming |
| < 4/6 (< 0.67) | Compaction failed — re-run with stricter preservation (extend the "Files Modified" and "Decisions Made" sections) before resuming |

## Artifact Trail Special Handling

Artifact Trail is historically the weakest dimension across all compression methods — even structured summarization only reaches approximately 2.2–2.5 out of 5.0 in rigorous evaluation. This dimension gets an automatic remediation step:

If Artifact Trail fails: before re-running compaction, extract a verbatim artifact list directly from the CONTEXT_EXHAUSTION-protected tail (which is never summarized). The tail contains the most recent wave receipt, which has explicit `files_written` or equivalent fields. Copy these identifiers verbatim into the "Files Modified" section rather than relying on summarization to reconstruct them.

This is why the receipt chain is architecturally superior to compression for artifact tracking: receipts are the authoritative artifact record. When compaction loses the artifact trail, the most recent wave receipt is the ground truth.

## Integration with Executor

The compaction quality gate runs after Step 2 of the CONTEXT_EXHAUSTION protocol (summarize middle) and before resuming the wave. If the gate fails, executor pauses and extends the summary — it does not skip the gate or advance the wave.

The gate does not produce a separate receipt. It is a quality checkpoint within the compression event, recorded in the `compression_occurred` field of the wave receipt when the wave completes.
