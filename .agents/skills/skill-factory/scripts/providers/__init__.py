#!/usr/bin/env python3
"""Provider registry with auto-detection, caching, and fallback chain.

Auto-detection priority:
1. Explicit --provider flag / SKILL_PROVIDER env var
2. Configured provider detection order
3. Provider availability checks

If no provider is detected, callers must configure one explicitly.
"""

import os
import re
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Type

from scripts.observability import write_redacted_json_log
from scripts.providers.base import (
    LLMProvider,
    ProviderNotAvailableError,
    CompletionResult,
    TriggerResult,
    ProviderCapabilities,
)
from scripts.providers.config import (
    adapter_map,
    detection_order,
    fallback_chains,
    provider_display_name,
)

# Lazy imports to avoid requiring all SDKs at once. Source of truth: config/providers.yaml.
_ADAPTER_MAP = adapter_map()
_DETECTION_ORDER = detection_order()
_FALLBACK_CHAINS = fallback_chains()

# Thread-safe provider instance cache
_provider_cache: dict[str, LLMProvider] = {}
_cache_lock = threading.Lock()


def _import_provider_class(dotpath: str) -> Type[LLMProvider]:
    """Dynamically import a provider class from its dotted path."""
    module_path, class_name = dotpath.rsplit(".", 1)
    import importlib
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_provider(name: str | None = None, **kwargs) -> LLMProvider:
    """Get a provider instance by name, with auto-detection fallback.

    Args:
        name: Provider name from config/providers.yaml.
              If None, auto-detects from environment.
        **kwargs: Extra arguments passed to the provider constructor.

    Returns:
        An initialized LLMProvider instance.

    Raises:
        ProviderNotAvailableError: If the requested provider isn't available.
    """
    # 1. Explicit name
    if name is None:
        name = os.environ.get("SKILL_PROVIDER")

    # 2. Auto-detect
    if name is None:
        name = auto_detect_provider()

    if name is None:
        raise ProviderNotAvailableError(
            "No provider detected. Set SKILL_PROVIDER or pass --provider."
        )

    name = name.lower().strip()

    if name not in _ADAPTER_MAP:
        available = ", ".join(_ADAPTER_MAP.keys())
        raise ProviderNotAvailableError(
            f"Unknown provider '{name}'. Available: {available}"
        )

    provider_class = _import_provider_class(_ADAPTER_MAP[name])
    instance = provider_class(**kwargs)
    return instance


def get_provider_cached(name: str | None = None) -> LLMProvider:
    """Get or create a cached provider instance (thread-safe).

    Use this in thread-pool paths where the same provider is needed
    many times.
    """
    resolved_name = name
    if resolved_name is None:
        resolved_name = os.environ.get("SKILL_PROVIDER")
    if resolved_name is None:
        resolved_name = auto_detect_provider()
    if resolved_name is None:
        raise ProviderNotAvailableError(
            "No provider detected. Set SKILL_PROVIDER or pass --provider."
        )
    resolved_name = resolved_name.lower().strip()

    with _cache_lock:
        if resolved_name not in _provider_cache:
            _provider_cache[resolved_name] = get_provider(resolved_name)
        return _provider_cache[resolved_name]


def auto_detect_provider() -> str | None:
    """Auto-detect the best available provider.

    Checks each provider in priority order and returns the first
    one that reports itself as available.

    Returns:
        Provider name string, or None if nothing is detected.
    """
    for provider_name in _DETECTION_ORDER:
        try:
            provider_class = _import_provider_class(_ADAPTER_MAP[provider_name])
            instance = provider_class()
            if instance.is_available():
                return provider_name
        except Exception:
            continue
    return None


def list_available_providers() -> list[dict]:
    """List all providers and their availability status.

    Returns:
        List of dicts with 'name', 'display_name', 'available', and 'default_model'.
    """
    results = []
    for name in _DETECTION_ORDER:
        try:
            provider_class = _import_provider_class(_ADAPTER_MAP[name])
            instance = provider_class()
            available = instance.is_available()
            results.append({
                "name": name,
                "display_name": provider_display_name(name),
                "available": available,
                "default_model": instance.get_default_model(),
                "capabilities": {
                    "streaming": instance.get_capabilities().streaming,
                    "function_calling": instance.get_capabilities().function_calling,
                    "native_trigger_detection": instance.get_capabilities().skill_trigger_detection,
                    "vision": instance.get_capabilities().vision,
                },
            })
        except Exception as e:
            results.append({
                "name": name,
                "display_name": provider_display_name(name),
                "available": False,
                "error": str(e),
            })
    return results


def print_provider_status():
    """Print a diagnostic table of provider availability to stderr."""
    providers = list_available_providers()
    print("\n=== Provider Status ===", file=sys.stderr)
    for p in providers:
        status = "✅ Available" if p.get("available") else "❌ Not available"
        model = p.get("default_model", "n/a")
        error = f" ({p['error']})" if p.get("error") else ""
        print(f"  {p['display_name']:20s} {status:20s} model={model}{error}", file=sys.stderr)

    detected = auto_detect_provider()
    if detected:
        print(f"\n  Auto-detected: {provider_display_name(detected)}", file=sys.stderr)
    else:
        print(f"\n  Auto-detected: None (set SKILL_PROVIDER or pass --provider)", file=sys.stderr)
    print("", file=sys.stderr)


def complete_with_fallback(
    prompt: str,
    provider_name: str | None = None,
    log_dir: str | Path | None = None,
    run_id: str | None = None,
    **kwargs,
) -> CompletionResult:
    """Complete a prompt with automatic fallback to alternative providers.

    Tries the primary provider first. If it fails, walks the fallback
    chain until one succeeds or all are exhausted.

    Args:
        prompt: The prompt text.
        provider_name: Primary provider name (auto-detected if None).
        **kwargs: Extra arguments passed to provider.complete().

    Returns:
        CompletionResult from the first provider that succeeds.

    Raises:
        ProviderNotAvailableError: If all providers in the chain fail.
    """
    from scripts.providers.base import ProviderError

    primary = provider_name
    if primary is None:
        primary = os.environ.get("SKILL_PROVIDER")
    if primary is None:
        primary = auto_detect_provider()
    if primary is None:
        raise ProviderNotAvailableError(
            "No provider detected. Set SKILL_PROVIDER or pass --provider."
        )
    primary = primary.lower().strip()

    chain = [primary] + _FALLBACK_CHAINS.get(primary, [])
    errors: list[str] = []

    run_id = run_id or uuid.uuid4().hex
    log_path = Path(log_dir) if log_dir else None

    for attempt, name in enumerate(chain, start=1):
        started = time.time()
        try:
            provider = get_provider(name)
            result = provider.complete(prompt, **kwargs)
            _write_provider_call_log(
                log_path,
                run_id,
                attempt,
                provider_name=name,
                model=kwargs.get("model") or provider.get_default_model(),
                prompt=prompt,
                status="success",
                duration_ms=(time.time() - started) * 1000,
                result=result,
                fallback_used=name != primary,
            )
            if name != primary:
                print(
                    f"  [fallback] {provider_display_name(primary)} failed, "
                    f"used {provider_display_name(name)} instead",
                    file=sys.stderr,
                )
            return result
        except Exception as e:
            _write_provider_call_log(
                log_path,
                run_id,
                attempt,
                provider_name=name,
                model=kwargs.get("model"),
                prompt=prompt,
                status="error",
                duration_ms=(time.time() - started) * 1000,
                error=e,
                fallback_used=name != primary,
            )
            errors.append(f"{provider_display_name(name)}: {e}")
            continue

    raise ProviderNotAvailableError(
        f"All providers failed:\n" + "\n".join(f"  - {e}" for e in errors)
    )


def _safe_log_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _write_provider_call_log(
    log_dir: Path | None,
    run_id: str,
    attempt: int,
    provider_name: str,
    model: str | None,
    prompt: str,
    status: str,
    duration_ms: float,
    result: CompletionResult | None = None,
    error: Exception | None = None,
    fallback_used: bool = False,
) -> None:
    """Write provider call attempt log when log_dir is configured."""
    if log_dir is None:
        return
    payload = {
        "kind": "provider_complete",
        "run_id": run_id,
        "attempt": attempt,
        "provider": provider_name,
        "model": model,
        "status": status,
        "duration_ms": round(duration_ms, 2),
        "fallback_used": fallback_used,
        "prompt": prompt,
    }
    if result is not None:
        payload.update({
            "response_text": result.text,
            "tokens_used": result.tokens_used,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "cost_estimate": result.cost_estimate,
        })
    if error is not None:
        payload.update({
            "error_class": type(error).__name__,
            "error": str(error),
        })

    filename = f"provider_{_safe_log_part(run_id)}_{attempt}_{_safe_log_part(provider_name)}.json"
    write_redacted_json_log(log_dir, filename, payload)


# Re-export key types for convenient imports
__all__ = [
    "get_provider",
    "get_provider_cached",
    "auto_detect_provider",
    "list_available_providers",
    "print_provider_status",
    "complete_with_fallback",
    "LLMProvider",
    "CompletionResult",
    "TriggerResult",
    "ProviderCapabilities",
]
