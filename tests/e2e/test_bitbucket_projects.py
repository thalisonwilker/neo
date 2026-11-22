"""Aceite da seleção de projeto Bitbucket com Key (features 0034 e 0035)."""

import json
from unittest.mock import Mock, patch

import httpx
import pytest
from typer.testing import CliRunner

from neo.cli import app
from neo.config import (
    get_bitbucket_project,
    get_git_config_value,
    set_bitbucket_workspace_project,
    set_git_config_value,
)
from neo.integrations.git.models import GitProject, GitRepo, GitWorkspace

runner = CliRunner()


@pytest.fixture
def context(tmp_path, monkeypatch):
    monkeypatch.setattr("neo.config.DEFAULT_CONFIG_DIR", tmp_path)
    monkeypatch.setattr("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml")
    monkeypatch.delenv("NEO_GIT_WORKSPACE", raising=False)
    monkeypatch.delenv("NEO_GIT_PROVIDER", raising=False)
    set_git_config_value("provider", "bitbucket")
    set_bitbucket_workspace_project("old", "OLD_KEY")
    client = Mock()
    client.list_workspaces.return_value = [GitWorkspace(slug="new", name="Novo")]
    client.list_projects.return_value = [GitProject(name="Easygestor", key="EASY")]
    with patch(
        "neo.commands.git.config.set.workspace.resolve_git_provider",
        return_value=("bitbucket", client),
    ):
        yield client


def test_AC_1_project_selected_and_persisted(context):
    result = runner.invoke(app, ["git", "config", "set", "workspace", "new"], input="1\n")
    assert result.exit_code == 0, result.output
    assert "Easygestor (EASY)" in result.output
    assert "projeto = EASY" in result.output
    assert get_git_config_value("workspace")[1] == "new"
    assert get_bitbucket_project("new") == "EASY"
    assert get_bitbucket_project("old") is None


@pytest.mark.parametrize("mode", ["empty", "failure", "invalid", "cancel"])
def test_AC_2_failures_preserve_previous_configuration(context, mode):
    if mode == "empty":
        context.list_projects.return_value = []
    elif mode == "failure":
        context.list_projects.side_effect = httpx.ConnectError("private")
    choice = "2\n" if mode == "invalid" else ""
    result = runner.invoke(app, ["git", "config", "set", "workspace", "new"], input=choice)
    assert result.exit_code != 0
    assert "private" not in result.output
    assert get_git_config_value("workspace")[1] == "old"
    assert get_bitbucket_project("old") == "OLD_KEY"


def test_AC_3_project_shown_only_for_bitbucket(context):
    for args in (["git", "config", "show", "--json"], ["--json", "git", "config", "show"]):
        result = runner.invoke(app, args)
        assert json.loads(result.output)["project"]["value"] == "OLD_KEY"
    assert "project:" in runner.invoke(app, ["git", "config", "show"]).output
    set_git_config_value("provider", "github")
    assert "project" not in json.loads(
        runner.invoke(app, ["git", "config", "show", "--json"]).output
    )
    assert "project:" not in runner.invoke(app, ["git", "config", "show"]).output


def test_AC_5_json_is_noninteractive_and_preserves_state(context):
    result = runner.invoke(app, ["--json", "git", "config", "set", "workspace", "new"])
    assert result.exit_code == 2
    assert "interativo" in json.loads(result.output)["message"]
    assert get_git_config_value("workspace")[1] == "old"
    assert get_bitbucket_project("old") == "OLD_KEY"
    context.list_projects.assert_not_called()


def test_AC_4_missing_or_mismatched_project_blocks_creation(context, tmp_path):
    client = Mock()
    for workspace in ("new", None):
        with (
            patch(
                "neo.commands.git.repo.create.common.resolve_git_provider",
                return_value=("bitbucket", client),
            ),
            patch(
                "neo.commands.git.repo.create.common.resolve_git_workspace_and_source",
                return_value=(workspace, "test"),
            ),
        ):
            result = runner.invoke(app, ["git", "repo", "create", "demo", "--path", str(tmp_path)])
        assert result.exit_code == 2
        assert "neo git config set workspace" in result.output
    client.create_repository.assert_not_called()


def test_AC_4_creation_sends_selected_project(context, tmp_path):
    client = Mock()
    client.create_repository.return_value = GitRepo(name="demo", slug="demo")
    with (
        patch(
            "neo.commands.git.repo.create.common.resolve_git_provider",
            return_value=("bitbucket", client),
        ),
        patch(
            "neo.commands.git.repo.create.common.resolve_git_workspace_and_source",
            return_value=("old", "test"),
        ),
    ):
        result = runner.invoke(app, ["git", "repo", "create", "demo", "--path", str(tmp_path)])
    assert result.exit_code == 1  # URL de clone ausente, depois da criação remota simulada.
    assert client.create_repository.call_args.kwargs["project_id"] == "OLD_KEY"


def test_AC_2_write_failure_preserves_previous_configuration(context):
    with patch("neo.config.os.replace", side_effect=OSError("failed")):
        result = runner.invoke(app, ["git", "config", "set", "workspace", "new"], input="1\n")
    assert result.exit_code == 1
    assert get_git_config_value("workspace")[1] == "old"
    assert get_bitbucket_project("old") == "OLD_KEY"
