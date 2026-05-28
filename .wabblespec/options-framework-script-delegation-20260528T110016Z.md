# Options: Script Delegation for Receipt/Changelog/VERSION Writes

**stage:** P1
**target:** Library-Package (WabbleSpec framework skills)
**generated_at:** 2026-05-28T11:00:16Z
**recommendation:** Option 1, with Option 2 as immediate follow-on

---

## Context

9 SKILL.md files reference changelog, VERSION, or receipt operations. Zero call the Python scripts built to eliminate manual file I/O. `archive.py` was explicitly designed to replace a 98KB+18KB CHANGELOG+receipt-index read loop, but `archive/SKILL.md` still instructs Claude to do all four operations manually. The scripts exist; the skills don't use them.

Guard SKILL.md is currently locked under `wave-checkpoint-v1` — Option 3 is blocked this session.

---

## Option 1: Rewrite SKILL.md steps to invoke scripts via Bash

**Summary:** Replace manual file I/O prose steps in affected skills with explicit `python script.py --args` Bash call sequences.

**How it works:** Each affected SKILL.md "how to do it" step that currently says "append to CHANGELOG.md", "bump VERSION", or "write receipt JSON" is replaced with the exact `python .wabblespec/engine/shared/scripts/<script>.py --flag value` call. Claude provides reasoning-dependent fields (summary, delta class, session ID) as CLI args and the script handles all structure, schema enforcement, and file I/O.

**Tradeoffs:**
| Dimension | Assessment |
|---|---|
| Complexity | Medium — 9 skills need targeted rewrites; no new infrastructure |
| Time to implement | 1 session covering all 9 affected skills |
| Risk | Low — scripts already exist and are tested; rewrites are SKILL.md text changes |
| Reversibility | Easy — revert SKILL.md text |
| Fits scope | Yes — framework skill authoring is product space |

**When to choose this:** The scripts exist and are correct. The only missing piece is that SKILL.md steps don't invoke them. This is the lowest-effort, highest-payoff fix.

**When NOT to choose this:** If the scripts have untested failure modes that would block execution — audit scripts before committing.

---

## Option 2: Add a shared reference declaring script delegation as mandatory

**Summary:** Write `_shared/references/script-delegation-contract.md` mapping every standard operation to its canonical script call, then route all relevant SKILL.md sections to this reference.

**How it works:** A single reference file lists the three canonical script calls (receipt-writer.py, archive.py, changelog-append.py / version-bump.py) with full example invocations. Each affected SKILL.md adds a Reference Routing table pointing to this file and removes the inline prose. New skills authored via Factory inherit the routing by default.

**Tradeoffs:**
| Dimension | Assessment |
|---|---|
| Complexity | Low-Medium — one new reference file; routing table updates to 9 skills |
| Time to implement | 1 session |
| Risk | Low — documentation change; no behavioral risk if skills still have fallback prose |
| Reversibility | Easy |
| Fits scope | Yes, but note: the reference file is new infrastructure; creating new reference files is out of scope for `toprank-integration-phase1` |

**When to choose this:** Best as a follow-on to Option 1 — prevents future skills from re-introducing manual steps after existing skills are fixed.

**When NOT to choose this:** Alone, without Option 1, this adds documentation without fixing the existing skills.

---

## Option 3: Guard layer intercept on manual framework file writes

**Summary:** Extend Guard's pre-tool-use hook to emit COMMAND_RISK when Edit/Write targets canonical framework artifacts without a script caller in the call chain.

**How it works:** Guard hook checks tool call destination against a watchlist (CHANGELOG.md, VERSION, state/receipts/*.json). If the caller is Claude's Edit/Write tool rather than a Python script subprocess, Guard emits a warning before the write lands.

**Tradeoffs:**
| Dimension | Assessment |
|---|---|
| Complexity | High — hook modification, pattern matching, false-positive handling |
| Time to implement | Multi-session |
| Risk | Medium — false positives possible; Python file I/O bypasses Claude tool layer entirely |
| Reversibility | Medium — hook changes need careful rollback |
| Fits scope | No — Guard SKILL.md is locked under `wave-checkpoint-v1` this session |

**When to choose this:** When Option 1+2 have been in place for several sessions and drift is re-occurring.

**When NOT to choose this:** Now — Guard is locked and this addresses symptom rather than root cause.

---

## Option 4: Archive.py as sole completion path — prose steps become input-prep only

**Summary:** Redesign Archive SKILL.md so all steps terminate in a single `archive.py` invocation; steps are input-gathering only, never direct file writes.

**How it works:** The 10-step Archive SKILL.md is restructured: Steps 1-3 gather/reason about inputs (receipts, delta class, not-tested list), and Step 4 is a single `python archive.py --session-id ... --summary ... --delta-class ...` call. The script handles CHANGELOG, VERSION, receipt-index, and delivery receipt in one pass without any of those files entering context.

**Tradeoffs:**
| Dimension | Assessment |
|---|---|
| Complexity | Medium — Archive-specific; deeper restructure than a step replacement |
| Time to implement | Less than 1 session for Archive alone |
| Risk | Low — archive.py already implements this contract exactly |
| Reversibility | Easy |
| Fits scope | Yes — and this is the highest-value single skill to fix given CHANGELOG is 98KB+ |

**When to choose this:** As a focused first fix before the broader Option 1 pass, given Archive has the worst token cost (98KB CHANGELOG read).

**When NOT to choose this:** If you want a uniform fix across all 9 skills in one pass — Option 1 subsumes this.

---

## Recommendation

**Option 1**, with **Option 2** as the natural follow-on in the same session.

Option 1 directly fixes the existing problem across all 9 affected skills with no new infrastructure. The scripts exist, are documented, and are tested — the only missing piece is that SKILL.md steps don't invoke them. This is a mechanical rewrite: identify the "write to file" step, replace with the corresponding script call and the args Claude is responsible for. Done.

Option 2 prevents the problem from recurring in new skills. It is cheap (one reference file, routing tables) and pairs cleanly with Option 1 in a single session.

Option 3 is blocked (Guard locked) and is a trailing enforcement mechanism, not the fix. Option 4 is subsumed by Option 1. Option 5 requires schema work that isn't justified until Option 1 proves insufficient.

**Note:** This recommendation is advisory. The selected option becomes the input to Specify.
