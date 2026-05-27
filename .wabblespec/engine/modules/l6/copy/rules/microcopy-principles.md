# Microcopy Principles

Rules for all UI micro-text categories. Applied in Copy Step 2.

## Universal rules

1. **Specific over generic.** "Save failed — disk full" beats "An error occurred." Name the problem.
2. **Action-oriented.** Every error, warning, and empty state includes what the user can do next.
3. **User's words, not system's.** Write what the user calls things, not what the code calls them.
4. **No blame.** Errors never say "you did" or "invalid input." State what happened; state the fix.
5. **No ellipsis in UI text.** "Loading..." is a habit. "Loading" is cleaner and sufficient.

## Category rules

### Labels
- Noun or noun phrase preferred: "Email address" not "Enter your email address"
- Title case for noun labels: "First Name" not "first name"
- Verb labels (buttons, links) are imperative: "Save" "Cancel" "Delete account"
- Button verbs match the outcome: "Delete" not "OK" for destructive actions

### Errors
- Headline: what happened (specific, past tense)
- Body: how to fix it (specific, imperative)
- CTA: the action that resolves it (if applicable)
- Format: `{What happened}. {How to fix it}.`
- Example: "Payment declined. Check that your card number and expiry date are correct."

### Tooltips
- One sentence maximum
- Answers "what is this?" not "how do I use it?"
- No period at the end (tooltip is a label, not a sentence)
- Do not repeat the label: if the label says "API Key," the tooltip does not start with "Your API key..."

### Empty states
- Never: "No data available" "Nothing to show" "Empty"
- Always: what this section is for + what the user can do to fill it
- Example: "No projects yet. Create your first project to start tracking work."

### Confirmations
- State what will happen, not what the user is doing
- For irreversible actions: state that it is irreversible
- Format for destructive: `{Consequence}. This cannot be undone. {confirmation action}.`
- Example: "This will permanently delete all project data. This cannot be undone."
- Confirm button label: "Delete" not "OK" or "Yes" — action verb that matches the consequence

### Security warnings
- See `rules/security-warning-format.md` for full specification
- Security warnings are never dismissable without acknowledgment
- Always name the specific risk; never generic "this may be unsafe"
