"""Testes E2E de aceite para a feature 0012 — listagem e filtro por iteração em `neo tasks`."""

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import set_task_columns_config

runner = CliRunner()

MOCK_ITERATIONS = [
    {
        "id": 21001,
        "name": "Sprint 70",
        "status": "done",
        "start_date": "2026-10-01",
        "end_date": "2026-10-14",
    },
    {
        "id": 21002,
        "name": "Sprint 71",
        "status": "started",
        "start_date": "2026-10-15",
        "end_date": "2026-10-29",
    },
]

MOCK_WORKFLOWS = [
    {
        "id": 500001,
        "name": "Atual",
        "states": [
            {"id": 500010, "name": "📝 - Backlog de Sprint", "type": "unstarted"},
            {"id": 500012, "name": "🚧 - Em Progresso", "type": "started"},
            {"id": 500013, "name": "✅ - Finalizado", "type": "done"},
        ],
    }
]

MOCK_STORIES = [
    {
        "id": 2153,
        "name": "Fazer um modelo web usando Design System - BI",
        "story_type": "feature",
        "workflow_state_id": 500010,
        "iteration_id": 21002,
        "labels": ["frontend"],
    },
    {
        "id": 2089,
        "name": "[New Desktop] Adições importantes pós mvp",
        "story_type": "feature",
        "workflow_state_id": 500012,
        "iteration_id": 21002,
        "labels": ["desktop"],
    },
    {
        "id": 1800,
        "name": "Story antiga da Sprint 70",
        "story_type": "chore",
        "workflow_state_id": 500013,
        "iteration_id": 21001,
        "labels": [],
    },
]


@pytest.fixture
def isolated_env(tmp_path: Path):
    """Isola Keyring e config.toml com token e colunas do Shortcut configurados."""
    stored: dict[str, str] = {"shortcut": "sc-token-valido"}
    with (
        patch("keyring.set_password", lambda s, u, p: stored.__setitem__(u, p)),
        patch("keyring.get_password", lambda s, u: stored.get(u)),
        patch("keyring.delete_password", lambda s, u: stored.pop(u, None)),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
    ):
        set_task_columns_config(
            todo=["📝 - Backlog de Sprint"],
            doing=["🚧 - Em Progresso"],
            done=["✅ - Finalizado"],
            service="shortcut",
            config_dir=tmp_path,
        )
        yield tmp_path


@respx.mock
def test_AC_1_tasks_iterations_list(isolated_env: Path):
    """AC-1: `neo tasks iterations` lista iterações da mais recente para a mais antiga e marca a atual."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )

    res = runner.invoke(app, ["tasks", "iterations"])
    assert res.exit_code == 0, res.output
    assert "Sprint 71" in res.output
    assert "[● Atual]" in res.output
    assert "Sprint 70" in res.output

    res_json = runner.invoke(app, ["--json", "tasks", "iterations"])
    assert res_json.exit_code == 0, res_json.output
    data = json.loads(res_json.output)
    assert len(data) == 2
    assert data[0]["id"] == 21002
    assert data[0]["name"] == "Sprint 71"


@respx.mock
def test_AC_2_default_latest_iteration_in_list_and_resume(isolated_env: Path):
    """AC-2: Sem `--iteration`, `neo tasks list` e `neo tasks resume` filtram pela última iteração (Sprint 71)."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={"id": "u-1", "profile": {"name": "Thalyson", "mention_name": "thalyson"}},
        )
    )
    search_route = respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(200, json={"data": MOCK_STORIES})
    )

    # 1. neo tasks list (sem -i -> filtra Sprint 71 = id 21002)
    res_list = runner.invoke(app, ["tasks", "list"])
    assert res_list.exit_code == 0, res_list.output
    assert "iteration:21002" in search_route.calls.last.request.url.params["query"]
    assert "Sprint 71" in res_list.output
    assert "#2153" in res_list.output
    assert "#1800" not in res_list.output

    # 2. neo tasks resume (sem -i -> filtra Sprint 71 = id 21002)
    res_resume = runner.invoke(app, ["tasks", "resume"])
    assert res_resume.exit_code == 0, res_resume.output
    assert "Sprint 71" in res_resume.output
    assert "#2153" in res_resume.output
    assert "#2089" in res_resume.output
    assert "#1800" not in res_resume.output


@respx.mock
def test_AC_3_explicit_iteration_filter_and_not_found(isolated_env: Path):
    """AC-3: `--iteration / -i` filtra por nome/substring/ID ou 'all', e retorna erro se inexistente."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={"id": "u-1", "profile": {"name": "Thalyson", "mention_name": "thalyson"}},
        )
    )
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(200, json={"data": MOCK_STORIES})
    )

    # Filtra pela Sprint 70 (-i 70)
    res_70 = runner.invoke(app, ["tasks", "list", "-i", "70"])
    assert res_70.exit_code == 0, res_70.output
    assert "Sprint 70" in res_70.output
    assert "#1800" in res_70.output
    assert "#2153" not in res_70.output

    # Filtra com -i all (traz todas as sprints)
    res_all = runner.invoke(app, ["tasks", "list", "-i", "all"])
    assert res_all.exit_code == 0, res_all.output
    assert "#1800" in res_all.output
    assert "#2153" in res_all.output

    # Iteração inexistente -> exit 1
    res_invalid = runner.invoke(app, ["tasks", "resume", "-i", "Sprint 999"])
    assert res_invalid.exit_code == 1
    assert "não encontrada" in res_invalid.output


@respx.mock
def test_AC_4_iteration_badge_in_resume_cards_and_json(isolated_env: Path):
    """AC-4: Card no `neo tasks resume` exibe `🔄 Sprint 71` e JSON inclui `iteration` e `iteration_id`."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={"id": "u-1", "profile": {"name": "Thalyson", "mention_name": "thalyson"}},
        )
    )
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(200, json={"data": MOCK_STORIES})
    )

    res = runner.invoke(app, ["tasks", "resume"])
    assert res.exit_code == 0, res.output
    assert "🔄 Sprint 71" in res.output

    res_json = runner.invoke(app, ["--json", "tasks", "resume"])
    assert res_json.exit_code == 0, res_json.output
    payload = json.loads(res_json.output)
    assert payload["iteration"]["id"] == 21002
    assert payload["iteration"]["name"] == "Sprint 71"
    assert payload["todo"][0]["iteration_id"] == 21002
