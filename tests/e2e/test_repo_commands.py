import json
import os
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolate_git_remote():
    with patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)):
        yield


def test_AC_6_repo_without_credentials():
    """AC-6: Erro amigável ao rodar comando de repositório sem credenciais."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        res = runner.invoke(app, ["git", "repo", "list"])
        assert res.exit_code == 1
        assert "Credenciais do Bitbucket não configuradas" in res.output


@respx.mock
def test_AC_1_repo_list_human_and_json():
    """AC-1: Listagem de repositórios em formato Rich e JSON."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Serviço Auth",
                        "slug": "servico-auth",
                        "is_private": True,
                        "updated_on": "2026-10-27T10:00:00Z",
                        "mainbranch": {"name": "main"},
                    }
                ]
            },
        )
    )

    with patch.dict(os.environ, {"BITBUCKET_TOKEN": "mock-token"}):
        # Modo Humano
        res_human = runner.invoke(app, ["git", "repo", "list", "--workspace", "my-workspace"])
        assert res_human.exit_code == 0
        assert "Serviço Auth" in res_human.output
        assert "servico-auth" in res_human.output

        # Modo JSON
        res_json = runner.invoke(
            app, ["--json", "git", "repo", "list", "--workspace", "my-workspace"]
        )
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert len(data) == 1
        assert data[0]["name"] == "Serviço Auth"
        assert data[0]["slug"] == "servico-auth"


@respx.mock
def test_AC_2_repo_search():
    """AC-2: Busca de repositórios por termo."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {"name": "Frontend", "slug": "frontend", "is_private": False},
                    {
                        "name": "Backend Pagamentos",
                        "slug": "backend-pagamentos",
                        "is_private": True,
                    },
                ]
            },
        )
    )

    with patch.dict(os.environ, {"BITBUCKET_TOKEN": "mock-token"}):
        res = runner.invoke(
            app, ["git", "repo", "search", "pagamentos", "--workspace", "my-workspace"]
        )
        assert res.exit_code == 0
        assert "Backend Pagamentos" in res.output
        assert "Frontend" not in res.output


@respx.mock
def test_AC_3_repo_clone():
    """AC-3: Resolução de URL e comando git clone."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace/meu-projeto").mock(
        return_value=httpx.Response(
            200,
            json={
                "name": "Meu Projeto",
                "slug": "meu-projeto",
                "is_private": True,
                "links": {
                    "clone": [
                        {"name": "ssh", "href": "git@bitbucket.org:my-workspace/meu-projeto.git"},
                        {
                            "name": "https",
                            "href": "https://bitbucket.org/my-workspace/meu-projeto.git",
                        },
                    ]
                },
            },
        )
    )

    with (
        patch.dict(os.environ, {"BITBUCKET_TOKEN": "mock-token"}),
        patch("subprocess.run") as mock_run,
    ):
        mock_run.return_value.returncode = 0
        res = runner.invoke(
            app, ["git", "repo", "clone", "meu-projeto", "--workspace", "my-workspace"]
        )
        assert res.exit_code == 0
        assert "clonado com sucesso" in res.output
        mock_run.assert_called_with(
            ["git", "clone", "git@bitbucket.org:my-workspace/meu-projeto.git"], check=False
        )


@respx.mock
def test_AC_4_repo_create():
    """AC-4: Criação de repositório com flag --yes."""
    respx.post("https://api.bitbucket.org/2.0/repositories/my-workspace/meu-novo-repo").mock(
        return_value=httpx.Response(
            201,
            json={
                "name": "meu-novo-repo",
                "slug": "meu-novo-repo",
                "is_private": True,
                "workspace": {"slug": "my-workspace"},
            },
        )
    )

    with patch.dict(os.environ, {"BITBUCKET_TOKEN": "mock-token"}):
        res = runner.invoke(
            app,
            ["git", "repo", "create", "meu-novo-repo", "--workspace", "my-workspace", "--yes"],
        )
        assert res.exit_code == 0
        assert "criado com sucesso" in res.output
