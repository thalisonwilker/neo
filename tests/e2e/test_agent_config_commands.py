"""Testes E2E para os comandos de configuração unificada `neo config agent` (feature 0015)."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


def test_AC_1_AC_2_AC_3_agent_config_set_command_validates_and_preserves_on_failure(
    tmp_path: Path,
):
    """AC-1, AC-2 e AC-3 (0015): Configura executável válido, rejeita inválido e preserva valor anterior."""
    mock_ok = MagicMock(returncode=0, stdout="Antigravity CLI v2.0.1\n", stderr="")

    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {}, clear=True),
    ):
        # 1. Configura agy com sucesso (AC-1)
        with (
            patch("shutil.which", return_value="/usr/local/bin/agy"),
            patch("subprocess.run", return_value=mock_ok),
        ):
            res_set = runner.invoke(app, ["config", "agent", "set", "command", "agy"])
            assert res_set.exit_code == 0
            assert "command = agy" in res_set.output

        # 2. Tenta configurar binário ausente no PATH -> falha com código 2 (AC-2) e preserva 'agy' (AC-3)
        with patch("shutil.which", return_value=None):
            res_fail = runner.invoke(
                app, ["config", "agent", "set", "command", "binario-inexistente"]
            )
            assert res_fail.exit_code == int(ExitCode.USAGE_ERROR)
            assert "não foi encontrado no PATH" in res_fail.output

        res_get = runner.invoke(app, ["config", "agent", "get", "command", "--json"])
        assert res_get.exit_code == 0
        data = json.loads(res_get.output)
        assert data["key"] == "command"
        assert data["value"] == "agy"
        assert data["source"] == "config"


def test_AC_4_AC_13_AC_14_agent_config_model_sdd_list_unset_and_show(tmp_path: Path):
    """AC-4, AC-13 e AC-14 (0015): Gerencia model e sdd-provider, bloqueia segredos e atualiza neo config show."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {}, clear=True),
    ):
        # Define model e sdd-provider
        res_mod = runner.invoke(app, ["config", "agent", "set", "model", "Gemini 3.8 Flash"])
        assert res_mod.exit_code == 0

        res_sdd = runner.invoke(app, ["config", "agent", "set", "sdd-provider", "spec-kit"])
        assert res_sdd.exit_code == 0

        # Lista em JSON
        res_list = runner.invoke(app, ["config", "agent", "list", "--json"])
        assert res_list.exit_code == 0
        listed = json.loads(res_list.output)
        assert listed["model"]["value"] == "Gemini 3.8 Flash"
        assert listed["sdd-provider"]["value"] == "spec-kit"
        assert listed["adapter"]["value"] == "antigravity"

        # Lista humana
        res_list_human = runner.invoke(app, ["config", "agent", "list"])
        assert res_list_human.exit_code == 0
        assert "Gemini 3.8 Flash" in res_list_human.output
        assert "spec-kit" in res_list_human.output

        # Rejeita chave de segredo (AC-14)
        res_secret = runner.invoke(app, ["config", "agent", "set", "token", "segredo-123"])
        assert res_secret.exit_code == int(ExitCode.USAGE_ERROR)
        assert "nunca armazena credenciais" in res_secret.output
        assert "segredo-123" not in (tmp_path / "config.toml").read_text(encoding="utf-8")

        # neo config show inclui bloco agent (AC-13)
        res_show_json = runner.invoke(app, ["config", "show", "--json"])
        assert res_show_json.exit_code == 0
        show_payload = json.loads(res_show_json.output)
        assert show_payload["agent"]["model"] == "Gemini 3.8 Flash"
        assert show_payload["agent"]["sdd_provider"] == "spec-kit"

        res_show_human = runner.invoke(app, ["config", "show"])
        assert res_show_human.exit_code == 0
        assert "Agente de Codificação (agent):" in res_show_human.output
        assert "Gemini 3.8 Flash" in res_show_human.output
        assert "spec-kit" in res_show_human.output

        # Unset model
        res_unset = runner.invoke(app, ["config", "agent", "unset", "model"])
        assert res_unset.exit_code == 0
        res_get_mod = runner.invoke(app, ["config", "agent", "get", "model", "--json"])
        assert json.loads(res_get_mod.output)["value"] is None
