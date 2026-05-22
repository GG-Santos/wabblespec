"""Deterministic adapter for offline tests and dry-run fixtures."""

from __future__ import annotations

import json
import time

from scripts.providers.base import CompletionResult, LLMProvider, ProviderCapabilities, TriggerResult


class FakeProvider(LLMProvider):
    """Provider adapter with deterministic local behavior."""

    def __init__(self, default_model: str = "offline-deterministic"):
        self.default_model = default_model

    def complete(
        self,
        prompt: str,
        model: str | None = None,
        timeout: int = 300,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> CompletionResult:
        start = time.time()
        if "[DESCRIPTION]" in prompt:
            text = "[DESCRIPTION]Use this skill for creating, improving, testing, and packaging AI coding skills.[/DESCRIPTION]"
        else:
            text = json.dumps({"triggered": "skill" in prompt.lower(), "reasoning": "deterministic offline"})
        return CompletionResult(
            text=text,
            model=model or self.default_model,
            tokens_used=len(prompt.split()),
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(text.split()),
            duration_ms=(time.time() - start) * 1000,
            cost_estimate=0.0,
        )

    def check_skill_trigger(
        self,
        query: str,
        skill_name: str,
        skill_description: str,
        model: str | None = None,
        timeout: int = 30,
    ) -> TriggerResult:
        lowered = query.lower()
        triggered = any(term in lowered for term in ("skill", "eval", "benchmark", "trigger"))
        return TriggerResult(
            triggered=triggered,
            tool_name=f"use_skill_{skill_name.replace('-', '_')}" if triggered else None,
            confidence=1.0,
            reasoning="deterministic offline trigger rule",
        )

    def get_default_model(self) -> str:
        return self.default_model

    def get_provider_name(self) -> str:
        return "offline"

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            streaming=False,
            function_calling=False,
            skill_trigger_detection=True,
            tool_use=False,
            vision=False,
            max_context_tokens=128000,
        )

    def is_available(self) -> bool:
        return True
