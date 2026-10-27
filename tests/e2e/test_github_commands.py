"""Testes E2E para comandos com provedor GitHub (`neo repo`, `neo commits`, `neo workspace`)."""

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


@pytest.fixture
def mock_github_env(tmp_path: Path):
    with (
        patch("neo.integrations.resolver.get_credential", return_value="ghp_mock_token"),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
    ):
        yield tmp_path


def test_AC_7_github_without_credentials():
    """Valida AC-7: Tratamento de erros e ausência de credenciais do GitHub."""
    with patch("neo.integrations.resolver.get_credential", return_value=None):
        res = runner.invoke(app, ["repo", "list", "--provider", "github"])
        assert res.exit_code == 1
        assert "Credenciais do GitHub não configuradas" in res.output


def test_AC_2_config_set_and_get_provider(tmp_path: Path):
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
    ):
        res_set = runner.invoke(app, ["config", "set-provider", "github"])
        assert res_set.exit_code == 0
        assert "Provedor Git padrão definido com sucesso: github" in res_set.output

        res_get = runner.invoke(app, ["config", "get-provider"])
        assert res_get.exit_code == 0
        assert "github" in res_get.output

        res_invalid = runner.invoke(app, ["config", "set-provider", "gitlab"])
        assert res_invalid.exit_code == 1
        assert "Provedor Git não suportado" in res_invalid.output


@respx.mock
def test_AC_5_repo_list_and_create_github(mock_github_env: Path):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "octocat", "name": "The Octocat"})
    )
    respx.get("https://api.github.com/user/repos").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "octo-repo",
                    "private": True,
                    "description": "Repositório GitHub",
                    "default_branch": "main",
                    "updated_at": "2026-10-27T10:00:00Z",
                    "clone_url": "https://github.com/octocat/octo-repo.git",
                    "ssh_url": "git@github.com:octocat/octo-repo.git",
                    "owner": {"login": "octocat"},
                }
            ],
        )
    )
    respx.post("https://api.github.com/user/repos").mock(
        return_value=httpx.Response(
            201,
            json={
                "name": "novo-projeto",
                "private": False,
                "description": "Criado via CLI",
                "default_branch": "main",
                "updated_at": "2026-10-27T10:00:00Z",
                "clone_url": "https://github.com/octocat/novo-projeto.git",
                "ssh_url": "git@github.com:octocat/novo-projeto.git",
                "owner": {"login": "octocat"},
            },
        )
    )

    # 1. Listar repositórios no GitHub
    res_list = runner.invoke(app, ["repo", "list", "--provider", "github"])
    assert res_list.exit_code == 0
    assert "octo-repo" in res_list.output
    assert "GitHub" in res_list.output

    # 2. Criar repositório no GitHub com flag --yes
    res_create = runner.invoke(
        app,
        ["repo", "create", "novo-projeto", "--provider", "github", "--public", "--yes"],
    )
    assert res_create.exit_code == 0
    assert "novo-projeto" in res_create.output
    assert "GitHub" in res_create.output


@respx.mock
def test_AC_5_commits_search_github(mock_github_env: Path):
    respx.get("https://api.github.com/repos/octocat/octo-repo/commits").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "sha": "a1b2c3d4e5f6",
                    "commit": {
                        "message": "fix: bugfix no backend",
                        "author": {"name": "Dev", "date": "2026-10-27T12:00:00Z"},
                    },
                }
            ],
        )
    )

    res = runner.invoke(
        app,
        [
            "commits",
            "search",
            "--repo",
            "octo-repo",
            "--workspace",
            "octocat",
            "--provider",
            "github",
        ],
    )
    assert res.exit_code == 0
    assert "a1b2c3d" in res.output
    assert "fix: bugfix no backend" in res.output
    assert "GitHub" in res.output


@respx.mock
def test_AC_6_workspace_list_github(mock_github_env: Path):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "octocat", "name": "The Octocat"})
    )
    respx.get("https://api.github.com/user/orgs").mock(
        return_value=httpx.Response(200, json=[{"id": 2, "login": "acme-corp"}])
    )

    res = runner.invoke(app, ["workspace", "list", "--provider", "github"])
    assert res.exit_code == 0
    assert "octocat" in res.output
    assert "acme-corp" in res.output
    assert "GitHub" in res.output

    res_json = runner.invoke(app, ["--json", "workspace", "list", "--provider", "github"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert len(data) == 2
    assert data[0]["slug"] == "octocat"
    assert data[1]["slug"] == "acme-corp"
