"""Hook generators: runtime-neutral lifecycle rules and optional adapters.

Extracted from component_generator.py to keep the orchestrator under ~1200 lines.
All functions are pure string/dict builders — no I/O. The generated hook
script embeds a small rule engine (load/normalize/validate/match rules)
inside its f-string so generated skills are self-contained at runtime.

Public API:
    - generate_hook_rules_scaffold(skill_name) -> str        # rules.yaml content
    - generate_hook_readme(skill_name) -> str                # README.md content
    - generate_hook_script(hook_type, skill_name) -> str     # optional adapter script
    - generate_hooks_json(skill_name, hook_types) -> dict    # neutral lifecycle manifest
"""

from __future__ import annotations

import json
from typing import Any


def generate_hook_rules_scaffold(skill_name: str) -> str:
    """Generate portable hook rule configuration.

    The scaffold ships with destructive-pattern denial and secret-aware
    warnings by default. Each rule carries a recovery message so the
    validator accepts it. Users can extend or override these in their
    own rules.yaml.
    """
    return f"""# Hook rules for {skill_name}
# Event values: bash, file, prompt, stop, all
# Actions: warn, block
# Operators: regex_match, contains, equals, not_contains, starts_with, ends_with
#
# Default-safe rules. These cover the common dangerous patterns; the
# skill author can append more rules below or override these.
rules:
  - name: warn-sensitive-file-edits
    enabled: true
    event: file
    action: warn
    conditions:
      - field: file_path
        operator: regex_match
        pattern: "\\\\.env$|credentials|secrets|id_rsa|\\\\.pem$|\\\\.ppk$"
    message: "Sensitive file edit detected. Verify secrets are not being written and the file is gitignored."

  - name: block-destructive-shell
    enabled: true
    event: bash
    action: block
    conditions:
      - field: command
        operator: regex_match
        pattern: "rm\\\\s+-rf\\\\s+[~/]|rm\\\\s+-rf\\\\s+\\\\*|mkfs|dd\\\\s+if=|>\\\\s*/dev/sd[a-z]"
    message: "Destructive shell command detected (rm -rf on home/root, mkfs, dd, or device-write). Confirm the target path and backup strategy before proceeding."

  - name: block-chmod-recursive-permissive
    enabled: true
    event: bash
    action: block
    conditions:
      - field: command
        operator: regex_match
        pattern: "chmod\\\\s+-R\\\\s+777|chmod\\\\s+777\\\\s+-R"
    message: "chmod -R 777 makes files world-writable recursively, which is rarely intended. Use a tighter mode (e.g., 755 for dirs + 644 for files) and a smaller scope."

  - name: block-fork-bomb
    enabled: true
    event: bash
    action: block
    conditions:
      - field: command
        operator: regex_match
        pattern: ":\\\\(\\\\)\\\\s*{{\\\\s*:\\\\|:&"
    message: "Fork-bomb pattern detected. This will exhaust process limits and crash the host. Refuse and ask the user what they actually intended."

  - name: block-curl-pipe-to-shell
    enabled: true
    event: bash
    action: block
    conditions:
      - field: command
        operator: regex_match
        pattern: "(?:curl|wget)\\\\s+[^|]*\\\\|\\\\s*(?:sh|bash|zsh)"
    message: "Curl/wget piped directly to a shell runs unaudited remote code. Download the script first, inspect it, then execute as a separate step."

  - name: block-ssh-key-exfiltration
    enabled: true
    event: bash
    action: block
    conditions:
      - field: command
        operator: regex_match
        pattern: "cat\\\\s+\\\\S*\\\\.ssh/|cat\\\\s+/etc/shadow|cat\\\\s+\\\\S*\\\\.aws/credentials"
    message: "Reading SSH keys, /etc/shadow, or AWS credentials. This pattern is associated with key exfiltration; verify the intent or refuse."

  - name: warn-eval-of-input
    enabled: true
    event: bash
    action: warn
    conditions:
      - field: command
        operator: regex_match
        pattern: "\\\\beval\\\\s+[\\\\$\\\\\\"\\\\\\`]"
    message: "eval on a variable or command substitution can execute attacker-controlled input. Verify the source of the evaluated string."
"""

def generate_hook_readme(skill_name: str) -> str:
    """Generate hook lifecycle docs."""
    return f"""# {skill_name} Lifecycle Rules

The generated hook layer is runtime-neutral:

- `lifecycle.json` maps portable lifecycle events to rule files.
- `rules.yaml` stores event/action/condition rules.
- Runtime adapters may translate portable decisions into host-specific hook APIs.

Portable events: `before_tool`, `after_tool`, `before_stop`, `on_user_prompt`.
Portable decisions: `warn`, `deny`, `block`.
"""

def generate_hook_script(hook_type: str, skill_name: str) -> str:
    """Generate a lifecycle hook Python script."""
    return f'''#!/usr/bin/env python3
"""{hook_type} hook for {skill_name}."""

import json
import re
import sys
from pathlib import Path

SCAFFOLD_MESSAGE = (
    "{skill_name} {hook_type} hook scaffold is installed but has no custom "
    "rules yet. Add rule checks in evaluate() when the skill requires them."
)


def main():
    try:
        input_data = json.load(sys.stdin)
        hook_event = input_data.get("hook_event_name", "{hook_type}")
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {{}})

        result = evaluate(hook_event, tool_name, tool_input, input_data)
        print(json.dumps(result), file=sys.stdout)

    except Exception as e:
        print(json.dumps({{"systemMessage": f"{hook_type} hook error: {{e}}"}}), file=sys.stdout)
    finally:
        sys.exit(0)


def evaluate(hook_event: str, tool_name: str, tool_input: dict, input_data: dict) -> dict:
    """Evaluate the event and return a hook response.

    Returns:
        {{}} for no action.
        {{"systemMessage": "..."}} for warnings.
        {{"decision": "deny", "systemMessage": "..."}} for tool blocks.
        {{"decision": "block", "reason": "..."}} for stop blocks.
    """
    _ = SCAFFOLD_MESSAGE
    valid_rules, invalid_rules = normalize_rules(load_rules())
    matches = match_rules(valid_rules, hook_event, tool_name, tool_input, input_data)
    if not matches:
        if invalid_rules:
            return {{"systemMessage": "\\n\\n".join(format_invalid_rule(rule) for rule in invalid_rules)}}
        return {{}}

    blocking = [rule for rule in matches if rule.get("action") == "block"]
    warnings = [rule for rule in matches if rule.get("action") != "block"]
    selected = blocking or warnings
    invalid_message = "\\n\\n".join(format_invalid_rule(rule) for rule in invalid_rules)
    matched_message = "\\n\\n".join(format_rule_message(rule) for rule in selected)
    message = "\\n\\n".join(part for part in (invalid_message, matched_message) if part)

    if blocking:
        if hook_event in ("before_stop", "stop"):
            return {{"decision": "block", "reason": message, "systemMessage": message}}
        if hook_event in ("before_tool", "after_tool"):
            return {{"decision": "deny", "systemMessage": message}}

    return {{"systemMessage": message}}


def load_rules() -> list:
    """Load generated hook rules from rules.yaml."""
    rules_path = Path(__file__).with_name("rules.yaml")
    if not rules_path.exists():
        return []

    text = rules_path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed.get("rules", [])
        return []
    except json.JSONDecodeError:
        return parse_simple_rules_yaml(text)


ALLOWED_EVENTS = {{"all", "bash", "file", "prompt", "stop"}}
ALLOWED_ACTIONS = {{"warn", "block"}}
ALLOWED_OPERATORS = {{"regex_match", "contains", "equals", "not_contains", "starts_with", "ends_with"}}
ALLOWED_FIELDS = {{
    "command", "file_path", "new_text", "new_string", "old_text", "old_string",
    "content", "user_prompt", "reason",
}}


def normalize_rules(rules: list) -> tuple[list, list]:
    """Split valid rules from invalid user-authored rules."""
    valid = []
    invalid = []
    for rule in rules:
        if not isinstance(rule, dict):
            invalid.append({{"name": "non-object-rule", "_error": "rule must be an object"}})
            continue

        errors = validate_rule(rule)
        if errors:
            copied = dict(rule)
            copied["_error"] = "; ".join(errors)
            invalid.append(copied)
        else:
            valid.append(rule)
    return valid, invalid


def validate_rule(rule: dict) -> list[str]:
    """Validate supported hook-rule subset; return error strings."""
    errors = []
    name = str(rule.get("name", "")).strip()
    if not name:
        errors.append("missing name")
    if str(rule.get("event", "all")).lower() not in ALLOWED_EVENTS:
        errors.append(f"unsupported event: {{rule.get('event')}}")
    if str(rule.get("action", "warn")).lower() not in ALLOWED_ACTIONS:
        errors.append(f"unsupported action: {{rule.get('action')}}")

    conditions = rule.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        errors.append("conditions must be a non-empty list")
        return errors

    for index, condition in enumerate(conditions, start=1):
        if not isinstance(condition, dict):
            errors.append(f"condition {{index}} must be an object")
            continue
        field = str(condition.get("field", "")).strip()
        operator = str(condition.get("operator", "contains")).strip()
        pattern = str(condition.get("pattern", ""))
        if field not in ALLOWED_FIELDS:
            errors.append(f"condition {{index}} unsupported field: {{field}}")
        if operator not in ALLOWED_OPERATORS:
            errors.append(f"condition {{index}} unsupported operator: {{operator}}")
        if pattern == "":
            errors.append(f"condition {{index}} pattern must be non-empty")
        if operator == "regex_match":
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(f"condition {{index}} invalid regex: {{exc}}")

    if str(rule.get("action", "warn")).lower() == "block" and not str(rule.get("message", "")).strip():
        errors.append("blocking rules require a recovery message")
    return errors


def format_invalid_rule(rule: dict) -> str:
    """Format invalid user-authored rule without dropping it silently."""
    name = rule.get("name", "unnamed-rule")
    return f"**[invalid-rule: {{name}}]**\\n{{rule.get('_error', 'invalid rule')}}"


def parse_simple_rules_yaml(text: str) -> list:
    """Parse the generated rules.yaml subset without external dependencies."""
    rules = []
    current = None
    current_condition = None
    in_conditions = False

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "rules:":
            continue

        if stripped.startswith("- name:"):
            current = {{"name": parse_scalar(stripped.split(":", 1)[1])}}
            rules.append(current)
            current_condition = None
            in_conditions = False
            continue

        if current is None:
            continue

        if stripped == "conditions:":
            current["conditions"] = []
            current_condition = None
            in_conditions = True
            continue

        if in_conditions and stripped.startswith("- field:"):
            current_condition = {{"field": parse_scalar(stripped.split(":", 1)[1])}}
            current.setdefault("conditions", []).append(current_condition)
            continue

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        if in_conditions and current_condition is not None and key in {{"operator", "pattern"}}:
            current_condition[key] = parse_scalar(value)
        else:
            current[key] = parse_scalar(value)
            if key not in {{"conditions"}}:
                in_conditions = False

    return rules


def parse_scalar(value: str):
    """Parse a tiny YAML scalar subset."""
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value.replace("\\\\\\\\", "\\\\")


def match_rules(rules: list, hook_event: str, tool_name: str, tool_input: dict, input_data: dict) -> list:
    """Return enabled rules whose conditions all match input."""
    matched = []
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        if not event_matches(rule.get("event", "all"), hook_event, tool_name):
            continue
        conditions = rule.get("conditions") or []
        if conditions and all(condition_matches(c, tool_name, tool_input, input_data) for c in conditions):
            matched.append(rule)
    return matched


def event_matches(rule_event: str, hook_event: str, tool_name: str) -> bool:
    """Map hook/tool data to portable event names."""
    rule_event = str(rule_event or "all").lower()
    if rule_event == "all":
        return True
    normalized_event = str(hook_event or "").lower()
    normalized_tool = str(tool_name or "").lower()
    if rule_event == "prompt":
        return normalized_event in ("on_user_prompt", "prompt", "user_prompt")
    if rule_event == "stop":
        return normalized_event in ("before_stop", "stop")
    if rule_event == "bash":
        return normalized_tool in ("bash", "shell", "run_shell_command")
    if rule_event == "file":
        return normalized_tool in ("write", "edit", "multiedit", "write_files", "edit_files")
    return False


def condition_matches(condition: dict, tool_name: str, tool_input: dict, input_data: dict) -> bool:
    """Evaluate one field/operator/pattern condition."""
    value = extract_field(str(condition.get("field", "")), tool_name, tool_input, input_data)
    if value is None:
        return False
    value = str(value)
    pattern = str(condition.get("pattern", ""))
    operator = condition.get("operator", "contains")

    if operator == "regex_match":
        try:
            return re.search(pattern, value, re.IGNORECASE) is not None
        except re.error:
            return False
    if operator == "contains":
        return pattern in value
    if operator == "equals":
        return pattern == value
    if operator == "not_contains":
        return pattern not in value
    if operator == "starts_with":
        return value.startswith(pattern)
    if operator == "ends_with":
        return value.endswith(pattern)
    return False


def extract_field(field: str, tool_name: str, tool_input: dict, input_data: dict):
    """Extract condition field from hook input."""
    if field in tool_input:
        return tool_input[field]
    if field in input_data:
        return input_data[field]
    normalized_tool = str(tool_name or "").lower()
    if field == "command" and normalized_tool in ("bash", "shell", "run_shell_command"):
        return tool_input.get("command", "")
    if field == "file_path" and normalized_tool in ("write", "edit", "multiedit", "write_files", "edit_files"):
        return tool_input.get("file_path", "")
    if field in ("new_text", "new_string"):
        if normalized_tool in ("multiedit", "edit_files"):
            return " ".join(edit.get("new_string", "") for edit in tool_input.get("edits", []))
        return tool_input.get("new_string", "") or tool_input.get("content", "")
    if field in ("old_text", "old_string"):
        return tool_input.get("old_string", "")
    if field == "content":
        return tool_input.get("content", "") or tool_input.get("new_string", "")
    if field == "user_prompt":
        return input_data.get("user_prompt", "")
    if field == "reason":
        return input_data.get("reason", "")
    return None


def format_rule_message(rule: dict) -> str:
    """Format matched rule for hook output."""
    name = rule.get("name", "unnamed-rule")
    message = rule.get("message", "Rule matched.")
    return f"**[{{name}}]**\\n{{message}}"


if __name__ == "__main__":
    main()
'''

def generate_hooks_json(skill_name: str, hook_types: list[str] | None = None) -> dict:
    """Generate a runtime-neutral lifecycle manifest."""
    hook_types = hook_types or ["before_tool"]

    events = []
    for ht in hook_types:
        events.append({
            "name": ht,
            "rules": "hooks/rules.yaml",
            "on_block": "deny" if ht == "before_tool" else "warn",
        })

    return {
        "version": "1.0",
        "description": f"{skill_name} plugin lifecycle rules",
        "events": events,
    }
