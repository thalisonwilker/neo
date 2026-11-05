"""Funções compartilhadas dos comandos."""

from __future__ import annotations

from typing import Any

from neo.config import (
    get_agent_config_value,
)


def resolve_agent_runtime(
    *,
    agent_arg: str | None = None,
    command_arg: str | None = None,
    model_arg: str | None = None,
    sdd_provider_arg: str | None = None,
) -> dict[str, Any]:
    """Resolve parâmetros efetivos do agente respeitando `CLI > ENV > config.toml > default` sem mutar config."""
    _, cfg_adapter, adapter_src = get_agent_config_value("adapter")
    _, cfg_command, command_src = get_agent_config_value("command")
    _, cfg_model, model_src = get_agent_config_value("model")
    _, cfg_sdd, sdd_src = get_agent_config_value("sdd-provider")

    adapter = (
        agent_arg.strip() if agent_arg and agent_arg.strip() else (cfg_adapter or "antigravity")
    )
    adapter_source = "cli" if (agent_arg and agent_arg.strip()) else adapter_src

    command = command_arg.strip() if command_arg and command_arg.strip() else (cfg_command or "agy")
    command_source = "cli" if (command_arg and command_arg.strip()) else command_src

    model = model_arg.strip() if model_arg and model_arg.strip() else cfg_model
    model_source = "cli" if (model_arg and model_arg.strip()) else model_src

    sdd_provider = (
        sdd_provider_arg.strip()
        if sdd_provider_arg and sdd_provider_arg.strip()
        else (cfg_sdd or "spec-driven")
    )
    sdd_source = "cli" if (sdd_provider_arg and sdd_provider_arg.strip()) else sdd_src

    return {
        "adapter": adapter,
        "adapter_source": adapter_source,
        "command": command,
        "command_source": command_source,
        "model": model,
        "model_source": model_source,
        "sdd_provider": sdd_provider,
        "sdd_source": sdd_source,
    }
