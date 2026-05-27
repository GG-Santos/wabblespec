# UX Principles

## User Mental Models

Target mental model declared per major flow in spec at P1:

```markdown
## User Mental Model — <flow name>

**Assumed model:** <what the user expects based on prior experience>
**Actual model:** <how the system actually works>
**Gap:** <where they diverge>
**Bridge strategy:** <how the UI helps the user cross the gap>
```

No undeclared mental model gaps. If the system behaves differently from user expectations, the gap is declared and the bridge strategy is documented.

## Affordances

Interactive elements visually communicate their affordance:
- Buttons look clickable (visual weight, color, cursor)
- Links look followable (underline, color, cursor)
- Inputs look fillable (border, background, placeholder)
- Drag handles look draggable (grip icon, cursor)

No interactive element that looks non-interactive. No non-interactive element that looks interactive.

## Feedback

Every user action has feedback within 100ms perceived. For actions that take longer:

| Duration | Required response |
|---|---|
| 0–100ms | No indicator needed |
| 100ms–1s | Spinner or progress indication |
| > 1s | Progress indicator with cancellation option if possible |
| > 10s | Time estimate if knowable |

No silent actions. No action that completes without any visible state change.

## Error States

Every error has a message. Every message has a recovery path:

| Error type | Required elements |
|---|---|
| Validation error | Inline, near the field, explains what is wrong and how to fix |
| Network error | User-facing message, retry option, what data was lost (if any) |
| Not found | Explanation, navigation path back to safety |
| Permission error | Explanation, path to request access or contact admin |
| System error | Apology, reference ID for support, what the user can do now |

Generic "Something went wrong" without a recovery path is not an acceptable error state.

## Audit Gates

- [ ] User mental model declared per major flow
- [ ] All interactive elements have correct affordance signals
- [ ] Feedback timing declared per action type
- [ ] Every error type has a message and a recovery path
- [ ] No silent actions
