---
name: command-risk-policy
description: WabbleSpec command risk classification policy. Defines SAFE/WARN/BLOCK tiers for shell commands found in wave plan steps. Consumed by Guard Layer 5. Adapted from destructive_command_guard-main core packs (git, filesystem, database).
---

# Command Risk Policy

Guard Layer 5 classifies shell commands in wave plan steps against this policy before a wave executes. Classification is pattern-based. Safe patterns take precedence — if a command matches a SAFE exception, it is not reclassified upward even if a BLOCK pattern also matches.

## Classification Tiers

| Tier | Meaning | Guard action |
|---|---|---|
| `SAFE` | Read-only, dry-run, or explicitly scoped to temp paths. No persistent state change. | Allow — no annotation required |
| `WARN` | Potentially destructive but contextually justified. Requires human-readable rationale in the wave plan step. | Allow with annotation — Guard adds WARN flag to receipt; wave may proceed; Executor logs rationale |
| `BLOCK` | Irreversible or high-blast-radius operation. Cannot proceed without explicit human attestation outside the wave plan. | HARD error — abort wave; return typed error with safer alternative |

**SAFE exception rule:** A command that matches a SAFE pattern is classified SAFE even if it also partially matches a WARN or BLOCK pattern. Safe patterns are listed first in each category.

## Category: Git

### SAFE — no classification needed

| Pattern | Reason |
|---|---|
| `git checkout -b <branch>` | Branch creation — no work destruction |
| `git checkout --orphan <branch>` | Orphan branch — no work destruction |
| `git restore --staged <path>` | Index only — working tree unchanged |
| `git restore -S <path>` | Index only — working tree unchanged |
| `git clean --dry-run` or `git clean -n` | Preview only — no deletion |
| `git stash list` | Read-only |
| `git log`, `git status`, `git diff`, `git show` | Read-only |
| `git fetch` | Remote read — no local ref change |
| `git branch -m` | Rename only — no deletion |
| `git push` without `--force` or `--force-with-lease` | Normal publish |

### WARN — requires rationale annotation in wave plan step

| Pattern | Risk | Required annotation |
|---|---|---|
| `git push --force-with-lease` | Overwrites remote if lease passes | State which branch and why force is needed |
| `git stash drop` or `git stash clear` | Stash loss | Confirm stash content is already applied or not needed |
| `git branch -d <branch>` | Branch deletion (safe if fully merged) | Confirm branch is merged or work is preserved |
| `git clean -f` without `-d` | Untracked file deletion | Confirm files are generated/temporary |
| `git rebase` without `--abort` | History rewrite on current branch | Confirm no upstream consumers |
| `git commit --amend` | History rewrite | Confirm commit not yet pushed |

### BLOCK — abort wave; require human attestation

| Pattern | Risk | Safer alternative |
|---|---|---|
| `git push --force` or `git push -f` | Overwrites remote permanently — upstream consumers lose history | Use `--force-with-lease` to check concurrent pushes |
| `git checkout -- <path>` or `git restore <path>` (working tree) | Discards uncommitted changes permanently | Use `git stash` to save changes first |
| `git reset --hard` | Discards all uncommitted changes permanently | Use `git stash` or `git reset --soft` |
| `git clean -fd` or `git clean -fdx` | Deletes untracked files and directories permanently | Run `git clean --dry-run` first to preview |
| `git branch -D <branch>` | Force-deletes branch regardless of merge state | Use `git branch -d` (merged check) or verify work is preserved |
| `git filter-branch` or `git filter-repo` | Rewrites entire history | Requires out-of-band human approval — not a wave operation |

## Category: Filesystem

### SAFE

| Pattern | Reason |
|---|---|
| `rm` targeting `/tmp/`, `$TMPDIR/`, or `.wabblespec/tmp/` | Scoped to temp paths |
| `rm -ri` | Interactive mode — user confirms each file |
| `ls`, `find`, `cat`, `head`, `tail` | Read-only |
| `mkdir -p` | Additive only |
| `cp` without `-r` on large directories | Low blast radius |
| `mv` within same project directory | Reversible by moving back |

### WARN

| Pattern | Risk | Required annotation |
|---|---|---|
| `rm <specific-file>` without `-r` | Single file deletion | Confirm file is generated or expendable |
| `rm -r <build-output-dir>` | Build artifact deletion | Confirm path is a generated output directory |
| `mv <file> <destination>` across directories | Relocation | Confirm destination and rollback path |
| `chmod -R` | Permission change on tree | Confirm scope and reversibility |
| `truncate` or `> file` (redirect) | File content overwrite | Confirm file is not a source artifact |

### BLOCK

| Pattern | Risk | Safer alternative |
|---|---|---|
| `rm -rf /` or `rm -rf ~` or `rm -rf $HOME` | Total filesystem destruction | Never valid in a wave — reject immediately |
| `rm -rf .` from project root | Deletes entire project | Scope to a specific subdirectory |
| `rm -rf <path>` outside temp and outside declared project scope | High-blast unscoped deletion | Run `find <path> -type f \| head -20` to preview first |
| `shred`, `wipe`, `srm` | Secure deletion — unrecoverable | Not valid in wave operations |

## Category: Database / Migration

### SAFE

| Pattern | Reason |
|---|---|
| `SELECT`, `EXPLAIN`, `SHOW`, `DESCRIBE` | Read-only |
| Migration `--dry-run` or `--pretend` flags | Preview only |
| Schema inspection queries | No state change |

### WARN

| Pattern | Risk | Required annotation |
|---|---|---|
| `ALTER TABLE ADD COLUMN` | Additive schema change | Confirm migration is reversible (has down migration) |
| `CREATE TABLE`, `CREATE INDEX` | Additive DDL | Confirm down migration exists |
| `INSERT INTO` in migration script | Data seeding | Confirm idempotent (no duplicate risk) |
| `UPDATE` with `WHERE` clause | Row modification | Confirm scope of affected rows |

### BLOCK

| Pattern | Risk | Safer alternative |
|---|---|---|
| `DROP TABLE` or `DROP DATABASE` | Data loss — irreversible without backup | Verify backup exists; use two-phase migration: deprecate first, drop later |
| `DELETE FROM` without `WHERE` | Full table deletion | Add `WHERE` clause or use `TRUNCATE` with explicit confirmation |
| `TRUNCATE TABLE` | All rows deleted — DDL-level, not transactional in some engines | Require explicit attestation outside the wave |
| `ALTER TABLE DROP COLUMN` | Data loss for that column — irreversible without restore | Use two-phase migration: mark deprecated, then drop in later wave |
| Migration rollback scripts that `DROP` | Rollback destroys data | Confirm rollback is safe before marking rollback available |

## Category: Process / Network

### SAFE

| Pattern | Reason |
|---|---|
| `kill -0 <pid>` | Existence check only — no signal sent |
| `curl --dry-run` or `wget --spider` | No side effects |
| Read-only network checks (`ping`, `nslookup`, `dig`) | No state change |

### WARN

| Pattern | Risk | Required annotation |
|---|---|---|
| `curl -X POST` or `curl -X PUT` to external service | External state change | Confirm endpoint, payload, and idempotency |
| `kill <pid>` (default SIGTERM) | Process termination — may have dependents | Confirm process identity and restart plan |
| `pkill <name>` | Pattern-matched termination | Confirm pattern scope |

### BLOCK

| Pattern | Risk | Safer alternative |
|---|---|---|
| `kill -9` or `kill -SIGKILL` | Immediate process kill — no cleanup | Use SIGTERM first and wait for graceful exit |
| `killall <name>` | Kills all matching processes — unscoped | Use `pkill` with `-n` (newest) or PID-targeted kill |
| `curl` or `wget` to authentication endpoints without explicit approval | Credential exposure or unintended auth state change | Require human review before any auth endpoint call in wave |

## Policy Application Rules

1. **Safe exceptions first.** Check all SAFE patterns before BLOCK or WARN. A SAFE match terminates classification for that command.
2. **Multiple commands in one step.** Classify each command independently. Highest tier wins for the step: one BLOCK command in a step blocks the entire step.
3. **Piped commands.** Classify each segment. `find . -name "*.tmp" | xargs rm -rf` is BLOCK because `xargs rm -rf` is BLOCK.
4. **Variables and wildcards.** Commands with unresolved shell variables or `*` in file paths that reach WARN or BLOCK threshold are escalated one tier. `rm -rf $UNKNOWN_PATH` → BLOCK regardless of SAFE exception.
5. **Actionable error messages.** Every BLOCK response MUST include the safer alternative from this table. "Command blocked" alone is not a valid Guard error.
6. **Not a complete catalog.** This policy covers core WabbleSpec execution patterns. Novel commands not matching any pattern default to WARN — require annotation, do not auto-block.
