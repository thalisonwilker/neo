"""Testes E2E para configuração de modelos por papel e exibição no neo config show (AC-4, AC-5)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import resolve_role_model

runner = CliRunner()


def test_agent_role_model_configuration(tmp_path: Path) -> None:
    """AC-4: neo config agent set/get model.<role> com precedência."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
    ):
        # 1. Define modelo geral
        res_gen = runner.invoke(app, ["config", "agent", "set", "model", "gemini-flash"])
        assert res_gen.exit_code == 0

        # Papel refine sem modelo específico deve usar o geral
        model_refine, src_refine = resolve_role_model("refine", config_dir=tmp_path)
        assert model_refine == "gemini-flash"
        assert src_refine == "config"

        # 2. Define modelo específico para review-pr
        res_role = runner.invoke(app, ["config", "agent", "set", "model.review-pr", "gemini-pro"])
        assert res_role.exit_code == 0

        res_get = runner.invoke(app, ["config", "agent", "get", "model.review-pr", "--json"])
        assert res_get.exit_code == 0
        get_data = json.loads(res_get.output)
        assert get_data["key"] == "model.review-pr"
        assert get_data["value"] == "gemini-pro"

        # Precedência: review-pr usa o específico, refine usa o geral
        model_pr, src_pr = resolve_role_model("review-pr", config_dir=tmp_path)
        assert model_pr == "gemini-pro"
        assert src_pr == "config"

        model_refine2, _ = resolve_role_model("refine", config_dir=tmp_path)
        assert model_refine2 == "gemini-flash"


def test_config_show_displays_agent_roles() -> None:
    """AC-5: neo config show exibe papéis disponíveis no painel AGENT."""
    res_human = runner.invoke(app, ["config", "show"])
    assert res_human.exit_code == 0
    assert "AGENT : AGENTES & SDD" in res_human.output
    assert "PAPÉIS:" in res_human.output
    assert "code, refine, review-pr, review-task" in res_human.output

    res_json = runner.invoke(app, ["config", "show", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert "roles" in data["agent"]
    assert "refine" in data["agent"]["roles"]
    assert "review-pr" in data["agent"]["roles"]

