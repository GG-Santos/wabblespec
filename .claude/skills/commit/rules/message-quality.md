# Message Quality

Quality gates for commit messages. Applied in Commit write mode Step 3–4.

## Subject line quality gates

**Length:** Total subject line (type + scope + `: ` + description) must be ≤ 72 characters. Messages that exceed this are truncated in most git UIs and are a FAIL.

**Imperative mood:** The description verb must be imperative (command form): "add", "fix", "remove", "update", "extract", "rename". Not "added", "adds", "adding".

Test: the description should complete the sentence "If applied, this commit will _____." A description that completes this sentence is in the right form.

**No period:** Subject line does not end with a period or any punctuation.

**No "and" in subject:** If you need "and," the commit should be split.

## Why-not-what rule for bodies

The commit body explains WHY, not what. The diff already shows what. The body adds context a reader cannot derive from the diff.

**What (do not write):**
- "Changed the authentication handler to use PKCE"
- "Updated the config to set max_connections to 100"
- "Renamed UserService to AccountService"

**Why (write this instead):**
- "PKCE is required for public clients per OAuth 2.0 Security BCP (RFC 9700). Mobile apps cannot keep secrets, making the authorization code flow with client secret unsafe."
- "Connection pool saturation was causing request queue buildup under load (observed in staging at 200 RPS). 100 connections saturates the DB connection limit for our plan."
- "AccountService is a more accurate name — the service manages the full account lifecycle, not just user authentication."

## When a body is required

A body is required when:
- The reason for the change is not obvious from the diff
- The change addresses a non-obvious constraint, bug, or decision
- The change is a breaking change (body must describe what breaks and what consumers must do)
- The change is a security fix (body should describe the class of vulnerability and the fix approach, without exploit details)

A body is optional when:
- The change is self-evident from the diff and the subject
- The change is mechanical (dependency bump, formatting, renaming that follows an obvious pattern)

## Body formatting

- Blank line between subject and body
- Wrap at 72 characters per line
- Use present tense in the body ("This allows..." not "This allowed...")
- Multiple paragraphs are allowed; separate with a blank line

## Breaking change footer format

A breaking change footer must:
1. State what the breaking change is (concisely)
2. State what consumers must do to adapt (specifically)
3. Reference migration documentation if available

Format:
```
BREAKING CHANGE: Removed the `user_id` field from the auth token payload.
Consumers must use `account_id` instead. Update all JWT decode references.
See docs/migration/v2-auth.md for a full migration guide.
```
