"""Testes unitários e de integração para o comando refatorado `neo git repo list` (spec 0028)."""

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
        patch("neo.integrations.resolver.selected_repo", return_value=None),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=(None, None, None),
        ),
        patch("neo.commands.repo.detect_git_remote_info", return_value=(None, None)),
    ):
        yield


@respx.mock
def test_AC_1_repo_list_columns_and_american_dates():
    """AC-1: neo git repo list exibe Nome, Data Criação, Última atualização e Task com datas MM/DD/YYYY."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Serviço Auth",
                        "slug": "servico-auth",
                        "is_private": True,
                        "created_on": "2024-03-15T08:30:00Z",
                        "updated_on": "2026-10-27T10:00:00Z",
                        "mainbranch": {"name": "main"},
                    },
                    {
                        "name": "Backend Pagamentos",
                        "slug": "backend-pagamentos",
                        "is_private": False,
                        "created_on": "2023-01-20T12:00:00Z",
                        "updated_on": "2026-11-04T15:00:00Z",
                        "mainbranch": {"name": "main"},
                    },
                ]
            },
        )
    )

    fake_tasks_map = {
        "servico-auth": "#123",
    }

    with (
        patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True),
        patch("neo.commands.repo.get_repo_tasks_map", return_value=fake_tasks_map),
    ):
        res = runner.invoke(app, ["git", "repo", "list", "--workspace", "my-workspace"])
        assert res.exit_code == 0
        output = res.output

        # Cabeçalhos da tabela
        assert "Nome" in output
        assert "Data Criação" in output
        assert "Última atualização" in output
        assert "Task" in output

        # Repositórios e valores
        assert "Serviço Auth" in output
        assert "03/15/2024" in output
        assert "10/27/2026" in output
        assert "#123" in output

        assert "Backend Pagamentos" in output
        assert "01/20/2023" in output
        assert "11/04/2026" in output
        assert "-" in output


def test_AC_2_repo_list_without_credentials_fails():
    """AC-2: Executar sem credenciais falha com código AUTH_ERROR (3)."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        res = runner.invoke(app, ["git", "repo", "list", "--workspace", "my-workspace"])
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git config set api-key" in res.output


@respx.mock
def test_AC_2_repo_list_with_invalid_credentials_401():
    """AC-2: Credencial inválida (401) falha com código AUTH_ERROR (3)."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Unauthorized"}})
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "invalid-token"}, clear=True):
        res = runner.invoke(app, ["git", "repo", "list", "--workspace", "my-workspace"])
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git config set api-key" in res.output


@respx.mock
def test_AC_3_repo_list_json_format():
    """AC-3: Flag --json emite payload estruturado com campos e task."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Serviço Auth",
                        "slug": "servico-auth",
                        "is_private": True,
                        "created_on": "2024-03-15T08:30:00Z",
                        "updated_on": "2026-10-27T10:00:00Z",
                    }
                ]
            },
        )
    )

    fake_tasks_map = {"servico-auth": "#456"}

    with (
        patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True),
        patch("neo.commands.repo.get_repo_tasks_map", return_value=fake_tasks_map),
    ):
        res = runner.invoke(app, ["git", "repo", "list", "--workspace", "my-workspace", "--json"])
        assert res.exit_code == 0
        data = json.loads(res.output)
        assert len(data) == 1
        assert data[0]["name"] == "Serviço Auth"
        assert data[0]["slug"] == "servico-auth"
        assert data[0]["created_on"] == "2024-03-15T08:30:00Z"
        assert data[0]["updated_on"] == "2026-10-27T10:00:00Z"
        assert data[0]["task"] == "#456"


@respx.mock
def test_AC_4_repo_list_empty_workspace():
    """AC-4: Workspace sem repositórios exibe painel informativo e retorna 0."""
    respx.get("https://api.bitbucket.org/2.0/repositories/vazio-ws").mock(
        return_value=httpx.Response(200, json={"values": []})
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        res = runner.invoke(app, ["git", "repo", "list", "--workspace", "vazio-ws"])
        assert res.exit_code == 0
        assert "Nenhum repositório encontrado no workspace informado." in res.output


@respx.mock
def test_AC_5_repo_remote_list_alias_and_local_list():
    """AC-5: remote-list é alias para list; local-list exibe repos locais."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Repo Remoto",
                        "slug": "repo-remoto",
                        "is_private": False,
                        "created_on": "2024-01-01T00:00:00Z",
                        "updated_on": "2024-02-01T00:00:00Z",
                    }
                ]
            },
        )
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        # Teste do alias remote-list
        res_alias = runner.invoke(
            app, ["git", "repo", "remote-list", "--workspace", "my-workspace"]
        )
        assert res_alias.exit_code == 0
        assert "Repo Remoto" in res_alias.output
        assert "Data Criação" in res_alias.output

        # Teste do local-list
        with patch(
            "neo.commands.repo.list_repos",
            return_value=[{"path": "/Users/user/projeto", "selected": True, "task": "999"}],
        ):
            res_local = runner.invoke(app, ["git", "repo", "local-list"])
            assert res_local.exit_code == 0
            assert "Repositórios locais" in res_local.output
            assert "/Users/user/projeto" in res_local.output
            assert "Sim" in res_local.output
            assert "999" in res_local.output
