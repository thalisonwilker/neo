"""Testes unitários para neo git config set api-key (spec 0029)."""

import os
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode, set_git_config_value

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
def test_AC_2_bitbucket_api_key_success():
    """AC-2: Para Bitbucket, não solicita e-mail, testa conexão e emite 'Conexão efetuada'."""
    set_git_config_value("provider", "bitbucket")
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json={"values": [{"slug": "meu-ws"}]})
    )

    with (
        patch("neo.commands.git.set_credential") as mock_set_cred,
    ):
        # Apenas uma entrada no prompt: a chave de API
        res = runner.invoke(app, ["git", "config", "set", "api-key"], input="my-bb-token\n")
        assert res.exit_code == 0
        assert "Conexão efetuada" in res.output
        mock_set_cred.assert_called_once_with("bitbucket", "my-bb-token")


@respx.mock
def test_AC_2_bitbucket_api_key_failure_401():
    """AC-2: Chave inválida para Bitbucket emite 'Conexão recusada' e código 3."""
    set_git_config_value("provider", "bitbucket")
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Unauthorized"}})
    )

    with patch("neo.commands.git.set_credential") as mock_set_cred:
        res = runner.invoke(app, ["git", "config", "set", "api-key"], input="invalid-token\n")
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "Conexão recusada" in res.output
        mock_set_cred.assert_not_called()


@respx.mock
def test_AC_3_github_api_key_success():
    """AC-3: Para GitHub, testa conexão na API REST e emite 'Conexão efetuada'."""
    set_git_config_value("provider", "github")
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "octocat"})
    )

    with patch("neo.commands.git.set_credential") as mock_set_cred:
        res = runner.invoke(app, ["git", "config", "set", "api-key"], input="ghp_validtoken\n")
        assert res.exit_code == 0
        assert "Conexão efetuada" in res.output
        mock_set_cred.assert_called_once_with("github", "ghp_validtoken")


@respx.mock
def test_AC_3_github_api_key_failure_401():
    """AC-3: Chave inválida para GitHub emite 'Conexão recusada' e código 3."""
    set_git_config_value("provider", "github")
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(401, json={"message": "Bad credentials"})
    )

    with patch("neo.commands.git.set_credential") as mock_set_cred:
        res = runner.invoke(app, ["git", "config", "set", "api-key"], input="ghp_invalid\n")
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "Conexão recusada" in res.output
        mock_set_cred.assert_not_called()


def test_AC_4_api_key_passed_as_argument_fails():
    """AC-4: Informar a chave como argumento falha com erro de uso."""
    set_git_config_value("provider", "github")
    res = runner.invoke(app, ["git", "config", "set", "api-key", "secret123"])
    assert res.exit_code == int(ExitCode.USAGE_ERROR)
    assert "Não informe a chave como argumento" in res.output


def test_AC_4_empty_api_key_fails():
    """AC-4: Enviar valor vazio no prompt falha com erro de uso."""
    set_git_config_value("provider", "github")
    res = runner.invoke(app, ["git", "config", "set", "api-key"], input="   \n")
    assert res.exit_code == int(ExitCode.USAGE_ERROR)
    assert "A chave de API não pode ser vazia" in res.output
