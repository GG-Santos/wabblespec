# MCP Servers Integration

Optional MCP server integrations, their activation patterns, and module-level call contracts. All servers are opt-in — execution never gates on their availability. Consumers check `mcp_servers.<id>.available` in `runtime-state.json`.

## Server Catalog

| Server | Provider | Status | Primary consumers |
|---|---|---|---|
| `context7` | Upstash | Active | executor, specify, gateway-engineering |
| `serena` | Oraios | Opt-in | explore, analyze, decompose, gateway-engineering |
| `playwright` | Microsoft | Opt-in | test, verifier (Demonstration), platform-web, gateway-experience |
| `github` | GitHub | Opt-in | wave-review, commit, archive |
| `linear` | Linear | Opt-in | recipe, specify, archive, triage |
| `gitlab` | GitLab | Opt-in | wave-review, commit, archive (GitLab variant of github) |
| `greptile` | Greptile | Opt-in | wave-review (Step 0b — pre-review findings) |
| `firebase` | Google | Opt-in | deploy, platform-api-service, platform-web |
| `terraform` | HashiCorp | Opt-in | deploy, scaffold, rollback |
| `laravel-boost` | Laravel | Opt-in | platform-api-service, scaffold, migrate |
| `asana` | Asana | Opt-in | recipe, team-plan (Asana alternative to linear) |

Full MCP server configs: `.mcp.json` at project root.
For servers not in `.mcp.json` (greptile, firebase, terraform, laravel-boost, asana): add manually per the external_plugins reference format.

---

## Context7

**Purpose:** Live library/framework documentation fetched by content ID and version.

**Activation:** check `mcp_servers.context7.available` in runtime-state.json. Full detection and call patterns: `context7-integration.md`.

**Call pattern:**
```
1. resolve-library-id libraryName: "<library>"
2. get-library-docs context7CompatibleLibraryID: "<id>" topic: "<specific API surface>"
```

Load only the specific section the wave plan names. Never load full library docs into context.

---

## Serena

**Purpose:** Semantic code navigation via LSP. Wraps multiple language servers in one MCP interface.

**Activation:** check `mcp_servers.serena.available` in runtime-state.json. When `false`: fall back to Glob/Grep/Read traversal — do not block.

**Install:** `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`

**Available tools:**
| Tool | Use for |
|---|---|
| `serena_find_references <symbol>` | Locate all callers of an entry point or function |
| `serena_go_to_definition <symbol>` | Resolve import paths and type definitions |
| `serena_list_symbols <file>` | Extract public API surface from a file |
| `serena_search_codebase <query>` | Semantic pattern search across the project |

**Module call contracts:**

*Explore:* Use `serena_find_references` and `serena_list_symbols` first for Steps 2 (entry points) and 6 (spec-referenced files). Add `serena_available: true` and a `semantic_nav` slice to project-map.md.

*Analyze:* Use `serena_search_codebase` to find code patterns (auth flows, database calls, error handling) before issuing file reads. Record symbol counts in the analysis receipt.

*Decompose:* Use `serena_find_references` on the primary entry point to identify impact surface before wave planning. If serena reports N > 10 callers for a function being changed, flag as HIGH blast-radius in the wave plan.

*Gateway-engineering:* Use `serena_list_symbols` on interface files to enumerate the public API surface before issuing code-quality judgments. A symbol count discrepancy between spec and implementation is a boundary violation.

---

## Playwright

**Purpose:** Browser automation — screenshots, form fills, click flows, E2E test execution.

**Activation:** check `mcp_servers.playwright.available` in runtime-state.json. When `false`: Verifier Demonstration mode must fall back to Observation mode with `confidence: 0.6` and note "browser verification unavailable."

**Install:** `npx @playwright/mcp@latest`

**Available tools (representative):**
| Tool | Use for |
|---|---|
| `playwright_navigate` | Open a URL in a controlled browser |
| `playwright_screenshot` | Capture visual state as evidence artifact |
| `playwright_click` | Trigger user interaction |
| `playwright_fill` | Populate form fields |
| `playwright_evaluate` | Run JavaScript in page context |

**Module call contracts:**

*Verifier (Demonstration mode):* Navigate to the feature URL, interact per the declared behavior, capture screenshot as evidence artifact. Embed screenshot path in verification receipt under `evidence`. PASS = behavior confirmed by screenshot comparison or assertion evaluation. FAIL = behavior not observed — describe what the screenshot shows instead.

*Test (E2E test execution):* Use `playwright_navigate` + `playwright_evaluate` to run assertion scripts in a real browser. Record result as Tier 1 evidence (execution artifact). PASS = all assertions green. FAIL = report the specific assertion and the actual page state.

*Gateway-experience:* Use Playwright to run the 5-dimension UX critique gate against a live render rather than a static mockup. Screenshots are captured at: initial load, hover states, form interaction, mobile viewport, and error state. Each dimension is scored against the screenshot evidence.

*Platform-web:* After any UI implementation wave, Playwright can be used to run a visual regression check. Navigate to the rendered page, screenshot, and compare against the spec's declared visual requirements.

---

## GitHub MCP

**Purpose:** GitHub PR/issue management via HTTP MCP.

**Activation:** check `mcp_servers.github.available` in runtime-state.json. Requires `GITHUB_PERSONAL_ACCESS_TOKEN` env var. When unavailable: skip PR-comment steps silently.

**Auth:** `Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}` header.

**Module call contracts:**

*Wave-review (Step 7 — inline PR comments):* After synthesizing findings, for each HIGH/CRITICAL finding where `finding.file` and `finding.line` are populated: post as an inline PR review comment. Comment format declared in wave-review SKILL.md Step 7. Only HIGH/CRITICAL severity is posted — lower findings stay in the receipt only.

*Commit:* When the commit concludes a feature that maps to a GitHub issue, the commit skill may add `Closes #<issue>` to the commit footer. Read the task card for an `issue_ref` field.

*Archive:* When archiving a task with an associated PR, embed the PR URL in the delivery receipt under `vcs_reference.pr_url`. Invoke `github_get_pull_request` to confirm the PR is merged before marking `delivery_status: complete`.

---

## Linear MCP

**Purpose:** Linear issue tracking — read tickets, write status, create sub-issues.

**Activation:** check `mcp_servers.linear.available` in runtime-state.json. Auth via Linear's OAuth; no env var required in HTTP MCP mode. When unavailable: task card is populated manually.

**Module call contracts:**

*Recipe (Step 2 — Linear ticket detection):* When the opening user message contains a Linear issue ID (e.g., `ENG-123` or a Linear URL), invoke `linear_get_issue` to fetch the issue title, description, and acceptance criteria. Pre-populate the task card fields:
- `task_name` ← issue title
- `goal` ← issue description
- `acceptance_criteria` ← issue labels + linked specs
- `linear_issue_id` ← issue ID (stored for archive sync)

*Specify:* When `linear_issue_id` is set in recipe.json, fetch the issue's linked documents (`linear_get_issue_attachments`) as potential spec source material. Do not auto-adopt — surface to human for review.

*Archive:* When `linear_issue_id` is set in the task card, after writing the delivery receipt: invoke `linear_update_issue_status` with `status: "Done"` and attach the delivery receipt URL as a comment. This closes the linear ticket automatically on archive.

*Triage:* When classifying a CRITICAL or HIGH finding, check whether a Linear issue already exists for this finding (`linear_search_issues` by description similarity). If found: link the receipt to the existing issue. If not found: create a new issue with finding details.

---

---

## Greptile

**Purpose:** External AI code review agent for GitHub/GitLab PRs. Surfaces existing review comments and org coding patterns into wave-review.

**Wave-review integration (Step 0b):** Before spawning native review agents, fetch existing Greptile comments via `list_merge_request_comments`. Map to `finding.schema.json` with `source: "greptile"`, `confidence: 0.75`. Surface as fourth agent input to Grader synthesis. Skip when no PR number declared or Greptile unavailable.

**Install:** Add to `.mcp.json` as stdio MCP — see external_plugins/greptile for config. Requires `GREPTILE_API_KEY`.

---

## Firebase

**Purpose:** Google Firebase backend management — Firestore, Authentication, Cloud Functions, Hosting, Storage.

**Module integration:**
- *Deploy:* use Firebase MCP tools to deploy Cloud Functions and Hosting after Executor wave completes
- *Platform-api-service:* Firebase Firestore and Auth are valid backend targets for platform-api-service tasks
- *Platform-web:* Firebase Hosting is a deployment target for web platform tasks

**Install:** Add `firebase` MCP entry to `.mcp.json`. Requires Firebase project ID.

---

## Terraform

**Purpose:** HashiCorp Terraform IaC — infrastructure provisioning, plan, apply, destroy lifecycle.

**Module integration:**
- *Deploy:* `terraform plan` before `terraform apply`; report plan diff to user before apply
- *Scaffold:* generate Terraform module structure for new infrastructure components
- *Rollback:* `terraform destroy` scoped to the applied resources is the rollback target

**Rollback gate:** Terraform apply is an irreversible operation (cloud resources). Guard Layer 5 classifies `terraform apply` as WARN; executor must require explicit user confirmation before the wave that calls `terraform apply`. Record the Terraform state file path in the wave receipt as the rollback reference.

**Install:** Add `terraform` MCP entry to `.mcp.json`. Requires cloud provider credentials.

---

## Laravel-Boost

**Purpose:** Laravel PHP framework toolkit — Artisan commands, Eloquent migrations, routing, code generation.

**Module integration:**
- *Platform-api-service:* Laravel is a valid API service target; laravel-boost provides Artisan tooling inline
- *Scaffold:* `artisan make:model`, `make:controller`, `make:migration` replace manual file creation
- *Migrate:* Eloquent migrations managed via `artisan migrate` and `artisan migrate:rollback`
- *Gateway-engineering:* Laravel-specific code quality (PSR standards, Eloquent query efficiency, N+1 detection)

**Install:** Add `laravel-boost` MCP entry to `.mcp.json`. Requires Laravel project in product space.

---

## Availability Pattern (all servers)

Modules check availability before using any MCP tool. Follow this pattern exactly (matches context7-integration.md contract):

```
1. Read mcp_servers.<id>.available from .wabblespec/state/runtime/runtime-state.json
2. If true: use MCP tools as documented above
3. If false or file missing: skip silently; log in receipt as <id>_enrichment.status: "unavailable"
4. Never emit a typed error for MCP unavailability
5. Never block wave execution on MCP availability
```

RuntimeProbe writes the `available` field for each server. Modules do not detect availability themselves — they read runtime-state.json only.
