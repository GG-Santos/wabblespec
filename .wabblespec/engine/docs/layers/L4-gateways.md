# L4 — Gateways

Safety and quality gates. L4 modules run after Decompose and before Executor. They do not execute tasks — they determine whether execution is safe, complete, and appropriate for the target domain.

Full gateway specification: `.wabblespec/engine/shared/infrastructure/gateway-pattern.md`.
Each gateway's detail doc: `_docs/gateways/`.

## Modules

| Module | Domain | Activates when |
|--------|--------|----------------|
| `gateway-security` | Cross-platform security threats | Any target with security-sensitive characteristics: auth, payments, PII, secrets, infra |
| `gateway-engineering` | Build quality and standards | Any engineering execution at Medium/High complexity |
| `gateway-ai` | LLM safety and evaluation | Any target producing AI/LLM output |
| `gateway-aesthetic` | Visual brand and style | Any UI/design deliverable |
| `gateway-design` | UX and interaction design | Any UX/interaction deliverable |
| `gateway-experience` | Accessibility, performance, delight | Any user-facing experience work. Requires design gateway PASS first. |

## Gateway verdict schema

```json
{
  "verdict": "PASS | FLAG | BLOCK",
  "domain": "string",
  "checks_run": ["array of check names"],
  "flags": ["array of FLAG items — empty if PASS"],
  "block_reason": "string | null",
  "override_required": "boolean"
}
```

## Verdict semantics

| Verdict | Effect |
|---------|--------|
| PASS | Executor runs normally |
| FLAG | Non-blocking warning. Execution proceeds. FLAG recorded in delivery receipt. |
| BLOCK | Executor does not run. Surfaced to human. Paused until block condition resolved or human override granted. |

## Sequencing when multiple gateways apply

1. `gateway-security` — always first; a BLOCK here stops the chain
2. `gateway-engineering`
3. `gateway-ai` (if LLM output involved)
4. `gateway-aesthetic`, `gateway-design`, `gateway-experience` — parallel (domain-independent)

## Two-phase activation

Every gateway operates in two phases:

### Phase A — Inform (Specify time)

Runs during Specify before execution. Injects domain knowledge and requirements into the spec as acceptance criteria.

Receipt type: `gateway-spec-receipt` with `status: INFORM`. Not a verdict — a knowledge contribution.

Each gateway declares a `references/` directory containing the knowledge files loaded in Phase A:
- `gateway-security/references/` — threat-modeling, OWASP, compliance, continuous-security, cycling/
- `gateway-engineering/references/` — quality-patterns, architecture
- `gateway-ai/references/` — safety, evals, cost
- `gateway-aesthetic/references/` — color, typography, motion
- `gateway-design/references/` — flows, components, systems
- `gateway-experience/references/` — wcag, platform-ux

gateway-security Phase A additionally runs STRIDE analysis and produces security requirements as acceptance criteria.

### Phase B — Verdict (pre-Executor)

Runs before Executor for each wave. Issues PASS / FLAG / BLOCK verdict.

Receipt type: `gateway-verdict-receipt`.

### Red/Blue/Purple cycling (security only)

Activated via `/security-cycle`, `/security-red`, `/security-blue`, `/security-score`, or `/security-intel`. Full adversarial exercise with Intel → Red → Blue → Purple phases. Cycling terminates on posture target, diminishing returns, max cycles, or all CRITICAL+HIGH closed. See `modules/l4/security/references/cycling/`.

## Gateway pattern

All L4 gateways load rule files and `references/` knowledge files. Their files live at `modules/l4/{name}/` alongside `SKILL.md` and `skill-rules.json`.

## Layer rules

- Gateways never write to `project/repo/`
- Gateways never call Executor
- A BLOCK from gateway-security stops the entire chain — do not run remaining gateways on a security-blocked execution
- Gateway checks run once per execution, not per wave (unless platform declaration changes mid-execution)
