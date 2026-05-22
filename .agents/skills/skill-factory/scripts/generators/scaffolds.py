"""Component-scaffold generators: agents, commands, scripts, eval files, templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.template_contract import (
    extract_placeholders,
    render_template_text,
    validate_context,
)


TEMPLATE_CATALOG_FILES = [
    "agent.md.j2",
    "command.md.j2",
    "eval.json.j2",
    "hook.py.j2",
    "matcher.md.j2",
    "mcp_tool.py.j2",
    "plugin.json.j2",
    "report.md.j2",
    "rules.yaml.j2",
    "schema.json.j2",
    "surface_registry.json.j2",
]

TEMPLATE_FALLBACKS = {
    "agent.md.j2": "# {{ agent_title }}\n\n{{ role_description }}\n\n## machine_readable_contract\n\nHAND OFF findings upward.\n",
    "command.md.j2": "---\ndescription: {{ command_description_json }}\nargument-hint: {{ argument_hint }}\nrequired-capabilities: {{ required_capabilities_json }}\n---\n\n# {{ command_title }}\n\n{{ command_description }}\n\n## Workflow\n\n{{ workflow_steps }}\n\n## Output Contract\n\n{{ output_contract }}\n\n## Failure Modes\n\n{{ failure_modes }}\n",
    "eval.json.j2": "{\n  \"skill_name\": \"{{ skill_name }}\",\n  \"eval_version\": \"{{ eval_version }}\",\n  \"evals\": [{\"id\": \"{{ eval_id }}\", \"name\": \"{{ eval_name }}\", \"prompt\": \"{{ eval_prompt }}\", \"expected_output\": \"{{ expected_output }}\", \"assertions\": {{ assertions_json }}}],\n  \"trigger_evals\": {{ trigger_evals_json }}\n}\n",
    "hook.py.j2": "import json\nimport sys\n\ninput_data = json.load(sys.stdin)\nprint(json.dumps({}))\n",
    "matcher.md.j2": "# {{ matcher_title }}\n\n{{ fields_table }}\n",
    "mcp_tool.py.j2": "@mcp.tool(name=\"{{ tool_name }}\")\nasync def {{ function_name }}(params: {{ input_model }}) -> str:\n    \"\"\"{{ tool_description }}.\"\"\"\n    return \"{{ tool_title }}\"\n",
    "plugin.json.j2": "{\n  \"name\": \"{{ plugin_name }}\",\n  \"version\": \"{{ plugin_version }}\"\n}\n",
    "report.md.j2": "# {{ report_title }}\n\n{{ summary }}\n",
    "rules.yaml.j2": "rules:\n  - name: {{ rule_name }}\n",
    "schema.json.j2": "{\n  \"title\": \"{{ schema_title }}\",\n  \"type\": \"object\"\n}\n",
    "surface_registry.json.j2": "{\n  \"version\": \"{{ registry_version }}\",\n  \"plugin\": \"{{ plugin_name }}\"\n}\n",
}

def _read_catalog_template(filename: str) -> str:
    """Read root template catalog file with fallback for standalone generator use."""
    root = Path(__file__).resolve().parents[2]
    candidates = [
        root / "templates" / filename,
        Path(__file__).resolve().parents[1] / "templates" / filename,
    ]
    for path in candidates:
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            continue
    return TEMPLATE_FALLBACKS[filename]

def _render_catalog_template(filename: str, context: dict[str, Any]) -> str:
    """Render a catalog template after validating its simple placeholders."""
    template_text = _read_catalog_template(filename)
    fields = extract_placeholders(template_text)
    findings = validate_context(filename, fields, context)
    errors = [finding for finding in findings if finding["severity"] == "error"]
    if errors:
        messages = "; ".join(finding["message"] for finding in errors)
        raise ValueError(f"Cannot render {filename}: {messages}")

    rendered, render_findings = render_template_text(filename, template_text, context)
    render_errors = [
        finding for finding in render_findings if finding["severity"] == "error"
    ]
    if render_errors:
        messages = "; ".join(finding["message"] for finding in render_errors)
        raise ValueError(f"Cannot render {filename}: {messages}")
    return rendered

def generate_template_scaffolds(skill_name: str) -> dict[str, str]:
    """Generate reusable template files from canonical catalog templates."""
    _ = skill_name
    return {
        f"templates/{filename}": _read_catalog_template(filename)
        for filename in TEMPLATE_CATALOG_FILES
    }

def generate_agent_scaffold(
    agent_name: str,
    role: str,
    tools: list[str] | None = None,
    skill_name: str | None = None,
) -> str:
    """Generate an agent definition markdown file from the agent template."""
    capabilities = tools or ["read_files", "list_files", "search_files"]
    trigger_context = (
        f"{agent_name} work in {skill_name} factory runs"
        if skill_name
        else f"{agent_name} work"
    )
    return _render_catalog_template("agent.md.j2", {
        "agent_name": agent_name,
        "agent_title": agent_name.replace("-", " ").title(),
        "capabilities_json": capabilities,
        "role_description": role,
        "trigger_context": trigger_context,
    })

def generate_command_scaffold(
    command_name: str,
    description: str,
    tools: list[str] | None = None,
    argument_hint: str = "Optional arguments",
    workflow_steps: str | None = None,
    output_contract: str | None = None,
    failure_modes: str | None = None,
) -> str:
    """Generate a slash command markdown file from the command template."""
    capabilities = tools or ["read_files", "list_files", "search_files"]
    return _render_catalog_template("command.md.j2", {
        "argument_hint": argument_hint,
        "command_description": description,
        "command_description_json": json.dumps(description),
        "command_title": command_name.replace("-", " ").title(),
        "required_capabilities_json": capabilities,
        "workflow_steps": workflow_steps or "\n".join([
            "1. Parse arguments and identify the target scope.",
            "2. Load only the files or references needed for the command.",
            "3. Execute the requested operation.",
            "4. Run the command's verification gate.",
            "5. Report changed files, checks, and remaining risks.",
        ]),
        "output_contract": output_contract or "\n".join([
            "- `status`: `pass`, `warn`, or `fail`.",
            "- `target`: path, artifact, or scope handled.",
            "- `changed_files`: files modified by the command.",
            "- `verification`: checks run and results.",
            "- `remaining_risks`: unresolved blockers or skipped checks.",
        ]),
        "failure_modes": failure_modes or "\n".join([
            "- Running with guessed destructive scope.",
            "- Reporting success before verification.",
            "- Hiding partial completion behind generic prose.",
        ]),
    })

def generate_script_scaffold(script_name: str, purpose: str) -> str:
    """Generate a Python script scaffold."""
    return f'''#!/usr/bin/env python3
"""{purpose}

Usage: python -m scripts.{script_name} [options]
"""

import argparse
import json
import sys
from pathlib import Path


def process(input_data: dict) -> dict:
    """Main processing logic.

    Args:
        input_data: Parsed input from CLI args or stdin.

    Returns:
        Result dict to be output as JSON.
    """
    if not isinstance(input_data, dict):
        return {{
            "status": "error",
            "error": "input_data must be a JSON object",
        }}

    task = input_data.get("task") or input_data.get("query") or input_data.get("sample")
    if task in (None, ""):
        return {{
            "status": "error",
            "error": "Provide a non-empty 'task' field or equivalent input.",
        }}

    return {{
        "status": "scaffold",
        "result": {{
            "accepted": True,
            "received_fields": sorted(input_data.keys()),
        }},
        "message": (
            "Scaffold accepted input. Replace process() with domain logic when "
            "the skill needs deterministic computation."
        )
    }}


def main():
    parser = argparse.ArgumentParser(description="{purpose}")
    parser.add_argument("--input", type=Path, help="Input JSON file")
    parser.add_argument("--output", type=Path, help="Output path (default: stdout)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    if args.input:
        input_data = json.loads(args.input.read_text())
    elif not sys.stdin.isatty():
        input_data = json.load(sys.stdin)
    else:
        print("Error: Provide --input or pipe JSON to stdin", file=sys.stderr)
        sys.exit(1)

    result = process(input_data)

    output_json = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(output_json)
        if args.verbose:
            print(f"Written to {{args.output}}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
'''

def generate_eval_scaffold(skill_name: str) -> dict:
    """Generate an evaluations scaffold from the eval template."""
    assertions = [
        {
            "text": "Output names the skill or generated artifact",
            "type": "content_contains",
            "target": "output",
            "pattern": skill_name,
        }
    ]
    trigger_evals = [
        {"query": f"Help me with {skill_name.replace('-', ' ')}", "should_trigger": True},
        {"query": "Write a fibonacci function in Python", "should_trigger": False},
    ]
    rendered = _render_catalog_template("eval.json.j2", {
        "assertions_json": assertions,
        "eval_id": "1",
        "eval_name": "basic_usage",
        "eval_prompt": f"Use the {skill_name} skill for a representative user request.",
        "eval_version": "1.0",
        "expected_output": (
            f"A concise result that follows the {skill_name} process and names "
            "generated artifacts."
        ),
        "skill_name": skill_name,
        "trigger_evals_json": trigger_evals,
    })
    return json.loads(rendered)
