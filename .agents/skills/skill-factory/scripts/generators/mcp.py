"""MCP scaffold generators (Python FastMCP + TypeScript)."""

from __future__ import annotations

import json
from typing import Any

from scripts.generators._common import _python_identifier, _short_description
from scripts.generators.scaffolds import _render_catalog_template


def generate_mcp_server_scaffold(skill_name: str, description: str) -> str:
    """Generate a Python FastMCP stdio server scaffold."""
    service_name = _python_identifier(skill_name)
    tool_prefix = service_name
    function_name = f"{tool_prefix}_health"
    tool_body = _render_catalog_template("mcp_tool.py.j2", {
        "destructive_hint": "False",
        "function_name": function_name,
        "idempotent_hint": "True",
        "input_model": "HealthInput",
        "open_world_hint": "False",
        "read_only_hint": "True",
        "tool_description": f"Report scaffold health for the {skill_name} MCP server.",
        "tool_name": f"{tool_prefix}_health",
        "tool_title": f"{skill_name} Health",
    })

    return f'''#!/usr/bin/env python3
"""MCP stdio server scaffold for {skill_name}.

Install optional dependencies before running:
  python -m pip install mcp pydantic
"""

from __future__ import annotations

import argparse
import json
import sys
from enum import Enum
from typing import Any

SERVICE_NAME = "{service_name}"
DESCRIPTION = {_short_description(description)!r}


def health_payload() -> dict[str, Any]:
    """Return deterministic health payload for smoke tests and JSON responses."""
    return {{
        "status": "scaffold",
        "service": SERVICE_NAME,
        "description": DESCRIPTION,
        "tools": ["{tool_prefix}_health"],
        "next_step": "Replace the health tool with schema-first workflow tools.",
    }}


def load_runtime():
    """Load optional MCP runtime dependencies only when serving."""
    try:
        from mcp.server.fastmcp import FastMCP
        from pydantic import BaseModel, ConfigDict, Field
    except ImportError as exc:
        raise SystemExit(
            "Optional MCP dependencies missing. Install with: python -m pip install mcp pydantic"
        ) from exc
    return FastMCP, BaseModel, ConfigDict, Field


if "--self-test" in sys.argv:
    print(json.dumps(health_payload(), indent=2))
    raise SystemExit(0)


FastMCP, BaseModel, ConfigDict, Field = load_runtime()
mcp = FastMCP(f"{{SERVICE_NAME}}_mcp")


{tool_body}


def main() -> None:
    parser = argparse.ArgumentParser(description="MCP server scaffold for {skill_name}")
    parser.add_argument("--self-test", action="store_true", help="Print health JSON without serving MCP")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(health_payload(), indent=2))
        return

    mcp.run()


if __name__ == "__main__":
    main()
'''

def generate_mcp_typescript_scaffold(skill_name: str, description: str) -> str:
    """Generate a TypeScript MCP server scaffold."""
    service_name = _python_identifier(skill_name)
    tool_name = f"{service_name}_health"
    return f'''#!/usr/bin/env node
/**
 * TypeScript MCP stdio server scaffold for {skill_name}.
 *
 * Install optional runtime before serving:
 *   npm install
 */

import {{ McpServer }} from "@modelcontextprotocol/sdk/server/mcp.js";
import {{ StdioServerTransport }} from "@modelcontextprotocol/sdk/server/stdio.js";
import {{ z }} from "zod";

const SERVICE_NAME = "{service_name}";
const DESCRIPTION = {_short_description(description)!r};

function healthPayload() {{
  return {{
    status: "scaffold",
    service: SERVICE_NAME,
    description: DESCRIPTION,
    tools: ["{tool_name}"],
    next_step: "Replace the health tool with schema-first workflow tools.",
  }};
}}

if (process.argv.includes("--self-test")) {{
  console.log(JSON.stringify(healthPayload(), null, 2));
  process.exit(0);
}}

const server = new McpServer({{
  name: `${{SERVICE_NAME}}_mcp`,
  version: "0.1.0",
}});

server.registerTool(
  "{tool_name}",
  {{
    title: "{skill_name} Health",
    description: "Report scaffold health for {skill_name}.",
    inputSchema: {{
      response_format: z.enum(["markdown", "json"]).default("markdown"),
    }},
    annotations: {{
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: false,
    }},
  }},
  async (params) => {{
    const payload = healthPayload();
    if (params.response_format === "json") {{
      return {{ content: [{{ type: "text", text: JSON.stringify(payload, null, 2) }}] }};
    }}

    return {{
      content: [
        {{
          type: "text",
          text: `# ${{SERVICE_NAME}} MCP\\n\\nStatus: scaffold\\n\\nAvailable tools:\\n- {tool_name}`,
        }},
      ],
    }};
  }},
);

const transport = new StdioServerTransport();
await server.connect(transport);
'''

def generate_mcp_typescript_package(skill_name: str) -> dict:
    """Generate npm package metadata for optional TypeScript MCP scaffold."""
    package_name = f"{skill_name}-mcp"
    return {
        "name": package_name,
        "version": "0.1.0",
        "private": True,
        "type": "module",
        "scripts": {
            "build": "tsc --noEmit",
            "start": "tsx server.ts",
            "self-test": "tsx server.ts --self-test",
        },
        "dependencies": {
            "@modelcontextprotocol/sdk": "^1.0.0",
            "zod": "^3.23.8",
        },
        "devDependencies": {
            "tsx": "^4.19.0",
            "typescript": "^5.6.0",
        },
    }

def generate_mcp_typescript_config() -> dict:
    """Generate TypeScript config for optional MCP scaffold."""
    return {
        "compilerOptions": {
            "target": "ES2022",
            "module": "NodeNext",
            "moduleResolution": "NodeNext",
            "strict": True,
            "skipLibCheck": True,
            "noEmit": True,
        },
        "include": ["server.ts"],
    }

def generate_mcp_readme(skill_name: str) -> str:
    """Generate MCP server documentation."""
    service_name = _python_identifier(skill_name)
    return f"""# {skill_name} MCP Server

This optional MCP server scaffold exposes `{service_name}_health` over stdio.

## Install Optional Runtime

```powershell
python -m pip install mcp pydantic
```

The skill-factory project does not add those dependencies globally. The generated
plugin can decide whether MCP support is required.

## Run

```powershell
python mcp/server.py
```

## Optional TypeScript Scaffold

```powershell
cd mcp/typescript
npm install
npm run self-test
npm run build
```

The TypeScript scaffold is shape-checked by Skill Factory tests but is not part
of the default runtime gate unless Node dependencies are installed.

## Self-Test Without MCP Dependencies

```powershell
python mcp/server.py --self-test
```

This prints deterministic health JSON and exits without starting an MCP server.

## Design Rules

- Prefix tool names with the service name.
- Use schema-first input models.
- Include tool annotations: read-only, destructive, idempotent, open-world.
- Return JSON for automation and Markdown for human inspection.
- Keep error messages actionable and avoid leaking internal details.
"""

def generate_mcp_evaluation(skill_name: str) -> str:
    """Generate an MCP evaluation scaffold."""
    return f"""<evaluation>
  <qa_pair>
    <question>Call the {skill_name} MCP health tool in JSON mode. What status is reported?</question>
    <answer>scaffold</answer>
  </qa_pair>
  <qa_pair>
    <question>List the generated MCP tool names for {skill_name}.</question>
    <answer>{_python_identifier(skill_name)}_health</answer>
  </qa_pair>
</evaluation>
"""
