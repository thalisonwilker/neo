import json
import os
from unittest.mock import patch

import httpx
import respx
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


def test_AC_6_story_without_credentials():
    """AC-6: Erro amigável ao executar comandos de story sem token."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        res = runner.invoke(app, ["tasks", "list"])
        assert res.exit_code == 1
        assert "Credenciais do Shortcut não configuradas" in res.output


@respx.mock
def test_AC_1_story_whoami_human_and_json():
    """AC-1: neo tasks whoami exibe membro autenticado."""
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "member-uuid-1",
                "profile": {
                    "name": "Thalyson Dev",
                    "mention_name": "thalyson",
                    "email_address": "dev@neo.com",
                },
            },
        )
    )

    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "mock-token"}):
        # Modo Humano
        res_human = runner.invoke(app, ["tasks", "whoami"])
        assert res_human.exit_code == 0
        assert "Thalyson Dev" in res_human.output
        assert "@thalyson" in res_human.output

        # Modo JSON
        res_json = runner.invoke(app, ["--json", "tasks", "whoami"])
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert data["id"] == "member-uuid-1"
        assert data["name"] == "Thalyson Dev"


@respx.mock
def test_AC_2_story_list_and_mine():
    """AC-2: Listagem de stories com e sem filtro --mine."""
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": 1234,
                        "name": "Implementar endpoint de busca",
                        "story_type": "feature",
                        "labels": [{"name": "backend"}],
                    }
                ]
            },
        )
    )
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={"id": "member-1", "profile": {"mention_name": "thalyson"}},
        )
    )

    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "mock-token"}):
        # List comum
        res = runner.invoke(app, ["tasks", "list"])
        assert res.exit_code == 0
        assert "#1234" in res.output
        assert "Implementar endpoint de busca" in res.output

        # List --mine
        res_mine = runner.invoke(app, ["tasks", "list", "--mine"])
        assert res_mine.exit_code == 0
        assert "#1234" in res_mine.output


@respx.mock
def test_AC_3_story_search():
    """AC-3: Busca de stories por termo."""
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": 5678,
                        "name": "Corrigir timeout em batch",
                        "story_type": "bug",
                        "labels": [{"name": "urgente"}],
                    }
                ]
            },
        )
    )

    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "mock-token"}):
        res = runner.invoke(app, ["tasks", "search", "timeout"])
        assert res.exit_code == 0
        assert "#5678" in res.output
        assert "Corrigir timeout em batch" in res.output


@respx.mock
def test_AC_4_story_show_and_not_found():
    """AC-4: Exibição detalhada de story e erro 404."""
    respx.get("https://api.app.shortcut.com/api/v3/stories/1234").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 1234,
                "name": "Refatorar camada de dados",
                "story_type": "chore",
                "description": "Detalhes técnicos da refatoração",
                "labels": [{"name": "refactor"}],
                "app_url": "https://app.shortcut.com/story/1234",
            },
        )
    )
    respx.get("https://api.app.shortcut.com/api/v3/stories/9999").mock(
        return_value=httpx.Response(404, json={"message": "Story not found"})
    )

    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "mock-token"}):
        # Sucesso
        res = runner.invoke(app, ["tasks", "show", "1234"])
        assert res.exit_code == 0
        assert "Story #1234: Refatorar camada de dados" in res.output
        assert "CHORE" in res.output

        # Não encontrada
        res_nf = runner.invoke(app, ["tasks", "show", "9999"])
        assert res_nf.exit_code == 1
        assert "não encontrada" in res_nf.output


@respx.mock
def test_AC_5_story_analyze():
    """AC-5: Análise de contexto de story em modos Rich e JSON."""
    respx.get("https://api.app.shortcut.com/api/v3/stories/789").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 789,
                "name": "Falha no calculo de checkout",
                "story_type": "bug",
                "description": "- [ ] Validar desconto de cupom\n- [ ] Teste de carga",
                "labels": [{"name": "blocker"}],
            },
        )
    )

    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "mock-token"}):
        # Modo Humano
        res_human = runner.invoke(app, ["tasks", "analyze", "789"])
        assert res_human.exit_code == 0
        assert "bug/sc-789-falha-no-calculo" in res_human.output
        assert "[sc-789]" in res_human.output
        assert "SIM (Alerta de impedimento)" in res_human.output
        assert "Validar desconto de cupom" in res_human.output

        # Modo JSON
        res_json = runner.invoke(app, ["--json", "tasks", "analyze", "789"])
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert data["story_id"] == 789
        assert data["commit_prefix"] == "[sc-789]"
        assert data["has_blockers"] is True
        assert len(data["acceptance_criteria"]) == 2
