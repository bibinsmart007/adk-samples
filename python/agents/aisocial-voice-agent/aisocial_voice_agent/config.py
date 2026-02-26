# Copyright 2025 AISocialGrowth
#
# AISocial Voice Agent - Configuration Loader
# Loads YAML bot configs by bot_id from the configs/ directory.

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).parent / "configs"

# Cache loaded configs to avoid repeated file I/O
_config_cache: dict[str, dict[str, Any]] = {}


def load_bot_config(bot_id: str = "default") -> dict[str, Any]:
    """Load a bot configuration by bot_id.

    Looks for a YAML file named {bot_id}.yaml in the configs/ directory.
    Falls back to default.yaml if the specified config is not found.

    Args:
        bot_id: The identifier for the bot configuration to load.

    Returns:
        A dictionary containing the bot configuration.
    """
    if bot_id in _config_cache:
        return _config_cache[bot_id]

    filename = f"{bot_id}.yaml"
    path = CONFIG_DIR / filename

    if not path.exists():
        # Fallback to default config
        path = CONFIG_DIR / "default.yaml"
        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found for bot_id='{bot_id}' "
                f"and no default.yaml exists in {CONFIG_DIR}"
            )

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Override webhook_url from environment variable if set
    env_webhook = os.getenv("AISOCIAL_WEBHOOK_URL")
    if env_webhook:
        config["webhook_url"] = env_webhook

    # Override notify channel from environment variable if set
    env_notify = os.getenv("AISOCIAL_NOTIFY_CHANNEL")
    if env_notify:
        config["notify_channel"] = env_notify

    _config_cache[bot_id] = config
    return config


def list_available_configs() -> list[str]:
    """List all available bot config IDs."""
    configs = []
    if CONFIG_DIR.exists():
        for f in CONFIG_DIR.glob("*.yaml"):
            configs.append(f.stem)
    return sorted(configs)


def clear_config_cache() -> None:
    """Clear the config cache. Useful for hot-reloading configs."""
    _config_cache.clear()


def build_system_prompt(config: dict[str, Any]) -> str:
    """Build a system prompt string from a bot config.

    Combines persona, goals, escalation rules, and language
    into a single instruction string for the ADK agent.

    Args:
        config: The bot configuration dictionary.

    Returns:
        A formatted system prompt string.
    """
    persona = config.get("persona", "You are a helpful assistant.")
    goals = config.get("goals", [])
    escalation = config.get("escalation_rules", {})
    language = config.get("language", "en")

    goals_text = "\n".join(f"  - {g}" for g in goals)
    escalation_conditions = escalation.get("transfer_conditions", [])
    escalation_text = "\n".join(f"  - {c}" for c in escalation_conditions)

    prompt = f"""{persona}

Your goals for this conversation:
{goals_text}

Escalation rules:
- Transfer to human: {escalation.get('transfer_to_human', False)}
- Transfer conditions:
{escalation_text}

Always respond in language: {language}.
Be concise, professional, and helpful.
"""
    return prompt
