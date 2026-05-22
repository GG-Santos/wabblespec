#!/usr/bin/env python3
"""Runtime-neutral prompt builder with delimiter mapping.

Builds prompts with generic bracket delimiters by default.
"""

from pathlib import Path
from typing import Any


DELIMITER_MAP = {
    "generic": {
        "open": "[{name}]",
        "close": "[/{name}]",
        "description_tag_open": "[DESCRIPTION]",
        "description_tag_close": "[/DESCRIPTION]",
    },
}

# Language replacements for agent-agnostic prompts
LANGUAGE_MAP = {
    "generic": {
        "assistant_name": "the AI coding assistant",
        "assistant_ref": "the assistant",
        "platform": "the AI coding environment",
    },
}


class PromptBuilder:
    """Build prompts with runtime-neutral language and delimiters."""

    def __init__(self, provider: str = "generic", template_dir: Path | None = None):
        self.provider = provider
        self.template_dir = template_dir or (Path(__file__).parent.parent / "templates")
        self.delimiters = DELIMITER_MAP.get(provider, DELIMITER_MAP["generic"])
        self.language = LANGUAGE_MAP.get(provider, LANGUAGE_MAP["generic"])

    def wrap(self, name: str, content: str) -> str:
        """Wrap content in configured delimiters.

        Args:
            name: The delimiter name (e.g., "current_description", "skill_content").
            content: The text to wrap.

        Returns:
            Wrapped text string.
        """
        open_tag = self.delimiters["open"].format(name=name)
        close_tag = self.delimiters["close"].format(name=name)
        return f"{open_tag}\n{content}\n{close_tag}"


    def build_improve_prompt(
        self,
        skill_name: str,
        current_description: str,
        skill_content: str,
        scores_summary: str,
        failures_section: str = "",
        history_section: str = "",
        repair_guidance_section: str = "",
    ) -> str:
        """Build the description improvement prompt.

        This is the refactored version of improve_description.py:79-142,
        extracted as a reusable builder method.
        """
        desc_open = self.delimiters["description_tag_open"]
        desc_close = self.delimiters["description_tag_close"]

        prompt = (
            f'You are optimizing a skill description for an AI coding assistant '
            f'skill called "{skill_name}". A "skill" is a structured prompt with '
            f'progressive disclosure:\n'
            f'- Title + description: shown to {self.language["assistant_ref"]} when '
            f'deciding whether to use the skill\n'
            f'- Full SKILL.md body: loaded when {self.language["assistant_ref"]} activates the skill\n'
            f'- Bundled resources: scripts, references, examples loaded on demand\n\n'
            f'The description appears in {self.language["assistant_ref"]}\'s available skills list. '
            f'When a user sends a query, {self.language["assistant_ref"]} decides whether to '
            f'invoke the skill based on this description.\n\n'
            f'Current description:\n'
            f'{self.wrap("current_description", current_description)}\n\n'
            f'Current scores ({scores_summary}):\n'
            f'{self.wrap("scores_summary", failures_section)}\n\n'
        )

        if history_section:
            prompt += f'{history_section}\n\n'

        if repair_guidance_section:
            prompt += f'{self.wrap("repair_guidance", repair_guidance_section)}\n\n'

        prompt += (
            f'Skill content (for context):\n'
            f'{self.wrap("skill_content", skill_content)}\n\n'
            f'Based on the failures, write a new description. Generalize from failures '
            f'to broader categories of user intent. Do NOT create an expanding list of '
            f'specific queries.\n\n'
            f'Keep the description under 200 words / 1024 characters.\n\n'
            f'Tips:\n'
            f'- Use imperative: "Use this skill for..." not "this skill does..."\n'
            f'- Focus on user intent, not implementation details\n'
            f'- Make it distinctive among competing skills\n\n'
            f'Respond with ONLY the new description in {desc_open} and {desc_close} tags.'
        )

        return prompt
