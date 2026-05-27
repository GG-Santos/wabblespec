# Design Gateway — User Flows Reference

User flow completeness requirements: error states, empty states, and loading states.

## Flow completeness requirement

A spec is incomplete if it only describes the happy path. Every user flow must declare all states.

### Required states for every flow

| State | Description | Spec requirement |
|---|---|---|
| Loading | Data is being fetched or action is being processed | Declare loading treatment |
| Empty | No data yet, or user has cleared/deleted all items | Declare empty state content |
| Error | Operation failed, network unavailable, permission denied | Declare error treatment per error type |
| Partial/degraded | Some data loaded, some failed | Declare how partial states are presented |
| Success | Operation completed; data loaded | The happy path |
| Offline | Device has no network | Declare offline behavior |

A flow spec that only documents the success state is a 20% complete spec.

## Loading states

Loading states must be designed, not left to the framework's default.

### Skeleton screens

For content-heavy views (feeds, lists, cards):

```
┌─────────────────────────┐
│ ████████████  ████████  │  ← title skeleton
│ ██████████████████████  │  ← body skeleton line
│ ████████████████        │  ← body skeleton line (shorter)
└─────────────────────────┘
```

Rules:
- Skeleton must match the shape of the real content (same number of lines, same proportions)
- Animate with a subtle shimmer or pulse (if `prefers-reduced-motion` is not set)
- Do not show skeleton for loads expected to complete in < 300ms — sudden appearance is jarring

### Loading indicators

For actions with unknown output shape (form submission, file upload):
- Button: show spinner inside the button; disable button; keep label visible or replace with "Saving..."
- Full-page: centered spinner + descriptive label for what is happening
- Progress bar: for operations where progress can be measured (file upload, multi-step process)

Spec must declare: which loading indicator is used per interaction type.

## Empty states

Empty states are opportunities. Every empty state must answer: what does the user do next?

### Empty state components

```
┌─────────────────────────┐
│         [Icon]          │  ← contextual illustration or icon
│                         │
│    Nothing here yet     │  ← headline: factual, not apologetic
│                         │
│  Create your first      │  ← supportive text: what this feature does
│  project to get started │
│                         │
│  [Create project]       │  ← primary action; the next step
└─────────────────────────┘
```

Types of empty states:

| Type | Example | Primary action |
|---|---|---|
| First-use | No projects created | Create first item |
| No results | Search returned nothing | Modify search / clear filters |
| Cleared | User deleted everything | Undo or start fresh |
| No permission | User has no access | Request access or contact admin |
| Error-caused | Failed to load | Retry / report issue |

Spec must declare: which empty state type applies to each list/grid view and what the primary action is.

## Error states

Every error must tell the user: what went wrong, whether it is their fault or the system's fault, and what to do next.

### Error categories and treatment

| Category | Examples | Treatment |
|---|---|---|
| User error | Invalid form field, wrong credentials | Inline validation; specific field highlight; actionable message |
| Not found | Page or resource doesn't exist | 404 page with navigation options |
| Permission denied | Access to a resource the user doesn't own | Explain why; offer path to get access if possible |
| Network error | Connection lost, request timed out | Retry button; explain offline status |
| Server error | 500 from the API | Apologetic tone; retry option; status page link |
| Rate limited | Too many requests | Explain limit; countdown to retry |

### Error message writing rules

| Rule | Wrong | Right |
|---|---|---|
| Be specific | "An error occurred" | "Could not save: file is larger than 10MB" |
| No blame | "You did not fill in the required fields" | "Please fill in these required fields" |
| Action-oriented | "Error: invalid password" | "Incorrect password. Try again or reset your password." |
| No jargon | "HTTP 403 Forbidden" | "You don't have permission to view this page" |
| No exclamation marks | "Error! Login failed!" | "Login failed. Check your password and try again." |

### Global error boundary

Every web application must have a global error state for uncaught errors:

```
Something went wrong

We're sorry — something unexpected happened.
Your work has been saved. Refresh the page to continue.

[Refresh page]  [Report this issue]
```

This must be distinct from the 404 page and from inline field errors.

## Flow documentation format

Spec must document each user flow as:

```markdown
## Flow: {flow name}

**Entry point**: {where the user starts this flow}
**Goal**: {what the user wants to accomplish}
**Exit**: {where the user ends up after success}

### Happy path
1. {Step 1}
2. {Step 2}
3. {Step 3}

### States

| State | Trigger | UI treatment |
|---|---|---|
| Loading | User submits form | Button shows spinner; form disabled |
| Success | Response 200 | Toast notification; redirect to /dashboard |
| Validation error | Missing required field | Inline error below each failing field; focus first error |
| Server error | Response 500 | Error banner above form; retry button; form re-enabled |
| Network offline | Navigator.onLine = false | "You're offline" banner; form still usable; queued on reconnect |

### Edge cases
- {Unusual but possible scenario and how it is handled}
```
