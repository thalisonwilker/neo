"""Testes E2E para o comando `neo tasks create` (Feature 0021)."""

import json
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()

MOCK_MEMBER = {
    "id": "member-uuid-123",
    "profile": {
        "name": "Thalyson Dev",
        "mention_name": "thalyson",
        "email_address": "thalyson@exemplo.com",
    },
}

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
            {"id": 500010, "name": "Backlog", "type": "unstarted"},
            {"id": 500012, "name": "Em Progresso", "type": "started"},
        ],
    }
]


@pytest.fixture
def mock_sc_auth():
    with patch("neo.commands.tasks.get_credential", return_value="mock-token"):
        respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
            return_value=httpx.Response(200, json=MOCK_WORKFLOWS)
        )
        yield


@respx.mock
def test_tasks_create_default_iteration_and_owner(mock_sc_auth):
    """AC-1: neo tasks create associa por padrão à última iteração e ao membro atual."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(200, json=MOCK_MEMBER)
    )

    created_story = {
        "id": 501,
        "name": "Nova Tarefa do Sprint",
        "description": "Detalhes da demanda",
        "story_type": "feature",
        "iteration_id": 21002,
        "owner_ids": ["member-uuid-123"],
        "app_url": "https://app.shortcut.com/story/501",
    }
    create_route = respx.post("https://api.app.shortcut.com/api/v3/stories").mock(
        return_value=httpx.Response(201, json=created_story)
    )

    result = runner.invoke(
        app,
        ["tasks", "create", "Nova Tarefa do Sprint", "-d", "Detalhes da demanda"],
    )

    assert result.exit_code == 0
    assert "Task #501 criada com sucesso!" in result.output
    assert "Nova Tarefa do Sprint" in result.output
    assert "Sprint 71" in result.output
    assert "https://app.shortcut.com/story/501" in result.output

    # Verifica payload enviado
    req_payload = json.loads(create_route.calls.last.request.content)
    assert req_payload["name"] == "Nova Tarefa do Sprint"
    assert req_payload["description"] == "Detalhes da demanda"
    assert req_payload["story_type"] == "feature"
    assert req_payload["iteration_id"] == 21002
    assert req_payload["owner_ids"] == ["member-uuid-123"]


@respx.mock
def test_tasks_create_without_iteration_and_owner(mock_sc_auth):
    """AC-1: Suporta desativar iteração e owner via flags --iteration none --owner none."""
    create_route = respx.post("https://api.app.shortcut.com/api/v3/stories").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 502,
                "name": "Tarefa Solta",
                "story_type": "chore",
                "iteration_id": None,
                "owner_ids": [],
            },
        )
    )

    result = runner.invoke(
        app,
        [
            "tasks",
            "create",
            "Tarefa Solta",
            "-t",
            "chore",
            "-i",
            "none",
            "--owner",
            "none",
        ],
    )

    assert result.exit_code == 0
    assert "Task #502 criada com sucesso!" in result.output
    assert "Tarefa Solta" in result.output

    req_payload = json.loads(create_route.calls.last.request.content)
    assert req_payload["name"] == "Tarefa Solta"
    assert req_payload["story_type"] == "chore"
    assert "iteration_id" not in req_payload or req_payload["iteration_id"] is None
    assert "owner_ids" not in req_payload or req_payload["owner_ids"] is None


@respx.mock
def test_tasks_create_explicit_iteration(mock_sc_auth):
    """AC-1: Permite especificar iteração por ID ou nome."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(200, json=MOCK_MEMBER)
    )
    create_route = respx.post("https://api.app.shortcut.com/api/v3/stories").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 503,
                "name": "Tarefa Sprint 70",
                "story_type": "bug",
                "iteration_id": 21001,
            },
        )
    )

    result = runner.invoke(
        app,
        ["tasks", "create", "Tarefa Sprint 70", "-t", "bug", "-i", "21001"],
    )

    assert result.exit_code == 0
    req_payload = json.loads(create_route.calls.last.request.content)
    assert req_payload["iteration_id"] == 21001
    assert req_payload["story_type"] == "bug"


@respx.mock
def test_tasks_create_json_mode(mock_sc_auth):
    """AC-1: Em modo --json, retorna o objeto JSON da story."""
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(200, json=MOCK_ITERATIONS)
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(200, json=MOCK_MEMBER)
    )
    respx.post("https://api.app.shortcut.com/api/v3/stories").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 504,
                "name": "Story JSON",
                "story_type": "feature",
                "iteration_id": 21002,
                "owner_ids": ["member-uuid-123"],
            },
        )
    )

    result = runner.invoke(
        app,
        ["--json", "tasks", "create", "Story JSON"],
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == 504
    assert data["name"] == "Story JSON"
    assert data["iteration_id"] == 21002


def test_tasks_create_missing_token():
    """Valida erro código 1 quando não há token configurado."""
    with patch("neo.commands.tasks.get_credential", return_value=None):
        result = runner.invoke(app, ["tasks", "create", "Story Sem Token"])
        assert result.exit_code == 1
        assert "Credenciais do Shortcut não configuradas" in result.output
