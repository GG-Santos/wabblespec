"""Provider configuration loaded from config/providers.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "providers.yaml"


class ProviderConfigError(RuntimeError):
    """Raised when provider configuration is missing or malformed."""


@lru_cache(maxsize=1)
def load_provider_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load provider config from YAML."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    try:
        import yaml
    except ImportError as exc:
        raise ProviderConfigError("PyYAML is required to load provider config") from exc

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProviderConfigError(f"Unable to read provider config {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ProviderConfigError("Provider config must be a YAML mapping")
    if not isinstance(data.get("providers"), dict):
        raise ProviderConfigError("Provider config missing providers mapping")

    for name, provider in data["providers"].items():
        if not isinstance(provider, dict):
            raise ProviderConfigError(f"Provider '{name}' config must be a mapping")
        if not provider.get("adapter"):
            raise ProviderConfigError(f"Provider '{name}' missing adapter")
        if not provider.get("default_model"):
            raise ProviderConfigError(f"Provider '{name}' missing default_model")

    data.setdefault("detection_order", list(data["providers"]))
    data.setdefault("fallback_chain", {})
    return data


def provider_configs() -> dict[str, dict[str, Any]]:
    return load_provider_config()["providers"]


def adapter_map() -> dict[str, str]:
    return {
        name: config["adapter"]
        for name, config in provider_configs().items()
    }


def detection_order() -> list[str]:
    config = load_provider_config()
    providers = provider_configs()
    return [
        name
        for name in config.get("detection_order", [])
        if name in providers
    ]


def fallback_chains() -> dict[str, list[str]]:
    providers = provider_configs()
    raw_chains = load_provider_config().get("fallback_chain", {})
    chains: dict[str, list[str]] = {}
    for name, chain in raw_chains.items():
        if name not in providers:
            continue
        if not isinstance(chain, list):
            raise ProviderConfigError(f"Fallback chain for '{name}' must be a list")
        chains[name] = [candidate for candidate in chain if candidate in providers]
    return chains


def provider_display_name(name: str) -> str:
    config = provider_configs().get(name, {})
    return config.get("display_name") or name


def provider_default_model(name: str) -> str:
    try:
        return provider_configs()[name]["default_model"]
    except KeyError as exc:
        raise ProviderConfigError(f"Unknown provider '{name}'") from exc
