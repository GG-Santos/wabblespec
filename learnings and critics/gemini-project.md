# Project Execution Judge: WabbleSpec v6

1. **What assumptions in this spec are probably wrong?**
That adding rigid, 9-layer bureaucracy (L0-L8) with mandatory "receipts" will improve LLM coding output, rather than suffocating it in token-heavy metadata and causing context exhaustion.

2. **What parts sound smart but are actually weak?**
"Build-target-routed software creation system." Routing logic sounds sophisticated, but LLMs do not need 11 predefined buckets (Web, CLI, IoT, etc.) to write code; they need specific, concise context. Pre-routing everything limits the model's natural ability to infer context.

3. **What parts are fake innovation?**
"Receipt-driven execution" and "Memory staleness tracking." This is just standard logging, caching, and state management rebranded with pseudo-academic terminology.

4. **What parts are just feature bloat?**
L8 Evolution, L7 Delivery, L6 Expression, L5 Memory, and supporting 11 platform targets out of the gate.

5. **What parts users likely will not care about?**
Users will not care about "v5.3 lineage," the 6 capability gateways, or the L0-L8 internal layer map. They only care if the tool reliably generates working software without breaking.

6. **What parts are technically risky or unrealistic?**
"Vendor-neutral runtime contracts." Attempting to perfectly abstract Claude, Codex, and Gemini into a unified interface will result in a leaky, lowest-common-denominator wrapper that fails to leverage any model's specific strengths.

7. **What parts are vague, hand-wavy, or not implementable?**
L8 Evolution's "Instinct observes execution for pattern extraction." The mechanism for an LLM to safely observe, evaluate, and rewrite its own framework patterns without human intervention is entirely hand-wavy and currently a research-grade problem.

8. **What parts are copied from existing tools without enough difference?**
The capability gateways and routing logic are heavily derivative of existing Agent/Tool/MCP patterns, but wrapped in a much heavier, proprietary markdown structure.

9. **What parts should be deleted before anything is built?**
The entire L5-L8 stack (Memory, Expression, Delivery, Evolution). Support for 10 of the 11 platforms. The vendor-neutrality requirement.

10. **What must be validated before writing code?**
That an LLM can actually follow the L0->L4 routing and receipt-generation chain for a simple feature without losing track of the original user intent or running out of context.

11. **What evidence is missing?**
There is zero evidence (no prototypes, no traces, no token-usage math) that this 9-layer architecture produces better code than a simple, single-prompt codebase context injection.

12. **What would make this idea not worth building?**
If the overhead of managing the routing, metadata, and receipts consumes so much of the context window that the LLM has no room left to reason about the actual software being built.

13. **What is the harshest honest interpretation of this project?**
It is an architecture astronaut's fantasy. It substitutes complex folder structures, jargon, and metadata rules for actual intelligence, destined to collapse under its own context weight.

14. **Am I solving a real problem, or decorating an idea?**
You are decorating an idea. You have built a massive bureaucracy of markdown files instead of a tool that solves a clear, painful problem for developers.

15. **Is this project real, or just a golden egg hoax?**
It leans heavily toward a golden egg hoax. "Self-modification" and "vendor neutrality" are shiny buzzwords hiding the lack of a working core generation loop.

---

## Problem
The framework defines 9 layers (L0-L8) with dozens of modules and capability gateways before a single line of project code is generated.

## Wrong Assumption
That adding rigid, multi-stage bureaucracy to LLMs improves output quality.

## Why It May Be False
LLMs perform best with clear instructions and relevant context, not when forced to navigate abstract framework routing and stage gates. This architecture will almost certainly lead to context exhaustion (as admitted in your error taxonomy) and hallucinated metadata.

## Missing Evidence
There is no proof that an LLM can successfully navigate from L0 Recipe to L4 Capability without losing the original user intent.

## Consequence If Ignored
The system will collapse under its own weight. Tokens will be wasted generating "receipts" and "spec hierarchies" instead of functioning software.

## Validation Test
Manually run a single prompt through the L0->L4 flow using Claude or GPT-4, strictly enforcing the receipt and routing rules, and measure the token overhead versus actual code output.

## Action
Simplify.

---

## Problem
Treating Claude, Codex, and Gemini as interchangeable parts behind a "runtime contract".

## Wrong Assumption
That AI models can be perfectly abstracted into a unified interface without losing their unique strengths.

## Why It May Be False
Every model has distinct prompt requirements, context limits, and reasoning behaviors. A vendor-neutral layer inevitably becomes a lowest-common-denominator wrapper, preventing you from using Claude's long-context or Codex's specific coding optimizations effectively.

## Missing Evidence
No evidence of a successful prompt or task shape that yields identical, high-quality results across all three models via this abstraction.

## Consequence If Ignored
You will spend months tweaking the "RuntimeProbe" and "ModelRouter" to handle model quirks, abandoning the actual framework logic.

## Validation Test
Write a single complex component using the proposed vendor-neutral runtime contract in all three models and compare the failure rates.

## Action
Pivot.

---

## Problem
The L8 Evolution layer proposes self-modification and pattern extraction ("Instinct").

## Wrong Assumption
That an LLM system can safely and reliably observe its own execution and rewrite its core framework without breaking.

## Why It May Be False
Autonomous self-improvement in coding frameworks is pure fantasy for a V1 spec. It assumes flawless test coverage, perfect hallucination detection, and an "Attestation" mode that won't just rubber-stamp bad code.

## Missing Evidence
Zero empirical evidence or prototype demonstrating the framework successfully improving a module without human intervention.

## Consequence If Ignored
You will waste massive engineering effort on a feature that either does nothing or actively corrupts the framework (`.wabblespec/`).

## Validation Test
Build a standalone script that uses an LLM to rewrite a simple Python function based on execution logs. Measure how often it breaks it.

## Action
Delete.

---

## Brutal Cut List
- L8 Evolution (entirely)
- L7 Delivery (use existing CI/CD tools, do not build this)
- L6 Expression
- L5 Memory (start with stateless or basic file reads)
- Vendor-neutral runtime contracts (pick one model, e.g., Claude, and optimize for it)
- 10 of the 11 platform targets (pick ONE target, e.g., Web, to start)
- Receipt generation for every single phase transition.

## MVP Reality Check
A single-script CLI that takes a prompt, reads a simplified `.planning/` folder, and outputs a working web app component using ONE specific model. No L0-L8 routing. No evolution. Just: Intent -> Context -> Code -> Test.

## Validation Plan
1. **End-to-End Token Cost:** Manually simulate the L0->L4 routing flow for a "Hello World" app to measure token consumption and context bloat.
2. **Abstraction Test:** Attempt to write a single prompt that works equally well for a complex task in both Claude and Gemini to prove "vendor neutrality" is actually viable.
3. **Receipt Overhead:** Measure how many tokens are spent generating "receipts" versus actual project code.
4. **Gate Collapse Test:** Verify if the "Gate collapsing" exception actually works without degrading output quality.
5. **The ONE Target Test:** Build a fully working prototype that only supports the "Web" target before adding any other platform routing.

## Kill Criteria
- If the token overhead for receipts and routing exceeds 40% of the context window.
- If the LLM repeatedly hallucinates framework layers (e.g., confusing L3 and L4).
- If it takes more than 10 manual prompts to fix the "automated" routing errors for a basic app.
- If you find yourself writing more PowerShell scripts to manage the framework than the framework writes actual code.

## Final Verdict
SHRINK
