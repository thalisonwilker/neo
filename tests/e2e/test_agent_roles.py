"""Testes E2E para comandos de papéis especializados neo agent roles e neo agent run --role (AC-1, AC-2, AC-3)."""

from __future__ import annotations

import json
from unittest.mock import patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


def test_agent_roles_human_and_json() -> None:
    """AC-1: neo agent roles lista todos os papéis suportados."""
    res_human = runner.invoke(app, ["agent", "roles"])
    assert res_human.exit_code == 0
    assert "Papéis de Agentes Especializados do Neo" in res_human.output
    for role_id in ("code", "refine", "review-pr", "review-task"):
        assert role_id in res_human.output

    res_json = runner.invoke(app, ["agent", "roles", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert isinstance(data, list)
    assert len(data) == 4
    role_ids = [item["id"] for item in data]
    assert "code" in role_ids
    assert "refine" in role_ids
    assert "review-pr" in role_ids
    assert "review-task" in role_ids


def test_agent_run_invalid_role_fails_with_usage_error() -> None:
    """AC-2: neo agent run com role inválido encerra com código 2."""
    res = runner.invoke(app, ["agent", "run", "--role", "deploy"])
    assert res.exit_code == int(ExitCode.USAGE_ERROR)
    assert "não é suportado" in res.output
    assert "Papéis disponíveis" in res.output


def test_agent_run_passes_role_prompt_to_adapter() -> None:
    """AC-2 e AC-3: neo agent run --role refine monta prompt contextualizado."""
    with (
        patch(
            "neo.commands.agent.validate_agent_executable",
            return_value={"resolved_path": "/bin/agy", "version": "1.0.0"},
        ),
        patch(
            "neo.commands.agent.AntigravityAdapter.run_interactive_session", return_value=0
        ) as mock_run,
        patch("neo.commands.agent.AntigravityAdapter.validate_compatibility"),
        patch("neo.commands.agent.resolve_active_task_id", return_value=2157),
        patch("neo.commands.agent.get_credential", return_value=None),
    ):
        res = runner.invoke(app, ["agent", "run", "--role", "refine"])
        assert res.exit_code == 0
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "/bin/agy" in call_args
        assert "--prompt-interactive" in call_args
        idx = call_args.index("--prompt-interactive")
        prompt = call_args[idx + 1]
        assert "Refinamento de Demandas" in prompt
        assert "#2157" in prompt
