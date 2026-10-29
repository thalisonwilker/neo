"""Testes E2E para neo config show com seções Rich e JSON estruturado (AC-3, AC-4, AC-5)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from neo.cli import app
from neo.services.active_context import bind_task_id

runner = CliRunner()


def test_config_show_human_sections(tmp_path: Path, monkeypatch) -> None:
    """AC-3: neo config show exibe painéis GIT, TASKS e AGENT."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    # Vincula task para verificar no painel
    bind_task_id(1234, repo_path=tmp_path)

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0

    # Verifica os 3 painéis
    assert "GIT : STATUS CONFIGURAÇÃO" in result.output
    assert "TASKS : DEMANDA ATIVA" in result.output
    assert "AGENT : AGENTES & SDD" in result.output

    # Verifica campos do GIT
    assert "PROVEDOR:" in result.output
    assert "WORKSPACE:" in result.output
    assert "REPOSITÓRIO:" in result.output
    assert "BRANCH:" in result.output
    assert "TASK ATIVA:" in result.output
    assert "#1234" in result.output

    # Verifica campos do TASKS
    assert "Shortcut (API v3)" in result.output
    assert "COMMITS NA TASK:" in result.output

    # Verifica campos do AGENT
    assert "MODELO:" in result.output
    assert "USAGE:" in result.output
    assert "PROVEDOR SDD:" in result.output


def test_config_show_json_structured_payload(tmp_path: Path, monkeypatch) -> None:
    """AC-4: neo config show --json retorna payload com blocos git, tasks e agent."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    bind_task_id(9876, repo_path=tmp_path)

    result = runner.invoke(app, ["config", "show", "--json"])
    assert result.exit_code == 0

    data = json.loads(result.output)

    # Blocos principais
    assert "git" in data
    assert "tasks" in data
    assert "agent" in data
    assert "services" in data

    # Bloco git
    git_block = data["git"]
    assert "provider" in git_block
    assert "provider_source" in git_block
    assert "workspace" in git_block
    assert "repo" in git_block
    assert "branch" in git_block
    assert git_block["active_task"]["id"] == 9876

    # Bloco tasks
    tasks_block = data["tasks"]
    assert tasks_block["service"] == "shortcut"
    assert "status" in tasks_block
    assert "workspace" in tasks_block
    assert "task_commits" in tasks_block
    assert isinstance(tasks_block["task_commits"], int)

    # Bloco agent
    agent_block = data["agent"]
    assert "adapter" in agent_block
    assert "command" in agent_block
    assert "model" in agent_block
    assert "sdd_provider" in agent_block
    assert "usage" in agent_block
    assert "percent" in agent_block["usage"]
    assert "display" in agent_block["usage"]


def test_config_show_resilience_outside_git(tmp_path: Path, monkeypatch) -> None:
    """AC-5: Fora de repositório git, exibe mensagens graciosas e encerra com código 0."""
    monkeypatch.chdir(tmp_path)  # Sem .git

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Não detectado (fora de repositório Git)" in result.output
    assert "Nenhuma vinculada" in result.output

    result_json = runner.invoke(app, ["config", "show", "--json"])
    assert result_json.exit_code == 0
    data = json.loads(result_json.output)
    assert data["git"]["branch"] is None
    assert data["git"]["active_task"] is None
    assert data["tasks"]["task_commits"] == 0
