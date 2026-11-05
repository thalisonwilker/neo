"""Contratos estruturais dos provedores existentes (feature 0031)."""

import httpx
import pytest
import respx

from neo.integrations.git.api.bitbucket.client import BitbucketAuthError, BitbucketClient
from neo.integrations.git.api.github.client import GitHubClient
from neo.integrations.git.provider import GitProvider
from neo.services.tasks.api.shortcut.client import ShortcutClient
from neo.services.tasks.provider import TaskIterationProvider, TaskProvider, TaskWorkflowProvider


def test_git_providers_implement_contract() -> None:
    assert isinstance(GitHubClient(token="test"), GitProvider)
    assert isinstance(BitbucketClient(token="test"), GitProvider)


@respx.mock
def test_git_authentication_validates_remote_credential() -> None:
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "user"})
    )
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(401)
    )
    GitHubClient(token="test").validate_auth()
    with pytest.raises(BitbucketAuthError):
        BitbucketClient(token="invalid").validate_auth()


def test_shortcut_implements_task_and_optional_contracts() -> None:
    client = ShortcutClient(token="test")
    assert isinstance(client, TaskProvider)
    assert isinstance(client, TaskWorkflowProvider)
    assert isinstance(client, TaskIterationProvider)


def test_missing_iteration_capability_fails_before_remote_operation(monkeypatch) -> None:
    from typer.testing import CliRunner

    from neo.cli import app
    from neo.commands.tasks import _common

    class ProviderWithoutIterations:
        pass

    monkeypatch.setattr(
        _common, "_get_client", lambda service, as_json: ProviderWithoutIterations()
    )
    result = CliRunner().invoke(app, ["tasks", "iterations"])
    assert result.exit_code != 0
    assert "não oferece a capacidade de iterações" in result.output
