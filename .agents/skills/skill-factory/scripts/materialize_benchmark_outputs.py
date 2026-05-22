#!/usr/bin/env python3
"""Materialize generated benchmark tasks into concrete skill artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is part of the packaged requirements.
    yaml = None


SCORECARD_KEYS = [
    "output_quality",
    "token_usage",
    "structure_completeness",
    "domain_specificity",
    "safety_quality",
    "testability",
    "reuse_value",
]

CHECK_KEYS = [
    "has_skill",
    "has_references",
    "has_templates",
    "has_scripts",
    "has_hooks",
    "has_agents",
    "has_mcp",
    "appears_in_eval_viewer",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "skill"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def category_key(value: str) -> str:
    return slugify(value).replace("_", "-")


def category_modules() -> dict[str, dict[str, Any]]:
    path = Path(__file__).resolve().parents[1] / "config" / "category_modules.yaml"
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    categories = data.get("categories", {})
    return categories if isinstance(categories, dict) else {}


CATEGORY_MODULES = category_modules()


def category_profile(category: str) -> dict[str, Any]:
    return CATEGORY_MODULES.get(category_key(category), {})


def text_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value or "")


def profile_line(profile: dict[str, Any], key: str, fallback: str) -> str:
    value = text_value(profile.get(key))
    return value or fallback


def output_fields(prompt: str) -> list[str]:
    lowered = prompt.lower()
    fields: list[str] = []
    for marker in ["must extract", "with", "using", "for"]:
        if marker in lowered:
            tail = prompt[lowered.index(marker) + len(marker):]
            fields = [
                slugify(part).replace("-", " ")
                for part in re.split(r",| and | then ", tail)
                if 2 <= len(part.strip()) <= 80
            ]
            break
    if len(fields) < 4:
        fields.extend(["objective", "inputs", "analysis", "risks", "recommendations", "next steps"])
    seen: set[str] = set()
    unique = []
    for field in fields:
        if field and field not in seen:
            unique.append(field)
            seen.add(field)
    return unique[:10]


def domain_lens(category: str) -> str:
    profile = category_profile(category)
    allowed = profile_line(profile, "allowed_help", "domain-specific analysis, explicit assumptions, repeatable output")
    disallowed = profile_line(profile, "disallowed_help", "fabricated certainty, unsafe overreach, unsupported claims")
    ambiguity = profile_line(profile, "ambiguity_trigger", "missing source, unclear audience, or conflicting constraints")
    redirect = profile_line(profile, "safe_redirect", "Ask for the missing evidence or produce a labeled best-effort output.")
    tags = text_value(profile.get("risk_tags")) or "none"
    return f"""## Domain Lens

- Category risk tags: {tags}.
- Allowed help: {allowed}.
- Disallowed help: {disallowed}.
- Ambiguity trigger: {ambiguity}.
- Safe redirect: {redirect}
"""


def workflow_steps(fields: list[str], category: str, variant: str) -> str:
    profile = category_profile(category)
    ambiguity = profile_line(profile, "ambiguity_trigger", "missing source, unclear audience, or conflicting constraints")
    redirect = profile_line(profile, "safe_redirect", "label assumptions and produce a bounded output")
    field_list = ", ".join(slugify(field).replace("-", "_") for field in fields[:8])
    return f"""1. Classify the request, audience, evidence quality, and whether this `{variant}` lane is the right entry point.
2. Extract required niche fields: {field_list}.
3. Apply the domain lens; if any ambiguity trigger appears ({ambiguity}), label it before drafting.
4. Build the output contract using only provided evidence, stated assumptions, and safe domain reasoning.
5. Use the safe redirect when blocked: {redirect}
6. Run the evaluation checklist and revise vague, unsafe, or untestable sections before handoff."""


def example_block(title: str, fields: list[str], category: str) -> str:
    profile = category_profile(category)
    ambiguity = profile_line(profile, "ambiguity_trigger", "missing source or unclear constraints")
    first = slugify(fields[0]).replace("-", "_") if fields else "objective"
    second = slugify(fields[1]).replace("-", "_") if len(fields) > 1 else "analysis"
    third = slugify(fields[2]).replace("-", "_") if len(fields) > 2 else "risk"
    return f"""Input: "Draft a {title.lower()} from notes with partial evidence, unclear constraints, and one possible risk: {ambiguity}."

Output excerpt:
- `{first}`: Extract the concrete user-provided fact, not an invented conclusion.
- `{second}`: State what the evidence supports and what remains unknown.
- `{third}`: Flag the domain-specific risk and the safe next check.
- `assumptions`: List assumptions separately from facts.
- `limits`: Name what the skill cannot verify.
- `next_steps`: Give the smallest testable follow-up."""


def skill_markdown(skill_name: str, title: str, category: str, prompt: str, variant: str = "core") -> str:
    fields = output_fields(prompt)
    field_rows = "\n".join(f"- `{slugify(field).replace('-', '_')}`: {field.title()}." for field in fields)
    profile = category_profile(category)
    disallowed = profile_line(profile, "disallowed_help", "fabricated certainty, unsafe overreach, unsupported claims")
    refusal = profile_line(profile, "refusal_pattern", "Decline unsafe or unsupported requests while preserving the safe task.")
    return f"""---
name: {skill_name}
description: >-
  Use this skill for {title.lower()} tasks in {category.lower()} workflows.
  It creates repeatable, testable outputs from user material while labeling
  assumptions, limits, and safety boundaries.
---

# {title}

## Purpose

Turn the user's request into a reusable {variant} workflow for: {prompt}

{domain_lens(category)}

## Activation Conditions

Use when the user asks for this niche, shares source material for it, asks for
review, or wants a repeatable template. Skip unrelated domains or requests that
would require unsupported facts.

## Inputs

- User goal or source material.
- Audience, context, constraints, and desired output format when available.
- Evidence, citations, files, logs, or examples when the task depends on them.

## Workflow

{workflow_steps(fields, category, variant)}

## Output Contract

{field_rows}
- `assumptions`: Explicit assumptions made.
- `limits`: What the output cannot prove or safely decide.
- `next_steps`: Concrete follow-up actions.

## Safety Boundaries

- Do not invent citations, measurements, legal claims, medical advice, live
  facts, or hidden evidence.
- Disallowed help for this category: {disallowed}.
- Refusal/redirect pattern: {refusal}
- Ask only when missing context changes safety, meaning, or output shape.

## Failure Modes

- Generic advice that ignores the niche fields.
- Hidden assumptions presented as facts.
- Missing safety boundary for high-impact contexts.
- Untestable output with no checklist.

## Evaluation Checklist

- Purpose is clear.
- Activation and non-use cases are clear.
- Output fields are present.
- Assumptions and limits are labeled.
- Domain lens is applied and disallowed help is avoided.
- Example is realistic for the niche.
- Safety boundary is explicit.

## Example

{example_block(title, fields, category)}
"""


def reference_doc(category: str, niche: str, prompt: str) -> str:
    profile = category_profile(category)
    return f"""# Source Notes

## Domain Assumptions

- Category: {category}
- Niche: {niche}
- Task packet: {prompt}
- Allowed help: {profile_line(profile, "allowed_help", "domain-specific analysis with labeled assumptions")}
- Disallowed help: {profile_line(profile, "disallowed_help", "unsupported certainty or unsafe overreach")}
- Ambiguity trigger: {profile_line(profile, "ambiguity_trigger", "missing source or unclear constraints")}

## Citation Placeholders

- Primary source: `<add source>`
- Secondary source: `<add source>`
- User-provided evidence: `<add file or note>`

## Boundary Notes

Use stable domain reasoning. Mark current facts, laws, prices, clinical claims,
or model/version claims as needing retrieval before final use.
"""


def template_doc(fields: list[str]) -> str:
    rows = "\n".join(f"## {field.title()}\n\n<fill {field}>\n" for field in fields[:8])
    return f"""# Output Template

{rows}
## Assumptions

- <assumption>

## Limits

- <limit>

## Next Steps

- <next step>
"""


def validator_script() -> str:
    return '''#!/usr/bin/env python3
"""Validate a benchmark artifact folder."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    missing = [name for name in ["README.md", "manifest.json", "eval.json"] if not (root / name).exists()]
    if missing:
        print("missing=" + ",".join(missing))
        return 1
    print("artifact=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def hook_script(name: str) -> str:
    return f'''#!/usr/bin/env python3
"""Benchmark {name} hook."""

from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {{}}
    print(json.dumps({{"decision": "allow", "hook": "{name}", "seen": bool(payload)}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def agent_doc(title: str) -> str:
    category = title.split("/")[0].strip() if "/" in title else ""
    return f"""---
name: reviewer
description: Reviews generated {title.lower()} artifacts for structure, specificity, safety, and testability.
---

# Reviewer Role

## Responsibilities

- Check every required file exists.
- Verify the output contract is domain-specific.
- Flag vague guidance, missing assumptions, and unsafe overreach.
- Check the category domain lens and disallowed-help boundary are present.

## Handoff

Return pass/fail findings with file paths and the smallest repair.
Escalate when safety, evidence, or missing context blocks reliable output.
"""


def mcp_doc(title: str, category: str = "") -> str:
    profile = category_profile(category)
    return f"""# MCP Integration Spec

## Purpose

Expose {title} benchmark artifacts to external review tools.

## Tools

- `list_artifacts`: returns file paths and metadata.
- `read_artifact`: reads a bounded text artifact.
- `validate_artifact`: runs structural checks and returns findings.
- `audit_domain_lens`: checks allowed/disallowed help, ambiguity triggers, and safe redirects.

## Schemas

- `list_artifacts` input: `{{ "root": "path" }}`
- `read_artifact` input: `{{ "root": "path", "artifact": "relative/path", "max_bytes": 20000 }}`
- `validate_artifact` input: `{{ "root": "path", "required_files": ["manifest.json", "eval.json"] }}`
- `audit_domain_lens` input: `{{ "root": "path", "category": "{category_key(category or title)}" }}`
- Output: `{{ "ok": true, "findings": [], "safe_fallback": "local validation" }}`

## Expected Calls

1. `list_artifacts` to enumerate manifest, eval, README, skill, and support files.
2. `read_artifact` on bounded text files only.
3. `validate_artifact` before accepting generated output.
4. `audit_domain_lens` when risk tags include `{text_value(profile.get("risk_tags")) or "none"}`.

## Fallback

If MCP is unavailable, use local file reads, `scripts/validate_artifact.py`,
and this safe redirect: {profile_line(profile, "safe_redirect", "label assumptions and keep the output bounded")}.
"""


def shared_interface_doc(category: str, niche: str, prompt: str, fields: list[str]) -> str:
    field_rows = "\n".join(f"- `{slugify(field).replace('-', '_')}`" for field in fields[:10])
    return f"""# Shared Interface

## Purpose

Coordinate the {niche} skill system for: {prompt}

{domain_lens(category)}

## Activation Conditions

Use this coordinated system when the request needs multiple role passes,
handoffs, safety review, or final verification before a reusable output.

## Input Contract

- `user_goal`: requested outcome.
- `source_material`: notes, files, claims, examples, or constraints.
- `audience`: intended user or review context.
- `safety_context`: known risks, uncertainty, and unsupported facts.

## Output Contract

{field_rows}
- `assumptions`
- `limits`
- `next_steps`

## Workflow

{workflow_steps(fields, category, "system")}

## Example

{example_block(niche, fields, category)}
"""


def shared_safety_doc(category: str) -> str:
    profile = category_profile(category)
    return f"""# Shared Safety Contract

## Safety Boundaries

- Risk tags: {text_value(profile.get("risk_tags")) or "none"}.
- Allowed help: {profile_line(profile, "allowed_help", "bounded domain analysis")}.
- Disallowed help: {profile_line(profile, "disallowed_help", "unsupported certainty or unsafe overreach")}.
- Refusal pattern: {profile_line(profile, "refusal_pattern", "Decline unsafe requests and preserve safe help")}.
- Safe redirect: {profile_line(profile, "safe_redirect", "label assumptions and ask for missing evidence")}.
"""


def shared_evaluation_doc(category: str) -> str:
    return f"""# Shared Evaluation Plan

## Evaluation Checklist

- Every role follows `shared-interface.md`.
- Every role cites the shared safety contract when a boundary appears.
- Routing selects the smallest role set that can complete the request.
- Final output includes assumptions, limits, and next steps.
- Regression warning if role outputs conflict, duplicate each other, or omit required fields.
- Domain lens check: {profile_line(category_profile(category), "ambiguity_trigger", "missing source or unclear constraints")}.
"""


def system_skill_markdown(skill_name: str, title: str, category: str, prompt: str, role: str) -> str:
    profile = category_profile(category)
    return f"""---
name: {skill_name}
description: >-
  Use this role inside the {title.lower()} system. It handles the {role}
  responsibility and delegates shared contracts to the system files.
---

# {title}

## Role Responsibility

Own the `{role}` lane for this task: {prompt}

## Workflow

1. Read `shared-interface.md`.
2. Perform only the `{role}` responsibility.
3. Apply `shared-safety.md` before proposing output.
4. Return concise findings for routing, merge, or final verification.

## Handoff Contract

- `role`: `{role}`
- `findings`: role-specific observations.
- `assumptions`: facts this role cannot verify.
- `blocked_by`: missing evidence, safety issue, or contradiction.
- `next_handoff`: next role or `final-verifier`.

## Failure Modes

- Repeating another role instead of adding role-specific value.
- Ignoring shared safety: {profile_line(profile, "disallowed_help", "unsafe or unsupported help")}.
- Producing final output before routing and verification complete.
"""


def system_roles(count: int) -> list[str]:
    base = [
        "intake-router",
        "domain-extractor",
        "output-planner",
        "safety-reviewer",
        "template-author",
        "evidence-checker",
        "example-writer",
        "test-designer",
        "integration-mapper",
        "final-verifier",
    ]
    return base[:count]


def materialize_task(task_dir: Path, overwrite: bool = False) -> bool:
    task = read_json(task_dir / "task.json")
    manifest = read_json(task_dir / "manifest.json")
    category = task["category"]["name"]
    niche = task["niche"]["name"]
    prompt = task["niche"]["tiny_prompt_packet"]
    target = task["output_target"]
    target_slug = target["slug"]
    title = niche
    files_written: list[str] = []

    def add(relative: str, content: str) -> None:
        path = task_dir / relative
        if overwrite or not path.exists():
            write_text(path, content)
        files_written.append(relative.replace("\\", "/"))

    fields = output_fields(prompt)
    if target.get("skill_count", 1) > 1:
        roles = system_roles(int(target["skill_count"]))
        add("shared-interface.md", shared_interface_doc(category, niche, prompt, fields))
        add("shared-safety.md", shared_safety_doc(category))
        add("shared-evaluation.md", shared_evaluation_doc(category))
        for index, role in enumerate(roles, start=1):
            skill_slug = f"{slugify(role)}-{slugify(niche)}"
            add(f"skills/skill-{index:02d}/SKILL.md", system_skill_markdown(skill_slug, f"{niche} / {role}", category, prompt, role))
        add(
            "routing.md",
            "# Routing Logic\n\n"
            "1. Start with `intake-router` for intent, evidence, and risk triage.\n"
            "2. Send field extraction to `domain-extractor` and structure decisions to `output-planner`.\n"
            "3. Route high-risk or ambiguous content through `safety-reviewer`.\n"
            "4. Merge role outputs only after `final-verifier` checks shared contracts.\n",
        )
        if "evaluation" in target["folders"]:
            add("evaluation-plan.md", shared_evaluation_doc(category))
        if "dependency_map" in target["folders"]:
            add(
                "dependency-map.md",
                "# Dependency Map\n\n"
                "shared-interface.md -> intake-router -> domain-extractor -> output-planner -> safety-reviewer -> final-verifier\n"
                "shared-safety.md -> every role\n"
                "shared-evaluation.md -> final-verifier\n",
            )
    else:
        add("skill/SKILL.md", skill_markdown(f"{slugify(niche)}-skill", title, category, prompt))
        if "references" in target["folders"]:
            add("references/source-notes.md", reference_doc(category, niche, prompt))
        if "templates" in target["folders"]:
            add("templates/output-template.md", template_doc(fields))
        if "scripts" in target["folders"]:
            add("scripts/validate_artifact.py", validator_script())
        if "hooks" in target["folders"]:
            add("hooks/preflight.py", hook_script("preflight"))
            add("hooks/post_generation.py", hook_script("post_generation"))
        if "agents" in target["folders"]:
            add("agents/reviewer.md", agent_doc(title))
        if "mcp" in target["folders"]:
            add("mcp/integration.md", mcp_doc(title, category))

    existing_files = set(manifest.get("files", []))
    existing_files.update(files_written)
    existing_files.update(["README.md", "prompt.txt", "task.json", "manifest.json", "eval.json"])
    manifest["files"] = sorted(existing_files)
    manifest["completed_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    manifest.setdefault("benchmark", {})["materialized"] = True
    write_json(task_dir / "manifest.json", manifest)

    checks = {key: False for key in CHECK_KEYS}
    checks["has_skill"] = True
    checks["has_references"] = "references" in target["folders"]
    checks["has_templates"] = "templates" in target["folders"]
    checks["has_scripts"] = "scripts" in target["folders"]
    checks["has_hooks"] = "hooks" in target["folders"]
    checks["has_agents"] = "agents" in target["folders"]
    checks["has_mcp"] = "mcp" in target["folders"]
    checks["appears_in_eval_viewer"] = True
    eval_payload = {
        "scorecard": {key: None for key in SCORECARD_KEYS},
        "checks": checks,
        "notes": ["Autonomous structural materialization complete. Quality scoring still requires grader evidence."],
    }
    write_json(task_dir / "eval.json", eval_payload)
    return True


def materialize_root(root: Path, limit: int | None = None, overwrite: bool = False) -> dict[str, Any]:
    task_dirs = sorted(path.parent for path in root.rglob("task.json"))
    if limit is not None:
        task_dirs = task_dirs[:limit]
    completed = 0
    errors: list[dict[str, str]] = []
    for task_dir in task_dirs:
        try:
            materialize_task(task_dir, overwrite=overwrite)
            completed += 1
        except Exception as exc:
            errors.append({"path": str(task_dir), "error": str(exc)})
    return {
        "schema_version": "benchmark-materialization-1.0",
        "root": str(root),
        "tasks_seen": len(task_dirs),
        "completed": completed,
        "errors": errors,
        "valid": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize benchmark task folders into concrete artifacts.")
    parser.add_argument("--root", type=Path, default=Path("evaluations") / "skill_benchmarks")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = materialize_root(args.root, limit=args.limit, overwrite=args.overwrite)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"materialize_benchmark_outputs: completed {report['completed']} of {report['tasks_seen']}")
        for error in report["errors"]:
            print(f"error: {error['path']}: {error['error']}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
