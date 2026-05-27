# Learned Parameters

EMA-learned sampling parameter adjustments per WabbleSpec context type.

Written by: `feedback --learn` (ParamLearner, G0DM0D3 Wave 5)
Read by: `model-router` (ContextTuner integration, Wave 2)
Script: `_shared/scripts/param-learner.py`

## Files

One JSON file per context type. Created on first `feedback --learn` signal for that type.

```
learned-params-spec-authoring.json
learned-params-code-generation.json
learned-params-security-review.json
learned-params-planning.json
learned-params-synthesis.json
learned-params-administrative.json
```

## Gate conditions for model-router to apply adjustments

- `sample_count >= 3` (MIN_SAMPLES cold-start gate)
- `freshness: FRESH | AGING` (not STALE/EXPIRED/SUPERSEDED)
- `adjustments` field non-empty

## Inspect stats

```bash
python _shared/scripts/param-learner.py --stats
python _shared/scripts/param-learner.py --get code-generation
```

## Reset a profile

```bash
python _shared/scripts/param-learner.py --reset code-generation
```

## Privacy note

Profile files contain only numeric parameter values and aggregate counts — no receipt content, no user data, no task descriptions.
