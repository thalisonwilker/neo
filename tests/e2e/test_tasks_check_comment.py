"""Testes E2E para `neo tasks check` e `neo tasks comment` (Feature 0021)."""

import json
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


@pytest.fixture
def mock_sc_auth():
    with patch("neo.commands.tasks.get_credential", return_value="mock-token"):
        yield


# --- Testes de Checklist (AC-2 e AC-3) ---


@respx.mock
def test_tasks_check_add(mock_sc_auth):
    """AC-2: neo tasks check add adiciona item de checklist à story."""
    respx.post("https://api.app.shortcut.com/api/v3/stories/501/tasks").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 1001,
                "description": "Configurar schema no banco",
                "complete": False,
            },
        )
    )

    result = runner.invoke(
        app,
        ["tasks", "check", "add", "501", "Configurar schema no banco"],
    )

    assert result.exit_code == 0
    assert "Checklist item #1001 adicionado à story #501" in result.output
    assert "Configurar schema no banco" in result.output


@respx.mock
def test_tasks_check_add_json(mock_sc_auth):
    """AC-2: neo tasks check add em modo --json retorna payload JSON."""
    respx.post("https://api.app.shortcut.com/api/v3/stories/501/tasks").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 1002,
                "description": "Rodar migrações",
                "complete": False,
            },
        )
    )

    result = runner.invoke(
        app,
        ["--json", "tasks", "check", "add", "501", "Rodar migrações"],
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == 1002
    assert data["description"] == "Rodar migrações"
    assert data["complete"] is False


@respx.mock
def test_tasks_check_complete_and_alias(mock_sc_auth):
    """AC-3: neo tasks check complete (e alias done) marca item como concluído."""
    respx.put("https://api.app.shortcut.com/api/v3/stories/501/tasks/1001").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 1001,
                "description": "Configurar schema no banco",
                "complete": True,
            },
        )
    )

    # 1. Testar comando complete
    result = runner.invoke(
        app,
        ["tasks", "check", "complete", "501", "1001"],
    )
    assert result.exit_code == 0
    assert "marcado como [✓] Concluído" in result.output

    # 2. Testar alias done com --json
    result_alias = runner.invoke(
        app,
        ["--json", "tasks", "check", "done", "501", "1001"],
    )
    assert result_alias.exit_code == 0
    data = json.loads(result_alias.output)
    assert data["id"] == 1001
    assert data["complete"] is True


@respx.mock
def test_tasks_check_uncomplete_and_alias(mock_sc_auth):
    """AC-3: neo tasks check uncomplete (e alias undone) reabre o item."""
    respx.put("https://api.app.shortcut.com/api/v3/stories/501/tasks/1001").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 1001,
                "description": "Configurar schema no banco",
                "complete": False,
            },
        )
    )

    # 1. Testar comando uncomplete
    result = runner.invoke(
        app,
        ["tasks", "check", "uncomplete", "501", "1001"],
    )
    assert result.exit_code == 0
    assert "reaberto como [ ] Aberto" in result.output

    # 2. Testar alias undone com --json
    result_alias = runner.invoke(
        app,
        ["--json", "tasks", "check", "undone", "501", "1001"],
    )
    assert result_alias.exit_code == 0
    data = json.loads(result_alias.output)
    assert data["id"] == 1001
    assert data["complete"] is False


# --- Testes de Comentários (AC-4) ---


@respx.mock
def test_tasks_comment_add(mock_sc_auth):
    """AC-4: neo tasks comment add adiciona comentário à story."""
    respx.post("https://api.app.shortcut.com/api/v3/stories/501/comments").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 3001,
                "text": "PR aberto para revisão #42",
                "author_id": "member-uuid-123",
            },
        )
    )

    result = runner.invoke(
        app,
        ["tasks", "comment", "add", "501", "PR aberto para revisão #42"],
    )

    assert result.exit_code == 0
    assert "Comentário #3001 adicionado à story #501" in result.output
    assert "PR aberto para revisão #42" in result.output


@respx.mock
def test_tasks_comment_json(mock_sc_auth):
    """AC-4: neo tasks comment add em modo --json retorna JSON."""
    respx.post("https://api.app.shortcut.com/api/v3/stories/501/comments").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": 3003,
                "text": "Nota JSON",
            },
        )
    )

    result = runner.invoke(
        app,
        ["--json", "tasks", "comment", "add", "501", "Nota JSON"],
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["id"] == 3003
    assert data["text"] == "Nota JSON"


# --- Teste de Exibição Completa no Show (AC-5) ---


@respx.mock
def test_tasks_show_with_checklist_and_comments(mock_sc_auth):
    """AC-5: neo tasks show exibe seções de Checklist e Comentários."""
    respx.get("https://api.app.shortcut.com/api/v3/stories/501").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 501,
                "name": "Story com Itens",
                "story_type": "feature",
                "description": "Descrição detalhada",
                "tasks": [
                    {"id": 101, "description": "Item 1 Concluído", "complete": True},
                    {"id": 102, "description": "Item 2 Pendente", "complete": False},
                ],
                "comments": [
                    {"id": 201, "text": "Primeiro comentário"},
                ],
            },
        )
    )

    result = runner.invoke(app, ["tasks", "show", "501"])

    assert result.exit_code == 0
    assert "Story #501: Story com Itens" in result.output
    assert "Checklist (1/2):" in result.output
    assert "#101 Item 1 Concluído" in result.output
    assert "#102 Item 2 Pendente" in result.output
    assert "Comentários (1):" in result.output
    assert "Primeiro comentário" in result.output
