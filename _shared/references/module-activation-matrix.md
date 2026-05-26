# Module Activation Matrix

**Consumed by:** l2/recipe (activation routing), l2/grader (audit completeness check)  
**Purpose:** Tabular view of which modules activate for each workflow type and platform. Companion to `gate-progression-reference.md` — that file explains why; this file is the quick lookup table.

**Legend:** `R` = Required, `O` = Optional (signal-dependent), `-` = Not applicable

---

## By workflow type

| Module | New Feature | Bug Fix | Security Patch | Breaking Change | Dep Upgrade | Refactor | Docs Update |
|---|---|---|---|---|---|---|---|
| **L1** | | | | | | | |
| Plan | R | R | R | R | O | O | O |
| ScopeFrame | R | R | R | R | R | R | R |
| Specify | R | R | R | R | O | O | - |
| Brainstorm | O | - | - | O | - | - | - |
| Enhance | O | - | - | O | - | - | - |
| Explore | R | O | O | R | - | O | - |
| Analyze | O | O | O | O | - | O | - |
| **L2** | | | | | | | |
| Recipe | R | R | R | R | R | R | R |
| Guard | R | R | R | R | R | R | R |
| Executor | R | R | R | R | R | R | R |
| Verifier | R | R | R | R | R | R | R |
| Archive | R | R | R | R | R | R | R |
| Rollback | O | O | O | O | - | - | - |
| **L3 Platform** | | | | | | | |
| Active platform | R | O | O | R | - | O | - |
| **L4 Gateways** | | | | | | | |
| Engineering | R | R | R | R | R | R | - |
| Security | O | O | R | O | O | O | - |
| AI | O | O | O | O | - | O | - |
| Aesthetic | O | - | - | O | - | - | - |
| Design | O | - | - | O | - | - | - |
| Experience | O | - | - | O | - | - | - |
| **L5 Memory** | | | | | | | |
| Memory | O | O | O | O | - | - | O |
| EntityGraph | O | - | - | O | - | O | - |
| Provenance | O | - | O | R | - | - | - |
| Nexus | O | - | O | R | - | - | - |
| Dream | - | - | - | - | - | - | - |
| Forget | - | - | - | - | - | O | - |
| **L6 Polish** | | | | | | | |
| Polish | R | R | R | R | - | R | R |
| Proofread | O | - | - | O | - | - | R |
| Markdown | O | - | - | O | - | - | O |
| Document | O | O | - | R | - | - | R |
| Legal | O | - | - | O | - | - | O |
| Translate | O | - | - | O | - | - | O |
| **L7 Delivery** | | | | | | | |
| Commit | R | R | R | R | R | R | R |
| Monitor | O | O | O | O | - | - | - |
| Changelog | R | O | R | R | - | - | - |
| Package | O | - | O | O | - | - | - |
| Release | O | - | O | O | - | - | - |
| Deploy | O | O | R | O | O | - | - |
| Scaffold | - | - | - | - | - | - | - |

_Dream runs on a background schedule (not task-triggered). Scaffold runs once at project creation. Forget is task-triggered only for data hygiene tasks._

---

## By L4 gateway — activation signals

| Gateway | Activates when |
|---|---|
| Engineering | Any task Medium complexity or higher; any production deploy |
| Security | New endpoint, auth change, external user input, CVE in dep, STRIDE flag from L1/Analyze |
| AI | Platform = AI-Agent; LLM SDK import detected in any wave file; `latest` model string found |
| Aesthetic | Platform has visual components (Web, Mobile, Desktop, Extension, Game); new visual component added |
| Design | 10+ components in wave; accessibility-affecting UI change; Platform = Web/Mobile/Desktop/Extension |
| Experience | P1 user-research scope declared in task card; Design gateway receipt present (prerequisite) |

---

## By platform — which L4 gateways are expected

| Platform | Engineering | Security | AI | Aesthetic | Design | Experience |
|---|---|---|---|---|---|---|
| Web | R | O | - | O | O | O |
| API-Service | R | R | - | - | - | - |
| CLI | R | O | - | - | - | - |
| Mobile | R | O | - | O | O | O |
| Desktop | R | O | - | O | O | O |
| Data-Pipeline | R | O | - | - | - | - |
| AI-Agent | R | R | R | - | - | - |
| IoT | R | R | - | - | - | - |
| Game | R | O | - | O | O | - |
| Library | R | O | - | - | - | - |
| Extension | R | R | - | O | O | - |

_Security is R (Required) for API-Service, AI-Agent, IoT, and Extension because they handle external input, network, or privileged access by definition._

---

## Provenance cascade conditions

Provenance cascade runs when Archive records a BREAKING delivery. It does NOT run for ADDITIVE or NON_BREAKING.

| Condition | Cascade triggered |
|---|---|
| delta_class = BREAKING | Yes — 2-hop depth limit |
| delta_class = ADDITIVE | No |
| delta_class = NON_BREAKING | No |

---

## Nexus refresh conditions

Nexus refresh runs post-Archive when the delivery introduces structural changes. It runs automatically when Archive records BREAKING or ADDITIVE.

| Condition | Nexus refresh triggered |
|---|---|
| delta_class = BREAKING | Yes — mandatory before next task starts |
| delta_class = ADDITIVE | Yes — recommended; Recipe should verify before next task |
| delta_class = NON_BREAKING | No |

---

## Minimum receipt set per workflow type

The L8 corpus gate counts individual receipts. Each wave generates: executor-receipt + verifier-receipt. Each task generates: delivery-receipt. Guard generates a guard-receipt per wave (counted separately).

| Workflow type | Minimum receipts per task |
|---|---|
| New Feature (1 wave) | 3 (executor + verifier + delivery) |
| New Feature (2 waves) | 5 (2x executor + 2x verifier + delivery) |
| Bug Fix (1 wave) | 3 |
| Security Patch (1 wave) | 3 |
| Breaking Change (2+ waves typical) | 5+ |
| Dep Upgrade (1 wave) | 3 |
| Refactor (1 wave) | 3 |
| Docs Update (1 wave) | 3 |

_Guard receipts are not counted in the L8 corpus gate — only executor, verifier, and delivery receipts count._

---

## Cross-references

- `_shared/references/gate-progression-reference.md` — narrative explanation for each workflow type
- `modules/l2/recipe/SKILL.md` — Recipe reads this matrix to derive activation list from task card signals
- `_shared/references/version-policy.md` — delta_class and SemVer bump per workflow type
- `_shared/references/guard-policy-reference.md` — Guard runs before every Executor wave regardless of matrix
