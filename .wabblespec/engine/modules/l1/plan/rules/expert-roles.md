# Expert Roles

Which expert perspectives to apply based on task domain and complexity. Minimum 2 always. Add domain-specific perspectives from the tables below.

## Default perspectives (apply to all plans at Medium+ complexity)

| Perspective | Core question |
|---|---|
| Architecture | Does this approach introduce hidden coupling, layering violations, or circular dependencies? |
| Security | What attack surface does this approach expose? What data is now accessible that wasn't before? |
| Operability | How does this fail in production? Is failure observable? How is it recovered? |
| Performance | What are the scale limits? What does this cost per request at 10x and 100x current load? |
| Maintainability | Will a future developer understand why this approach was chosen without reading this conversation? |

## Domain-specific perspectives

### Web + API-Service

| Perspective | Core question |
|---|---|
| API contract | Does this change break existing clients? What migration is needed? |
| UX | Does this change affect user-facing flows? Are error states handled visibly? |
| Caching | Does this invalidate caches? Are cache keys updated? |

### Security scope (any task tagged `security` or touching auth/crypto/permissions)

| Perspective | Core question |
|---|---|
| Threat model | What threat actors does this change the exposure for? |
| Privilege | Does this escalate privileges? Who can invoke this path? |
| Data exposure | Does this expose PII, secrets, or internal state to new surfaces? |

### Data pipeline / Database

| Perspective | Core question |
|---|---|
| Data integrity | Does this change put data in an inconsistent state mid-execution? |
| Migration safety | Can this migration be rolled back? What is the rollback state? |
| Volume | Does this approach work at the current and projected data volume? |

### Infrastructure / Irreversible scope

| Perspective | Core question |
|---|---|
| Blast radius | What breaks if this goes wrong? How many systems are affected? |
| Rollback | Can this be undone? How long does rollback take? |
| Coordination | What other teams or systems need to be notified before this runs? |

## Applying a perspective

For each perspective: state one finding. Options are:
- **Concern:** "Architecture — this introduces a circular dependency between auth and sessions modules."
- **Confirmation:** "Security — no new attack surface exposed; change is additive to an internal cache."
- **Risk:** "Operability — failure mode is silent; no alerting path. BLOCKING until observability is added."

Do not write "no concerns found" without actually checking. Apply the lens, then report.
