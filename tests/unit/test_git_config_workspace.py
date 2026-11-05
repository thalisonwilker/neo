"""Testes unitários para o comando refatorado neo git config set workspace (spec 0030)."""

import os
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode, get_git_config_value, set_git_config_value

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolate_config(tmp_path: Path):
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch.dict(os.environ, {}, clear=True),
    ):
        yield


@respx.mock
def test_AC_1_interactive_workspace_selection():
    """AC-1: Seleciona workspace interativamente a partir da lista do provedor."""
    set_git_config_value("provider", "bitbucket")
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {"slug": "workspace-alpha", "name": "Workspace Alpha"},
                    {"slug": "workspace-beta", "name": "Workspace Beta"},
                ]
            },
        )
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        # Usuário seleciona o item 2 (workspace-beta)
        res = runner.invoke(app, ["git", "config", "set", "workspace"], input="2\n")
        assert res.exit_code == 0
        assert "Workspaces disponíveis:" in res.output
        assert "workspace-alpha" in res.output
        assert "workspace-beta" in res.output
        assert "workspace = workspace-beta" in res.output
        assert get_git_config_value("workspace")[1] == "workspace-beta"


@respx.mock
def test_AC_2_direct_argument_validates_existing_workspace():
    """AC-2: Passar slug válido como argumento salva direto sem prompt."""
    set_git_config_value("provider", "github")
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "my-user", "name": "My User"})
    )
    respx.get("https://api.github.com/user/orgs").mock(
        return_value=httpx.Response(200, json=[{"login": "my-org"}])
    )

    with patch.dict(os.environ, {"NEO_GITHUB_TOKEN": "mock-token"}, clear=True):
        res = runner.invoke(app, ["git", "config", "set", "workspace", "my-org"])
        assert res.exit_code == 0
        assert "workspace = my-org" in res.output
        assert get_git_config_value("workspace")[1] == "my-org"


@respx.mock
def test_AC_2_direct_argument_non_existent_workspace_fails():
    """AC-2: Passar slug inexistente encerra com código 4 (NOT_FOUND)."""
    set_git_config_value("provider", "bitbucket")
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(
            200,
            json={"values": [{"slug": "meu-ws", "name": "Meu WS"}]},
        )
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        res = runner.invoke(app, ["git", "config", "set", "workspace", "inexistente"])
        assert res.exit_code == int(ExitCode.NOT_FOUND)
        assert "não encontrado na conta autenticada" in res.output


@respx.mock
def test_AC_3_invalid_interactive_choice():
    """AC-3: Seleção fora do intervalo encerra com erro de uso (código 2)."""
    set_git_config_value("provider", "bitbucket")
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(
            200,
            json={"values": [{"slug": "meu-ws", "name": "Meu WS"}]},
        )
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        # Digita 5 quando só existe 1 opção
        res = runner.invoke(app, ["git", "config", "set", "workspace"], input="5\n")
        assert res.exit_code == int(ExitCode.USAGE_ERROR)
        assert "Seleção inválida" in res.output


def test_AC_4_unconfigured_provider_fails():
    """AC-4: Sem provedor configurado, encerra com código 2."""
    res = runner.invoke(app, ["git", "config", "set", "workspace"])
    assert res.exit_code == int(ExitCode.USAGE_ERROR)
    assert "Configure primeiro o provedor" in res.output


def test_AC_4_missing_credentials_fails():
    """AC-4: Sem credenciais, encerra com código 3 (AUTH_ERROR)."""
    set_git_config_value("provider", "github")
    with patch("neo.integrations.resolver.get_credential", return_value=None):
        res = runner.invoke(app, ["git", "config", "set", "workspace"])
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git config set api-key" in res.output


@respx.mock
def test_AC_4_empty_workspaces_list_fails():
    """AC-4: Nenhum workspace retornado pela API encerra com NOT_FOUND (código 4)."""
    set_git_config_value("provider", "bitbucket")
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json={"values": []})
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        res = runner.invoke(app, ["git", "config", "set", "workspace"])
        assert res.exit_code == int(ExitCode.NOT_FOUND)
        assert "Nenhum workspace encontrado" in res.output

