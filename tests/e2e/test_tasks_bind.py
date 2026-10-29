"""Testes E2E para neo tasks bind e neo tasks unbind (AC-1)."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from neo.cli import app
from neo.services.active_context import get_bound_task_id

runner = CliRunner()


def test_tasks_bind_and_unbind_e2e(tmp_path: Path, monkeypatch) -> None:
    # Simula repositório Git no diretório temporário
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    # 1. Bind task 2157
    result = runner.invoke(app, ["tasks", "bind", "2157"])
    assert result.exit_code == 0
    assert "Task #2157 vinculada com sucesso" in result.output
    assert get_bound_task_id(tmp_path) == 2157

    # 2. Bind em formato JSON
    result_json = runner.invoke(app, ["tasks", "bind", "3000", "--json"])
    assert result_json.exit_code == 0
    data = json.loads(result_json.output)
    assert data["status"] == "success"
    assert data["story_id"] == 3000
    assert data["bound"] is True
    assert get_bound_task_id(tmp_path) == 3000

    # 3. Unbind
    result_unbind = runner.invoke(app, ["tasks", "unbind"])
    assert result_unbind.exit_code == 0
    assert "removido com sucesso" in result_unbind.output
    assert get_bound_task_id(tmp_path) is None

    # 4. Unbind novamente (sem vínculo existente)
    result_unbind_again = runner.invoke(app, ["tasks", "unbind", "--json"])
    assert result_unbind_again.exit_code == 0
    data_unbind = json.loads(result_unbind_again.output)
    assert data_unbind["status"] == "success"
    assert data_unbind["unbound"] is False


def test_tasks_bind_outside_git(tmp_path: Path, monkeypatch) -> None:
    # Diretório sem .git
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["tasks", "bind", "1234"])
    assert result.exit_code != 0
    assert "não é um repositório Git válido" in result.output
