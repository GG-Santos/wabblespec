---
name: guard-no-force-push
enabled: true
event: bash
pattern: git\s+push\s+.*--force(?!-with-lease)
action: block
---

BLOCKED: Force push detected.

Force pushing overwrites upstream history and can destroy collaborators' work.

Safer alternative:
- `git push --force-with-lease` — fails if upstream has new commits (safe force push)
- `git push` after `git rebase origin/main` — rebase instead of force

If you need to force push main/master: this requires explicit human approval. Stop and ask the user to confirm.

WabbleSpec guard rule — destructive git operation prevention.
