# EARS Syntax

Easy Approach to Requirements Syntax. Consumers: specify. Source: Mavin et al., 2009.

## The five EARS templates

### Ubiquitous (always active)
```
The <system> shall <system response>.
```
Example: "The API shall return a JSON response for all requests."

---

### Event-driven (triggered by external event)
```
WHEN <optional precondition> <trigger> THE <system> SHALL <system response>.
```
Example: "WHEN the user submits the login form, THE authentication service SHALL validate credentials within 500ms."

---

### Unwanted behaviour (error/exception handling)
```
IF <optional precondition> <trigger>, THEN THE <system> SHALL <system response>.
```
Example: "IF the database connection fails, THEN THE system SHALL return a 503 status code and log the error."

---

### State-driven (conditional on system state)
```
WHILE <system state>, THE <system> SHALL <system response>.
```
Example: "WHILE the queue depth exceeds 1000, THE consumer SHALL throttle ingestion to 100 items per second."

---

### Optional feature (feature-gated)
```
WHERE <feature is included>, THE <system> SHALL <system response>.
```
Example: "WHERE the analytics module is enabled, THE event tracker SHALL record user interactions to the events table."

---

## Quality rules for EARS requirements

1. **One requirement per statement.** No "and" connecting two different behaviors.
2. **Testable.** A QA engineer can write a test that confirms the requirement is met or not met.
3. **No implementation.** Specify behavior, not how to achieve it. "shall validate" not "shall call bcrypt".
4. **Named subject.** The `<system>` must be a specific named component, not "the system" generically.
5. **Measurable when quantifiable.** "within 500ms" not "quickly". "< 1% error rate" not "low error rate".

## Acceptance criteria format

For task cards, acceptance criteria map directly to EARS:

```
AC-1: WHEN <trigger>, THE <module> SHALL <behavior>.
AC-2: IF <error condition>, THEN THE <module> SHALL <recovery>.
AC-N: ...
```

Each criterion gets a unique ID. The verify receipt checks each criterion by ID.

## Common anti-patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| "The system should..." | "should" is ambiguous — optional or required? | Use "shall" (required) or document as optional feature |
| "...in a timely manner" | Untestable | Add a measurement: "...within 200ms" |
| "The system shall handle errors" | No specified response | "...shall return error code X and log the exception" |
| "Authentication and authorization shall..." | Two behaviors | Split into two EARS statements |
