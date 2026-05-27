# Context Optimization

Compaction, masking, partitioning, and KV-cache techniques. Consumers: executor, autopilot, economy.

## Compaction

Reducing context size by replacing verbose content with dense equivalents.

### Receipt compaction
Replace a full module output with its receipt. A receipt is the information-minimal record of what happened. The full output is on disk at the path cited in the receipt.

Pattern: Load receipt path → cite in context → load full output only if a downstream decision requires it.

### Conversation compaction
At natural breakpoints (end of a wave, before a new phase), replace accumulated turns with a structured summary. Summary must preserve:
- All decisions made (with rationale)
- All facts established (values, thresholds, file paths)
- Current state (which step, which wave, what remains)
- Receipts written (with paths)

Summary must not preserve:
- Exploratory reasoning that reached a conclusion (keep the conclusion, drop the path)
- Rejected alternatives (keep the chosen alternative, note rejections in one line)
- Tool call outputs already captured to disk

### Reference compaction
Replace an in-context reference file with a project-map card (summary). Project-map cards are < 200 tokens. Load full reference only when the card is insufficient.

## Masking

Masking prevents sensitive information from appearing in context.

### PII masking
Before loading a file containing PII into context: replace PII with tokens. `john.doe@example.com` → `[EMAIL_1]`. `+1-555-0100` → `[PHONE_1]`. Maintain a mask table if tokens need to be reversed later.

### Credential masking
Credentials (API keys, passwords, tokens) are never loaded into context. If a file containing credentials is referenced: load only the key names, not the values. `API_KEY=<redacted>`.

### Irrelevant context masking
When a large file is partially relevant: load only the relevant sections. Use headings to identify and extract the relevant section. Reference the file path for the rest.

## Partitioning

Splitting context into independently managed partitions.

### System partition
Invariants + framework config + guard-policy. Loaded once. Cached. Never evicted during a session.

### Task partition
Task card + wave plan + acceptance criteria. Loaded at session start. Refreshed if task card is updated.

### Working partition
Current wave outputs, active receipts, in-flight tool results. Cleared between waves. Only receipts survive wave boundaries.

### On-demand partition
Reference files, Memory drawers, search results. Loaded for a specific step. Dropped after the step completes.

## KV-cache optimization

Position content from most-stable to least-stable in the prompt:
1. System context (cache: session-long)
2. Task card (cache: task-long)
3. Wave plan (cache: wave-long)
4. Current wave working context (cache: few turns)
5. On-demand content (no cache — changes per request)

Moving frequently-changing content to position 5 prevents cache invalidation of positions 1–4.

## Anti-patterns

| Anti-pattern | Cost | Fix |
|---|---|---|
| Keeping full prior wave output in context | Growing context per wave | Replace with receipt after wave completes |
| Reloading same reference file each turn | Cache miss per turn | Load once, reference by path thereafter |
| Copying receipt content inline | Doubles the token count | Reference receipt path; load only if needed |
| Unmasked PII in context | Privacy risk | Mask before loading |
