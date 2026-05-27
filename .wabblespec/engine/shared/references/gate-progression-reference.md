# Gate Progression Reference

**Consumed by:** l2/recipe (activation routing), l2/executor (wave planning), l2/grader (audit), l2/reviewer (violation routing)  
**Purpose:** Documents how L1–L8 gates chain for each major workflow type. Recipe consults this when assembling the module activation list for a task card. Grader uses it to audit whether the correct gates ran.

---

## How gate progression works

1. **Recipe** reads the task card, detects the platform (L3), and derives the activation list from this reference.
2. **Guard** runs before every Executor wave — it is never listed explicitly because it is always present.
3. **L4 gateways** activate based on platform signals and task type, not always together.
4. **L8/Archive** accumulates every delivery into the receipt corpus — it always runs at task close.

The progression below shows which modules are required at each layer. "Optional" means the module activates only when the specified signal is present.

---

## Workflow type: New Feature

**Commit type:** `feat`  
**delta_class:** ADDITIVE  
**SemVer bump:** MINOR  
**Archive Shift trigger:** Yes

### L1 — Specification
| Module | Required | Signal |
|---|---|---|
| Plan | Yes | Always first — task card and recipe |
| ScopeFrame | Yes | Establishes in-scope / out-of-scope boundary |
| Specify | Yes | Locks acceptance criteria before Executor |
| Brainstorm | Optional | When solution approach is not yet clear |
| Enhance | Optional | When input spec needs elaboration |
| Explore | Yes | Project-map.md must be FRESH before Executor |

### L2 — Orchestration
| Module | Required |
|---|---|
| Recipe | Yes |
| Guard | Yes (before every wave) |
| Executor | Yes |
| Verifier | Yes |
| Archive | Yes (closes task) |

### L3 — Platform
Load the platform module matching the build target. One module per task.

### L4 — Gateways
| Gateway | Required | Activation signal |
|---|---|---|
| Engineering | Yes (Medium+ complexity) | Always for new features |
| Security | Yes | Any new endpoint, auth change, or external input |
| AI | Yes | Platform = AI-Agent or LLM SDK detected |
| Aesthetic | Optional | Platform has visual components |
| Design | Optional | 10+ components or accessibility-affecting UI |
| Experience | Optional | P1 user-research scope declared |

### L5 — Memory
| Module | Required | Signal |
|---|---|---|
| Memory | Optional | Research evidence cited in spec |
| EntityGraph | Optional | New entities introduced |
| Provenance | Optional | Evidence chain tracking needed |
| Nexus | Optional | Why-query or blast-radius analysis needed |

### L6 — Polish
| Module | Required | Signal |
|---|---|---|
| Polish | Yes | Runs on all completed output |
| Proofread | Optional | User-facing copy present |
| Document | Optional | Feature requires documentation update |

### L7 — Delivery
| Module | Required | Signal |
|---|---|---|
| Commit | Yes | Code changes to commit |
| Monitor | Yes | SLO declarations present in engineering spec |
| Changelog | Yes | Before release |
| Package | Optional | Distributable artifact generated |
| Release | Optional | Version tag to publish |
| Deploy | Optional | Deployment to an environment |
| Scaffold | No | Only on project creation |

### L8 — Archive
Archive always runs. Verifier receipt + Executor receipt → delivery receipt → receipt corpus.

---

## Workflow type: Bug Fix

**Commit type:** `fix`  
**delta_class:** NON_BREAKING  
**SemVer bump:** PATCH  
**Archive Shift trigger:** No

### Differences from New Feature

**L1:** Brainstorm and Enhance rarely needed. Explore required only if project-map is STALE or EXPIRED. Specify may be abbreviated for small fixes.

**L4 gateways:**
- Engineering: Yes — coverage floor and complexity still apply
- Security: Only if the bug is security-related (input handling, auth, injection)
- AI: Only if the fix is in AI code paths
- Aesthetic / Design / Experience: Only if the fix affects UI behavior

**L5:** Memory rarely consulted unless the bug requires understanding historical evidence.

**L6:** Polish required. Document only if the fix changes documented behavior.

**L7:** Commit required. Monitor only if SLOs are affected. Changelog entry (Fixed section). Package/Release/Deploy only if the fix needs immediate deployment.

**Key constraint:** Bug fix commit must not include feature work. If the fix requires refactoring that adds new capability, split into separate commits (Commit module enforces this).

---

## Workflow type: Security Patch

**Commit type:** `security` (or `fix` with `security:` scope)  
**delta_class:** NON_BREAKING (BREAKING if the patch changes an API)  
**SemVer bump:** PATCH (or MAJOR if breaking)  
**Archive Shift trigger:** No (or Yes if BREAKING)

### Differences from Bug Fix

**Priority:** Security patches interrupt the normal sprint queue. No deferral — CVE in a direct dependency or in code is a BLOCK.

**L4 gateways:**
- Security: **Always** — Phase A (STRIDE re-analysis of the affected surface) + Phase B (verdict)
- Engineering: Yes — CVE audit must show zero high/critical after patch

**L7:**
- Changelog entry goes in the **Security** section (never buried in Fixed)
- Release: if the patch is in a published library or distributed artifact, publish immediately — do not wait for the next scheduled release
- Deploy: if in a deployed service, deploy to production after staging verification; Attestation required

**L4/Security Phase A additional check:** Verify the CVE is not also present in any transitive dependency that is not upgraded by this patch. If it is, open a separate ticket — do not silently leave it.

---

## Workflow type: Breaking Change

**Commit type:** Any type with `!` suffix or `BREAKING CHANGE:` footer  
**delta_class:** BREAKING  
**SemVer bump:** MAJOR  
**Archive Shift trigger:** Yes (Nexus refresh required)

### Differences from New Feature

**L1:** Specify must explicitly declare the breaking change in acceptance criteria. ScopeFrame must list all callers and consumers affected — blast-radius analysis via Nexus before Executor.

**L2:**
- Executor wave plan must include migration path for affected callers
- Verifier checks that backward compatibility is NOT preserved (breaking means broken intentionally — verify it is actually broken for old callers, not accidentally backwards-compatible)

**L4 gateways:**
- Engineering: Yes — API surface change must be reflected in breaking-change-detection CI gate (API Extractor / semver-checks)
- Security: If the break changes auth or trust boundaries
- Experience: If the break affects user workflows — UX migration path required

**L5:**
- Provenance: cascade required (BREAKING delta triggers cascade per Provenance SKILL.md, 2-hop limit)
- Nexus: blast-radius query before Executor; post-Archive Nexus refresh mandatory

**L6:**
- Document: Required — breaking changes must be documented with migration guide
- Changelog: BREAKING CHANGE entry in Changed section with "Breaking:" prefix; migration guide linked

**L7:**
- Commit: BREAKING CHANGE footer required in commit message body
- Changelog: Entry promoted to Changed section; Breaking: prefix; no omission
- Release: Major version tag; release notes must include migration guide
- Deploy: If deployed service, staged rollout recommended; rollback plan required before activation

---

## Workflow type: Dependency Upgrade

**Commit type:** `chore(deps)` or `fix(deps)` (security)  
**delta_class:** NON_BREAKING (or BREAKING if upgrade changes behavior)  
**SemVer bump:** PATCH (or MAJOR if behavior breaks callers)  
**Archive Shift trigger:** No

### Gate activation

**L1:** Plan optional for small upgrades. Specify not required. A task card is still needed — use a minimal one declaring which deps are being upgraded and the rationale.

**L2:** Guard + Executor + Verifier + Archive — standard.

**L3:** Platform module not required unless the upgrade affects platform-specific behavior.

**L4 gateways:**
- Engineering: **Always** — dependency-standards.md checks run; upgrade must clear N-2 and CVE audit
- Security: If the upgrade is a CVE patch — follow Security Patch workflow instead
- Others: Not required unless the dep affects the platform surface

**L5/L6:** Memory and Polish not required for pure dep upgrades.

**L7:**
- Commit: Required. Body must explain WHY (security, unblock feature, EOL avoidance) and reference upstream CHANGELOG
- No Changelog entry required for routine dep upgrades (chore — excluded from user-facing release notes)
- No Release or Deploy unless the upgrade fixes a production CVE

**Key constraint:** Dep upgrades are separate commits — never bundled with feature work. One dep family per commit (e.g. all `@babel/*` packages together, not mixed with unrelated deps).

---

## Workflow type: Refactor

**Commit type:** `refactor`  
**delta_class:** NON_BREAKING  
**SemVer bump:** PATCH  
**Archive Shift trigger:** No

### Gate activation

**L1:** Specify required only if the refactor changes module boundaries. Explore required if project-map is stale.

**L4 gateways:**
- Engineering: **Yes** — coverage floor and complexity gates; refactors that reduce complexity are validated here
- Security: Only if refactor touches auth or input handling paths
- Others: Not required

**L5:** EntityGraph may be updated if the refactor changes entity relationships.

**L6:** Polish required. Document not required unless public API documentation needs updating.

**L7:** Commit required. No Changelog entry (refactor excluded from user-facing notes).

**Key constraint:** Refactor commits must not introduce new capability. If the refactor requires a new helper that could be reused elsewhere, extract it in a separate ADDITIVE commit.

---

## Workflow type: Documentation Update

**Commit type:** `docs`  
**delta_class:** NON_BREAKING  
**SemVer bump:** PATCH  
**Archive Shift trigger:** No

### Gate activation

**L1:** Specify not required. ScopeFrame confirms which docs are in scope.

**L4 gateways:** Not required. Engineering gateway skips for docs-only changes (no code = no coverage or complexity to check).

**L5:** If the docs update is triggered by new research: ResearchLog + Memory write.

**L6:** Polish, Proofread, Markdown — all may activate. Legal if the docs include legal copy (ToS, privacy). Document activates as the primary module for this workflow.

**L7:** Commit required. No Changelog entry unless the docs change describes a previously-undocumented user-facing behavior.

---

## Guard is always present

Guard does not appear in any workflow type above because it is universal — it runs before every Executor wave regardless of workflow type. It is not "activated" by Recipe; it is enforced by the pre-tool-use hook independently.

---

## Cross-references

- `.wabblespec/engine/shared/references/module-activation-matrix.md` — tabular view of which modules activate per workflow type
- `modules/l2/recipe/SKILL.md` — how Recipe reads task card to derive activation list
- `modules/l2/guard/SKILL.md` and `.wabblespec/engine/shared/references/guard-policy-reference.md` — Guard's 5 layers
- `.wabblespec/engine/shared/references/version-policy.md` — delta_class and SemVer bump rules referenced above
- `modules/l7/commit/SKILL.md` — mixed-concern split rule; WHY body requirement
