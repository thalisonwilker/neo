"""Testes E2E para comandos de repositório (`neo git repo list|search|show`, features 0003 e 0014)."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolate_git_remote(tmp_path: Path):
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=(None, None, None),
        ),
        patch("neo.commands.repo.detect_git_remote_info", return_value=(None, None)),
    ):
        yield


def test_AC_5_repo_without_credentials():
    """AC-5 e AC-8 (0014): Erro código 3 ao rodar comando de repositório sem credenciais."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        res = runner.invoke(app, ["git", "repo", "list"])
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git auth login --provider bitbucket" in res.output


@respx.mock
def test_AC_5_repo_list_human_and_json():
    """AC-5 (0014): Listagem de repositórios em formato Rich e `--json`."""
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

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        res_human = runner.invoke(app, ["git", "repo", "list", "--workspace", "my-workspace"])
        assert res_human.exit_code == 0
        assert "Serviço Auth" in res_human.output
        assert "servico-auth" in res_human.output

        res_json = runner.invoke(
            app, ["git", "repo", "list", "--workspace", "my-workspace", "--json"]
        )
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert len(data) == 1
        assert data[0]["name"] == "Serviço Auth"
        assert data[0]["slug"] == "servico-auth"


@respx.mock
def test_AC_5_repo_search_with_query_option():
    """AC-5 (0014): `neo git repo search --query <termo>` e erro código 2 quando `--query` falta."""
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

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        # Sem --query -> exit 2
        res_missing = runner.invoke(app, ["git", "repo", "search", "--workspace", "my-workspace"])
        assert res_missing.exit_code == int(ExitCode.USAGE_ERROR)

        # Com --query -> exit 0
        res = runner.invoke(
            app,
            [
                "git",
                "repo",
                "search",
                "--query",
                "pagamentos",
                "--workspace",
                "my-workspace",
            ],
        )
        assert res.exit_code == 0
        assert "Backend Pagamentos" in res.output
        assert "Frontend" not in res.output


@respx.mock
def test_AC_5_repo_show_human_and_json():
    """AC-5 (0014): `neo git repo show` exibe detalhes completos e retorna código 4 se 404."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace/meu-projeto").mock(
        return_value=httpx.Response(
            200,
            json={
                "name": "Meu Projeto",
                "slug": "meu-projeto",
                "is_private": True,
                "description": "API principal",
                "mainbranch": {"name": "main"},
                "workspace": {"slug": "my-workspace"},
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
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace/inexistente").mock(
        return_value=httpx.Response(404, json={"error": {"message": "Not found"}})
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        res_show = runner.invoke(
            app,
            ["git", "repo", "show", "--repo", "meu-projeto", "--workspace", "my-workspace"],
        )
        assert res_show.exit_code == 0
        assert "Meu Projeto" in res_show.output
        assert "git@bitbucket.org:my-workspace/meu-projeto.git" in res_show.output

        res_json = runner.invoke(
            app,
            [
                "git",
                "repo",
                "show",
                "--repo",
                "meu-projeto",
                "--workspace",
                "my-workspace",
                "--json",
            ],
        )
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert data["slug"] == "meu-projeto"
        assert data["ssh_clone_url"] == "git@bitbucket.org:my-workspace/meu-projeto.git"

        res_404 = runner.invoke(
            app,
            ["git", "repo", "show", "--repo", "inexistente", "--workspace", "my-workspace"],
        )
        assert res_404.exit_code == int(ExitCode.NOT_FOUND)


def test_AC_8_legacy_repo_clone_and_create_fail_with_hint():
    """AC-8 (0014): `repo clone` e `repo create` falham com código 2 informando backlog planejado."""
    res_clone = runner.invoke(app, ["git", "repo", "clone", "meu-projeto"])
    assert res_clone.exit_code == int(ExitCode.USAGE_ERROR)
    assert "neo git repo show" in res_clone.output

    res_create = runner.invoke(app, ["git", "repo", "create", "meu-novo-repo"])
    assert res_create.exit_code == int(ExitCode.USAGE_ERROR)
    assert "backlog planejado" in res_create.output
