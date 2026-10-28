"""Testes E2E de aceite para a feature 0011 — comando `neo tasks resume` e configuração de colunas."""

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import get_task_columns_config, set_task_columns_config

runner = CliRunner()

MOCK_WORKFLOWS = [
    {
        "id": 500001,
        "name": "Atual",
        "states": [
            {"id": 500010, "name": "📝 - Backlog de Sprint", "type": "unstarted"},
            {"id": 500011, "name": "🚨 - Bug", "type": "unstarted"},
            {"id": 500012, "name": "🚧 - Em Progresso", "type": "started"},
            {"id": 500013, "name": "✅ - Finalizado", "type": "done"},
        ],
    }
]

MOCK_STORIES = [
    {
        "id": 2157,
        "name": "Adicionar o FCP ST no CSOSN 900",
        "story_type": "feature",
        "workflow_state_id": 500010,
        "labels": ["Sprint 71"],
    },
    {
        "id": 1914,
        "name": "Sistema não está baixando arquivos no iOS",
        "story_type": "bug",
        "workflow_state_id": 500011,
        "labels": ["Sprint 71"],
    },
    {
        "id": 2089,
        "name": "[New Desktop] Adições importantes pós mvp",
        "story_type": "feature",
        "workflow_state_id": 500012,
        "labels": ["Sprint 71"],
    },
    {
        "id": 2163,
        "name": "Emissao automatica de NFSe (Interno)",
        "story_type": "feature",
        "workflow_state_id": 500013,
        "labels": ["Sprint 71"],
    },
]


@pytest.fixture
def isolated_env(tmp_path: Path):
    """Isola Keyring e config.toml com token do Shortcut pré-configurado."""
    stored: dict[str, str] = {"shortcut": "sc-token-valido"}
    with (
        patch("keyring.set_password", lambda s, u, p: stored.__setitem__(u, p)),
        patch("keyring.get_password", lambda s, u: stored.get(u)),
        patch("keyring.delete_password", lambda s, u: stored.pop(u, None)),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
    ):
        yield tmp_path


@respx.mock
def test_AC_1_resume_auto_configures_when_missing(isolated_env: Path):
    """AC-1: Sem colunas configuradas, `neo tasks resume` busca workflows na API, solicita mapeamento e exibe o quadro."""
    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "u-1",
                "profile": {"name": "Thalyson", "mention_name": "thalyson"},
            },
        )
    )
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(200, json={"data": MOCK_STORIES})
    )

    # Seleciona: A fazer = 1, 2 (Backlog + Bug), Fazendo = 3 (Em Progresso), Feito = 4 (Finalizado)
    res = runner.invoke(app, ["tasks", "resume"], input="1, 2\n3\n4\n")
    assert res.exit_code == 0, res.output
    assert "Colunas configuradas com sucesso" in res.output
    assert "Quadro Resumo" in res.output
    assert "#2157" in res.output
    assert "#1914" in res.output
    assert "#2089" in res.output
    assert "#2163" in res.output

    saved = get_task_columns_config("shortcut", config_dir=isolated_env)
    assert saved == {
        "todo": ["📝 - Backlog de Sprint", "🚨 - Bug"],
        "doing": ["🚧 - Em Progresso"],
        "done": ["✅ - Finalizado"],
    }


@respx.mock
def test_AC_2_config_columns_command_and_reconfigure(isolated_env: Path):
    """AC-2: `neo tasks config columns` via flags e interativo atualiza o mapeamento."""
    res_flags = runner.invoke(
        app,
        [
            "tasks",
            "config",
            "columns",
            "--todo",
            "📝 - Backlog de Sprint, 🚨 - Bug",
            "--doing",
            "🚧 - Em Progresso",
            "--done",
            "✅ - Finalizado",
        ],
    )
    assert res_flags.exit_code == 0, res_flags.output
    cfg = get_task_columns_config("shortcut", config_dir=isolated_env)
    assert cfg is not None
    assert cfg["todo"] == ["📝 - Backlog de Sprint", "🚨 - Bug"]

    # Testa erro quando falta alguma flag
    res_partial = runner.invoke(app, ["tasks", "config", "columns", "--todo", "Backlog"])
    assert res_partial.exit_code == 1
    assert "--todo" in res_partial.output


@respx.mock
def test_AC_3_resume_renders_kanban_mine_by_default(isolated_env: Path):
    """AC-3: Com colunas já configuradas, `neo tasks resume` filtra minhas tasks e renderiza as 3 colunas."""
    set_task_columns_config(
        todo=["📝 - Backlog de Sprint", "🚨 - Bug"],
        doing=["🚧 - Em Progresso"],
        done=["✅ - Finalizado"],
        service="shortcut",
        config_dir=isolated_env,
    )

    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
    )
    member_route = respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "u-1",
                "profile": {"name": "Thalyson", "mention_name": "thalyson"},
            },
        )
    )
    search_route = respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(200, json={"data": MOCK_STORIES})
    )

    res = runner.invoke(app, ["tasks", "resume"])
    assert res.exit_code == 0, res.output
    assert member_route.called
    assert "owner:thalyson" in search_route.calls.last.request.url.params["query"]
    assert "Minhas Tasks" in res.output
    assert "A fazer (2)" in res.output
    assert "Fazendo (1)" in res.output
    assert "Feito (1)" in res.output


@respx.mock
def test_AC_4_resume_all_and_json_mode(isolated_env: Path):
    """AC-4: `--all` busca todo o board sem filtro de owner e `--json` retorna estrutura completa."""
    # 1. Em modo --json sem colunas configuradas deve falhar com exit 1
    res_unconfigured = runner.invoke(app, ["--json", "tasks", "resume"])
    assert res_unconfigured.exit_code == 1
    err_payload = json.loads(res_unconfigured.output)
    assert err_payload["status"] == "error"

    # 2. Configura colunas e executa com --all e --json
    set_task_columns_config(
        todo=["📝 - Backlog de Sprint", "🚨 - Bug"],
        doing=["🚧 - Em Progresso"],
        done=["✅ - Finalizado"],
        service="shortcut",
        config_dir=isolated_env,
    )

    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
    )
    search_route = respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(200, json={"data": MOCK_STORIES})
    )

    res_json = runner.invoke(app, ["--json", "tasks", "resume", "--all"])
    assert res_json.exit_code == 0, res_json.output
    assert "owner:" not in search_route.calls.last.request.url.params["query"]

    data = json.loads(res_json.output)
    assert data["service"] == "shortcut"
    assert data["filter"] == "all"
    assert len(data["todo"]) == 2
    assert len(data["doing"]) == 1
    assert len(data["done"]) == 1
    assert data["todo"][0]["id"] == 2157
    assert data["doing"][0]["id"] == 2089
    assert data["done"][0]["id"] == 2163
