"""Testes da validação de credenciais da feature 0023 (AC-6)."""

import json
from unittest.mock import Mock

import httpx
import pytest
from typer.testing import CliRunner

from neo.cli import app
from neo.commands.git import _common as git
from neo.commands.git.config import unset as git_unset
from neo.commands.git.config.set import api_key

runner = CliRunner()


@pytest.mark.parametrize("provider", ["github", "bitbucket"])
def test_AC_6_valid_key_is_validated_before_save(monkeypatch, provider):
    monkeypatch.setattr(git, "get_git_config_value", lambda key: (key, provider, "config"))
    client = Mock()
    factory = Mock(return_value=client)
    monkeypatch.setattr(api_key, "create_git_provider", factory)
    save = Mock()
    monkeypatch.setattr(api_key, "set_credential", save)
    inputs = "new-secret\n"
    result = runner.invoke(app, ["git", "config", "set", "api-key"], input=inputs)
    assert result.exit_code == 0, result.output
    assert "new-secret" not in result.output
    assert "Conexão efetuada" in result.output
    save.assert_called_once_with(provider, "new-secret")
    factory.assert_called_once_with(provider, "new-secret")
    client.validate_auth.assert_called_once()


def test_AC_6_invalid_or_unreachable_key_preserves_previous(monkeypatch):
    monkeypatch.setattr(git, "get_git_config_value", lambda key: (key, "github", "config"))
    client = Mock()
    client.validate_auth.side_effect = httpx.ConnectError("new-secret")
    monkeypatch.setattr(api_key, "create_git_provider", Mock(return_value=client))
    save = Mock()
    monkeypatch.setattr(api_key, "set_credential", save)
    result = runner.invoke(app, ["git", "config", "set", "api-key"], input="new-secret\n")
    assert result.exit_code != 0
    assert "new-secret" not in result.output
    assert "Conexão recusada" in result.output
    save.assert_not_called()


def test_AC_6_requires_explicit_provider_and_hidden_input(monkeypatch):
    monkeypatch.setattr(git, "get_git_config_value", lambda key: (key, None, "default"))
    result = runner.invoke(app, ["git", "config", "set", "api-key"])
    assert result.exit_code == 2
    assert "provider" in result.output
    result = runner.invoke(app, ["git", "config", "set", "api-key", "not-accepted"])
    assert result.exit_code == 2
    assert "not-accepted" not in result.output


def test_AC_6_status_and_unset_do_not_expose_environment_secret(monkeypatch):
    monkeypatch.setattr(git, "get_git_config_value", lambda key: (key, "github", "env"))
    monkeypatch.setattr(git, "get_credential_source", lambda provider: "env")
    remove = Mock(return_value=True)
    monkeypatch.setattr(git_unset, "delete_credential", remove)
    result = runner.invoke(app, ["git", "config", "get", "api-key", "--json"])
    assert json.loads(result.stdout) == {"key": "api-key", "value": "Configurado", "source": "env"}
    cancelled = runner.invoke(app, ["git", "config", "unset", "api-key"], input="n\n")
    assert cancelled.exit_code != 0
    remove.assert_not_called()
    result = runner.invoke(app, ["git", "config", "unset", "api-key", "--yes"])
    assert result.exit_code == 0
    remove.assert_called_once_with("github")
