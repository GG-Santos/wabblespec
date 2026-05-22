"""Generators: component scaffolding split from component_generator.py."""

from scripts.generators._common import _python_identifier, _short_description
from scripts.generators.hook import (
    generate_hook_rules_scaffold, generate_hook_readme,
    generate_hook_script, generate_hooks_json,
)
from scripts.generators.mcp import (
    generate_mcp_server_scaffold, generate_mcp_typescript_scaffold,
    generate_mcp_typescript_package, generate_mcp_typescript_config,
    generate_mcp_readme, generate_mcp_evaluation,
)
from scripts.generators.scaffolds import (
    TEMPLATE_CATALOG_FILES, TEMPLATE_FALLBACKS,
    _read_catalog_template, generate_template_scaffolds,
    generate_agent_scaffold, generate_command_scaffold,
    generate_script_scaffold, generate_eval_scaffold,
)

__all__ = [
    "_python_identifier", "_short_description",
    "generate_hook_rules_scaffold", "generate_hook_readme",
    "generate_hook_script", "generate_hooks_json",
    "generate_mcp_server_scaffold", "generate_mcp_typescript_scaffold",
    "generate_mcp_typescript_package", "generate_mcp_typescript_config",
    "generate_mcp_readme", "generate_mcp_evaluation",
    "TEMPLATE_CATALOG_FILES", "TEMPLATE_FALLBACKS",
    "_read_catalog_template", "generate_template_scaffolds",
    "generate_agent_scaffold", "generate_command_scaffold",
    "generate_script_scaffold", "generate_eval_scaffold",
]
