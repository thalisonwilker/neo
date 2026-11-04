"""Critérios de aceite da spec 0025 para pull requests."""

import json
from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from neo.cli import app
from neo.commands import pr
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.pr_models import PullRequest

runner = CliRunner()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Mock:
    result = Mock()
    result.list_pr_branches.return_value = ["main", "feature/x"]
    result.create_pull_request.return_value = PullRequest(
        id=17,
        title="Título",
        state="OPEN",
        source="feature/x",
        destination="main",
        url="https://example.test/pr/17",
    )
    monkeypatch.setattr(pr, "current_branch", lambda: "feature/x")
    monkeypatch.setattr(pr, "_context", lambda *args: ("demo", "team", result))
    return result


def test_AC_1_open_with_parameters_and_json(client: Mock) -> None:
    result = runner.invoke(
        app,
        [
            "git",
            "pr",
            "open",
            "--base",
            "main",
            "--title",
            "Título",
            "--description",
            "Descrição",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["id"] == 17
    client.create_pull_request.assert_called_once_with(
        "demo", "feature/x", "main", "Título", "Descrição", workspace="team"
    )


def test_AC_1_open_selects_branch_and_rejects_unpublished_source(client: Mock) -> None:
    result = runner.invoke(app, ["git", "pr", "open"], input="1\nTítulo\nDescrição\n")
    assert result.exit_code == 0, result.output
    client.list_pr_branches.return_value = ["main"]
    result = runner.invoke(
        app, ["git", "pr", "open", "--base", "main", "--title", "t", "--description", "d"]
    )
    assert result.exit_code != 0
    assert "Publique" in result.output
    assert client.create_pull_request.call_count == 1


def test_AC_2_approve_sends_message_and_reports_partial_failure(client: Mock) -> None:
    result = runner.invoke(app, ["git", "pr", "approve", "17", "--message", "ok", "--json"])
    assert result.exit_code == 0, result.output
    client.approve_pull_request.assert_called_once_with("demo", 17, "ok", workspace="team")
    client.approve_pull_request.side_effect = BitbucketError(
        "Comentário publicado, mas aprovação falhou."
    )
    result = runner.invoke(app, ["git", "pr", "approve", "17", "--message", "ok"])
    assert result.exit_code != 0
    assert "Comentário publicado" in result.output


def test_AC_3_decline_requires_confirmation(client: Mock) -> None:
    result = runner.invoke(app, ["git", "pr", "decline", "17"], input="n\n")
    assert result.exit_code != 0
    client.decline_pull_request.assert_not_called()
    result = runner.invoke(app, ["git", "pr", "decline", "17", "--yes", "--json"])
    assert result.exit_code == 0, result.output
    client.decline_pull_request.assert_called_once_with("demo", 17, workspace="team")


def test_AC_4_search_returns_normalized_results(client: Mock) -> None:
    client.search_pull_requests.return_value = [client.create_pull_request.return_value]
    result = runner.invoke(app, ["git", "pr", "search", "Título", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)[0]["id"] == 17
    client.search_pull_requests.assert_called_once_with("demo", "Título", workspace="team")


def test_AC_5_list_open_by_default_and_empty(client: Mock) -> None:
    client.list_open_pull_requests.return_value = [client.create_pull_request.return_value]
    result = runner.invoke(app, ["git", "pr", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)[0]["id"] == 17
    client.list_open_pull_requests.assert_called_once_with("demo", workspace="team")
    client.list_open_pull_requests.return_value = []
    result = runner.invoke(app, ["git", "pr", "--json"])
    assert json.loads(result.output) == []
    assert "Nenhum pull request" in runner.invoke(app, ["git", "pr"]).output
    assert runner.invoke(app, ["git", "pr", "--help"]).exit_code == 0
