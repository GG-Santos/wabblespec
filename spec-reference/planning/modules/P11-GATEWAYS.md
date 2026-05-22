# Module Plan — L4 Capability Gateways (All 6)

**Tier:** 1 — CRITICAL ROUTING
**Layer:** L4 Capability
**v5.3 origin:** Security gateway (retained cross-cutting, platform portions moved), Engineering gateway (retained cross-cutting, platform portions moved), AI gateway (restored), Aesthetic/Design/Experience (unchanged)

---

## Common Structure

Every capability gateway follows this layout:

```
.wabblespec/gateways/<gateway>/
  SKILL.md                      <- gateway routing logic, scope declaration
  skill-rules.json              <- activation signals, authority declaration
  references/                   <- cross-cutting domain knowledge
  rules/                        <- policy files enforced across all targets
  evaluations/                  <- eval cases for gateway quality checks
  schemas/
    receipt.schema.json
```

Gateway modules are cross-cutting — they apply regardless of build target. Platform packages feed target-specific concerns upward to the gateway; the gateway feeds cross-cutting policy downward to Apply. No gateway owns product files (I11).

---

## 1. Security Gateway

**Scope (cross-cutting):** Threat modeling, continuous security cycles, OWASP, pentest guidance, compliance frameworks, cross-cutting defense patterns.

**Explicitly NOT in scope:** firmware signing (IoT platform), app permissions (Mobile platform), extension sandboxing (Extension/Plugin platform), library supply chain (Library/Package platform). Those live in their respective L3 platform security/ directories.

### Activation

`skill-rules.json` triggers:
- Any P3 or P4 spec stage (security review always runs before Technical Spec locks)
- Explicit `/security` command
- Verifier audit mode (Security is consulted for Audit verification)
- Platform security modules forward cross-cutting concerns upward

### References

`references/threat-modeling.md`:
- STRIDE methodology: Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege
- Threat model artifact: required in P2 Systems Design for all targets
- DFD (Data Flow Diagram): level 0 and level 1 required, level 2 for complex targets
- Trust boundaries: every external input crosses a trust boundary — must be declared

`references/owasp.md`:
- OWASP Top 10 (Web): checklist applied for Web and API/Service targets
- OWASP API Security Top 10: checklist applied for API/Service target
- OWASP Mobile Top 10: checklist applied for Mobile target — forwarded from Mobile platform
- OWASP ASVS: Level 1 baseline for all targets, Level 2 for high-assurance applications

`references/continuous-security.md`:
- Dependency scanning: automated, every build — block on critical CVEs
- SAST: static analysis integrated into CI — block on high/critical findings
- Secret scanning: pre-commit hook + CI gate — block on any detected secrets
- Penetration testing: scope declared in spec — when and how (internal, third-party)

`references/compliance.md`:
- GDPR: data processing inventory, consent management, right to erasure — scoped to project
- SOC 2: controls mapping when target is SaaS — declared in P1 spec
- HIPAA: when health data in scope — adds encryption and audit log requirements
- PCI-DSS: when payment data — scope reduction strategy (tokenization) preferred

### Rules

`rules/auth-policy.md`:
- Every external endpoint has declared auth requirement
- Session management: tokens expire, refresh tokens rotate
- MFA: required for admin interfaces and high-value actions

`rules/secrets-policy.md`:
- No secrets in code, config files, or logs
- Rotation policy: API keys rotated on any exposure event
- Vault: secret management tool declared for production (not env files in production)

### Verification Mode

**Audit** — security checklist completed per target, threat model present, no critical/high SAST findings, no secrets in repo.

### Receipt Extension Fields

```json
{
  "threat_model_present": "boolean",
  "owasp_checklist": "string",
  "critical_findings": "integer",
  "high_findings": "integer",
  "compliance_scope": ["string"],
  "pentest_required": "boolean"
}
```

---

## 2. Engineering Gateway

**Scope (cross-cutting):** CI/CD patterns, architecture review, reliability principles, systems design standards, cross-cutting technical standards.

**Explicitly NOT in scope:** build toolchain (L3 platform engineering), target-specific performance budgets (L3 platform engineering), hardware integration (IoT platform), platform build pipeline (platform engineering).

### Activation

`skill-rules.json` triggers:
- P2 Systems Design stage (architecture review always runs)
- P3 Technical Spec (cross-cutting engineering standards applied)
- Explicit `/engineering` command
- BREAKING spec changes route through Engineering before Executor proceeds

### References

`references/architecture-review.md`:
- ADR (Architecture Decision Record): required for any decision with >6 month implications
- C4 model: Context, Container, Component, Code — level appropriate to spec stage
- Coupling: loose coupling between services declared and measured
- Cohesion: module boundaries justify grouping — not convenience grouping

`references/ci-cd.md`:
- Pipeline stages: lint → test → build → security scan → deploy (declared order)
- Branch strategy: declared in spec (trunk-based vs. GitFlow vs. GitHub Flow)
- Deployment strategy: blue-green, canary, rolling — declared per environment
- Rollback: automated rollback trigger declared (error rate threshold)

`references/reliability.md`:
- SLO: availability and latency targets declared in spec, not implied
- Error budget: derived from SLO, used to gate risky changes
- Circuit breaker: required for all synchronous external calls
- Chaos engineering: scope declared (none/limited/continuous) — not required, must be declared

`references/systems-design.md`:
- CAP theorem: consistency/availability trade-off declared for distributed components
- Idempotency: declared for all state-mutating operations
- Backpressure: declared for all async processing paths
- Data contracts: versioned, not implicit

### Rules

`rules/adr-policy.md`:
- ADR required for: framework selection, database selection, auth mechanism, deployment strategy
- ADR format: title, status (proposed/accepted/deprecated/superseded), context, decision, consequences
- ADR supersession: new ADR references old ADR — old marked superseded

`rules/test-coverage-policy.md`:
- Unit coverage floor: declared per project (not universal 80% — declared)
- Integration tests: required for all external integrations
- E2E tests: required for critical user journeys
- Contract tests: required for API consumers

### Verification Mode

**Review** — architecture review completed, ADRs present for major decisions, CI pipeline declared, reliability targets documented.

### Receipt Extension Fields

```json
{
  "adr_count": "integer",
  "architecture_reviewed": "boolean",
  "ci_pipeline_declared": "boolean",
  "slo_declared": "boolean",
  "breaking_changes_reviewed": "integer"
}
```

---

## 3. AI Gateway

**Scope:** LLM evaluation, prompt engineering, chain/agent design, safety and alignment considerations. Applies to any target embedding AI features — not only the AI/Agent build target. AI/Agent platform package routes here for all implementation content.

### Activation

`skill-rules.json` triggers:
- AI/Agent build target (always active)
- Any target with LLM SDK dependency detected by Explore
- Explicit `/ai` command
- P3 Technical Spec for AI features on any target

### References

`references/prompt-engineering.md`:
- System prompt: declarative, versioned, tested — not ad hoc
- Few-shot examples: curated, representative, updated with observed failure cases
- Temperature: declared per task type (creative: higher, deterministic: lower/zero)
- Token budget: system prompt + examples + user input + output — declared, not assumed

`references/chain-design.md`:
- Chain steps: each step has declared input schema, output schema, validation
- Branching: conditional routing declared — not implicit in model output parsing
- Error recovery: fallback per step, not per chain
- Context passing: explicit, not via global state between chain steps

`references/agent-architecture.md`:
- Tools: each tool has declared name, description, input schema, output schema
- Tool selection: model selects, but tool execution is deterministic
- Loop bounds: maximum iterations declared — no unbounded agent loops
- Observation: tool output returned to model as structured observation, not raw text
- Human-in-the-loop: irreversible tool calls require Attestation gate

`references/evaluation.md`:
- Eval dimensions: declared per use case (accuracy, helpfulness, safety, latency, cost)
- Eval dataset: curated, versioned, separate from development data
- Regression: eval suite runs on every model or prompt change
- Red-teaming: adversarial inputs tested, failure modes documented

`references/safety.md`:
- Output validation: LLM output never directly executed or rendered without validation
- PII: no PII in prompts without explicit DPA and declared processing purpose
- Bias: eval suite includes fairness dimensions for public-facing applications
- Refusal handling: declared — what happens when model refuses a valid request

### Rules

`rules/model-pinning.md`:
- Model version pinned — never `latest` in production
- Version bump: eval suite must pass before promoting to new model version
- Fallback: declared fallback model for unavailability

`rules/eval-policy.md`:
- Eval suite required before any prompt or model change ships
- Eval coverage: all declared eval dimensions tested
- Eval data: no production data in eval suite without anonymization

### Verification Mode

**Measurement** — eval suite passes declared thresholds, model version pinned, token budget within spec, safety dimensions evaluated.

### Receipt Extension Fields

```json
{
  "model_pinned": "boolean",
  "eval_dimensions": ["string"],
  "eval_pass": "boolean",
  "token_budget_declared": "boolean",
  "tools_declared": "integer",
  "attestation_gates": "integer"
}
```

---

## 4. Aesthetic Gateway

**Scope:** Visual design, brand identity, style systems, color, typography, motion. Applies to Web, Mobile, Desktop, Game, Extension/Plugin targets.

**v5.3:** Unchanged in scope and responsibility.

### Activation

`skill-rules.json` triggers:
- Visual-facing build target (Web, Mobile, Desktop, Game, Extension/Plugin)
- Explicit `/aesthetic` command
- P3 stage for visual targets (style system review)
- Homowabian ultra mode suppressed for aesthetic content (prose context needed)

### References

`references/brand.md`:
- Brand assets: logo, wordmark, color palette — source of truth location declared
- Brand voice: consistency with Expression layer output
- Asset usage: approved formats, minimum sizes, clear space rules

`references/color.md`:
- Color system: semantic tokens (not raw hex in components)
- Contrast: WCAG AA minimum (4.5:1 text, 3:1 large text) — non-negotiable
- Dark mode: declared in scope (yes/no/auto) at P1 spec
- Brand colors vs. semantic colors: separation maintained

`references/typography.md`:
- Type scale: modular scale declared (not ad hoc font sizes)
- Font loading: variable fonts preferred, font-display: swap, subset if large
- Type hierarchy: H1-H6 semantic use, not visual-only

`references/motion.md`:
- Motion principles: purposeful (communicates state) vs. decorative (only with justification)
- Reduced motion: prefers-reduced-motion respected — non-negotiable for accessibility
- Duration: 150ms-300ms for UI transitions, 0ms option for reduced motion
- Easing: declared easing tokens, not inline values

### Rules

`rules/design-token-policy.md`:
- All visual values (color, spacing, typography, radius) declared as design tokens
- No raw values in component code — token references only
- Token format: CSS custom properties or platform equivalent

### Verification Mode

**Review** — design token system present, contrast ratios pass, motion accessible, brand assets referenced correctly.

### Receipt Extension Fields

```json
{
  "design_tokens_present": "boolean",
  "contrast_audit_passed": "boolean",
  "reduced_motion_handled": "boolean",
  "dark_mode_scope": "yes|no|auto"
}
```

---

## 5. Design Gateway

**Scope:** UX, interaction design, information architecture, user flows, wireframes, design system components. Applies to visual-facing targets.

**v5.3:** Unchanged in scope and responsibility.

### Activation

`skill-rules.json` triggers:
- Visual-facing build target
- Explicit `/design` command
- P1 Design Document stage (user flows required)
- P3 Technical Spec for interaction patterns

### References

`references/ux-principles.md`:
- User mental models: spec declares target mental model per major flow
- Affordances: interactive elements visually communicate affordance
- Feedback: every user action has immediate feedback (< 100ms perceived or loading indicator)
- Error states: every error has a message, every message has a recovery path

`references/information-architecture.md`:
- Navigation: max 3 levels deep for primary navigation
- Labeling: content labels from user research or domain vocabulary — not internal jargon
- Search: when content > 20 items, search or filter required

`references/interaction-design.md`:
- Touch targets: minimum 44x44px for mobile, 32x32px desktop with keyboard alternative
- Keyboard: all interactions keyboard-accessible
- Focus management: focus lands on meaningful element after state change
- Gestures: no gesture-only interactions — all gestures have button equivalent

`references/design-system.md`:
- Component library: declared (existing vs. build-from-scratch vs. headless)
- Component documentation: each component has usage guidelines, do/don't examples
- Storybook or equivalent: required for component-heavy projects
- Token consumption: components consume Aesthetic tokens directly

### Rules

`rules/accessibility-floor.md`:
- WCAG 2.1 AA: minimum baseline for all visual targets
- Keyboard navigation: all interactive elements reachable by keyboard
- Screen reader: semantic HTML or ARIA where HTML semantics insufficient
- No accessibility-only paths: accessibility is not a separate mode

### Verification Mode

**Demonstration** — user flows completable, keyboard nav works, touch targets pass, design system documented.

### Receipt Extension Fields

```json
{
  "user_flows_documented": "integer",
  "wcag_level": "A|AA|AAA",
  "keyboard_audit_passed": "boolean",
  "design_system_declared": "boolean"
}
```

---

## 6. Experience Gateway

**Scope:** User research, usability testing, accessibility deep-dives, user satisfaction measurement. Applies to visual-facing targets where user research is in scope.

**v5.3:** Unchanged in scope and responsibility.

### Activation

`skill-rules.json` triggers:
- Visual-facing target with user research in scope (declared at P1)
- Explicit `/experience` command
- P1 or P4 stage when user validation is declared
- Verifier Demonstration mode for user-facing deliverables

### References

`references/user-research.md`:
- Research methods: interviews, surveys, usability tests — method chosen based on question type
- Participant recruitment: minimum 5 participants for usability testing (Nielsen heuristic)
- Research artifacts: synthesis note, affinity diagram, insight list — written to Memory as FRESH drawers
- Research cadence: declared (continuous discovery vs. milestone-based)

`references/usability-testing.md`:
- Test scenarios: task-based, not feature-based
- Facilitator guide: neutral phrasing — no leading questions
- Metrics: task completion rate, time on task, error rate, satisfaction (SUS or equivalent)
- Remote vs. in-person: declared, tooling declared

`references/accessibility.md`:
- Screen reader testing: VoiceOver (Mac/iOS), NVDA/JAWS (Windows), TalkBack (Android) — matrix declared
- Cognitive accessibility: plain language, consistent navigation, no time limits without extension
- Color blindness: tested with deuteranopia simulation
- Motor accessibility: switch access, voice control compatibility declared in scope

`references/satisfaction-measurement.md`:
- SUS (System Usability Scale): optional baseline metric for major releases
- NPS: optional for long-running products
- In-product feedback: mechanism declared when continuous measurement in scope

### Rules

`rules/research-ethics.md`:
- Informed consent: required for all research participants
- Data anonymization: participant data anonymized before storage
- Compensation: declared — no uncompensated high-effort tasks

### Verification Mode

**Demonstration** — usability test conducted (if in scope), accessibility matrix tested, research insights written to Memory.

### Receipt Extension Fields

```json
{
  "research_in_scope": "boolean",
  "usability_test_conducted": "boolean",
  "accessibility_matrix_tested": ["string"],
  "insights_written_to_memory": "integer"
}
```

---

## Common Integration Points (all gateways)

| Module | Relationship |
|---|---|
| Apply | Apply reads active gateway SKILL.md for routing decisions during execution |
| Verifier | Verifier reads gateway verification gates during wave verification |
| Platform packages (L3) | Platform security/engineering modules feed cross-cutting concerns upward to gateway |
| Reviewer | Reviewer consults relevant gateway during budget-gated review |
| Specify | Specify consults gateway rules when classifying spec changes as BREAKING |
| Archive | Archive aggregates gateway receipts into final version archive |

---

## Open Decisions

| Decision | Options | When to resolve |
|---|---|---|
| Security gateway runs per-wave vs. per-stage | Per-stage (current: P3/P4) vs. per-wave (more frequent, more overhead) | Implementation |
| AI gateway scope for non-AI targets | Current: any target with LLM SDK vs. opt-in only | P10 platform refinement |
| Experience gateway activation floor | Always for visual targets vs. only when research declared in scope | Per-project |
| Design/Aesthetic gateway merge | Keep separate (current) vs. merge into single UX gateway | Locked: keep separate — different activation points |
