# Safety-Sensitive Overlay

Extends `templates/skill/base-universal.md`. Use for high-stakes or dual-use
categories.

## Domain Operating Model

Define allowed help, disallowed help, and safe redirects for the specific risk
area.

## Request Triage

Check whether the request asks for operational harm, evasion, concealment,
abuse, self-harm, or high-stakes personal direction.

## Workflow

1. Preserve benign intent when possible.
2. Refuse only the unsafe slice.
3. Provide a safe transform.
4. Guard against over-refusal of education, prevention, authorized defense, or
   non-operational fiction.

## Output Contract

Include `boundary`, `allowed_help`, `blocked_request`, and `safe_redirect`.

## Examples And Edge Cases

Cover clearly safe, clearly unsafe, mixed-intent, and ambiguous requests.

## Failure Modes

Operational enablement, over-refusal, vague refusal, and unsafe details inside a
safe wrapper.
