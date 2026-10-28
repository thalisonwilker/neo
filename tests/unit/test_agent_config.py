"""Testes unitários para configuração do agente e provedores SDD (feature 0015)."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from neo.config import (
    get_agent_config_value,
    list_agent_config_values,
    set_agent_config_value,
    unset_agent_config_value,
    validate_agent_adapter,
    validate_agent_config_key,
    validate_sdd_provider,
)


def test_AC_4_agent_config_crud_and_aliases(tmp_path: Path):
    """AC-4 (0015): Persistir, consultar, listar e remover command, model, sdd-provider e adapter."""
    with patch.dict(os.environ, {}, clear=True):
        # Defaults
        assert get_agent_config_value("command", config_dir=tmp_path) == (
            "command",
            "agy",
            "default",
        )
        assert get_agent_config_value("model", config_dir=tmp_path) == (
            "model",
            None,
            "default",
        )
        assert get_agent_config_value("sdd-provider", config_dir=tmp_path) == (
            "sdd-provider",
            "spec-driven",
            "default",
        )
        assert get_agent_config_value("adapter", config_dir=tmp_path) == (
            "adapter",
            "antigravity",
            "default",
        )

        # Set usando aliases documentados (agent-code -> command, sdd -> sdd-provider)
        k_cmd, v_cmd = set_agent_config_value(
            "agent-code", "/usr/local/bin/agy", config_dir=tmp_path
        )
        assert k_cmd == "command"
        assert v_cmd == "/usr/local/bin/agy"

        k_mod, v_mod = set_agent_config_value("model", "Gemini 3.8 Flash", config_dir=tmp_path)
        assert k_mod == "model"
        assert v_mod == "Gemini 3.8 Flash"

        k_sdd, v_sdd = set_agent_config_value("sdd", "spec-kit", config_dir=tmp_path)
        assert k_sdd == "sdd-provider"
        assert v_sdd == "spec-kit"

        # Consulta persistida
        assert get_agent_config_value("command", config_dir=tmp_path) == (
            "command",
            "/usr/local/bin/agy",
            "config",
        )
        assert get_agent_config_value("model", config_dir=tmp_path) == (
            "model",
            "Gemini 3.8 Flash",
            "config",
        )
        assert get_agent_config_value("sdd-provider", config_dir=tmp_path) == (
            "sdd-provider",
            "spec-kit",
            "config",
        )

        all_vals = list_agent_config_values(config_dir=tmp_path)
        assert all_vals["command"]["value"] == "/usr/local/bin/agy"
        assert all_vals["model"]["value"] == "Gemini 3.8 Flash"
        assert all_vals["sdd-provider"]["value"] == "spec-kit"

        # Unset independente
        assert unset_agent_config_value("model", config_dir=tmp_path) is True
        assert unset_agent_config_value("model", config_dir=tmp_path) is False
        assert get_agent_config_value("model", config_dir=tmp_path) == (
            "model",
            None,
            "default",
        )
        # Outras chaves permanecem intactas
        assert get_agent_config_value("command", config_dir=tmp_path)[1] == "/usr/local/bin/agy"


def test_AC_4_agent_config_env_precedence(tmp_path: Path):
    """AC-4 (0015): Variáveis NEO_AGENT_CODE, NEO_AGENT_MODEL e NEO_SDD_PROVIDER têm precedência sobre config.toml."""
    set_agent_config_value("command", "agy", config_dir=tmp_path)
    set_agent_config_value("model", "Modelo Config", config_dir=tmp_path)
    set_agent_config_value("sdd-provider", "spec-driven", config_dir=tmp_path)

    env = {
        "NEO_AGENT_CODE": "agy-env",
        "NEO_AGENT_MODEL": "Gemini 3.1 Pro (High)",
        "NEO_SDD_PROVIDER": "spec-kit",
        "NEO_AGENT_ADAPTER": "antigravity",
    }
    with patch.dict(os.environ, env, clear=True):
        assert get_agent_config_value("command", config_dir=tmp_path) == (
            "command",
            "agy-env",
            "env",
        )
        assert get_agent_config_value("model", config_dir=tmp_path) == (
            "model",
            "Gemini 3.1 Pro (High)",
            "env",
        )
        assert get_agent_config_value("sdd-provider", config_dir=tmp_path) == (
            "sdd-provider",
            "spec-kit",
            "env",
        )


def test_AC_14_forbidden_secret_keys_and_invalid_values(tmp_path: Path):
    """AC-14 (0015): Chaves de credenciais/segredos são bloqueadas em neo config agent."""
    for secret_key in ("token", "api-key", "api_key", "secret", "password", "auth", "credentials"):
        with pytest.raises(ValueError, match="nunca armazena credenciais"):
            validate_agent_config_key(secret_key)

    with pytest.raises(ValueError, match="Chave de configuração de agente desconhecida"):
        validate_agent_config_key("chave-inexistente")

    with pytest.raises(ValueError, match="Provedor SDD não suportado"):
        validate_sdd_provider("outro-sdd")

    with pytest.raises(ValueError, match="Adaptador de agente não suportado"):
        validate_agent_adapter("outro-agente")

    with pytest.raises(ValueError, match="não pode ser vazio"):
        set_agent_config_value("model", "   ", config_dir=tmp_path)
