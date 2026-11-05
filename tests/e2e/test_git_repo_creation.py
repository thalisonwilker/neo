"""Critérios AC-4 e AC-5 da feature 0023, com Git local e provedor simulado."""

import os
import subprocess
from pathlib import Path
from unittest.mock import Mock

import httpx
import typer
from typer.testing import CliRunner

from neo.commands.git import local_repo
from neo.commands.git.repo.create import create_repo
from neo.commands.git.repo.edit import edit_repo
from neo.integrations.git.models import CloneLink, GitRepo

app = typer.Typer()
app.command("create")(create_repo)
app.command("edit")(edit_repo)
runner = CliRunner()


def _prepare(monkeypatch):
    for key, value in {
        "GIT_AUTHOR_NAME": "Neo Test",
        "GIT_AUTHOR_EMAIL": "neo@example.test",
        "GIT_COMMITTER_NAME": "Neo Test",
        "GIT_COMMITTER_EMAIL": "neo@example.test",
    }.items():
        monkeypatch.setenv(key, value)
    client = Mock()
    client.create_repository.return_value = GitRepo(
        name="demo",
        slug="demo",
        clone_links=[CloneLink(name="https", href="https://github.com/test/demo.git")],
    )
    monkeypatch.setattr(local_repo, "resolve_git_provider", lambda *a, **k: ("github", client))
    monkeypatch.setattr(
        local_repo, "resolve_git_workspace_and_source", lambda *a: ("test", "config")
    )
    monkeypatch.setattr(
        local_repo, "get_git_config_value", lambda *a: ("default-branch", "main", "default")
    )
    selected = Mock()
    monkeypatch.setattr(local_repo, "select_repo", selected)
    push = Mock()
    monkeypatch.setattr(local_repo, "_push_with_credential", push)
    return client, selected, push


def test_AC_4_create_local_and_private_remote(tmp_path: Path, monkeypatch):
    client, selected, push = _prepare(monkeypatch)
    target = tmp_path / "demo"
    result = runner.invoke(app, ["create", "demo", "--path", str(target)])
    assert result.exit_code == 0, result.output
    assert (target / "README.md").read_text() == "# demo\n"
    assert (target / "AGENTS.md").is_file()
    assert (target / ".git").is_dir()
    client.create_repository.assert_called_once_with(
        "demo", workspace="test", is_private=True, description=None
    )
    selected.assert_called_once_with(target)
    push.assert_called_once_with(target, "github", "https://github.com/test/demo.git")


def test_AC_4_remote_failure_preserves_local_and_public_option(tmp_path: Path, monkeypatch):
    client, _, _ = _prepare(monkeypatch)
    client.create_repository.side_effect = httpx.ConnectError("network unavailable")
    target = tmp_path / "demo"
    result = runner.invoke(app, ["create", "demo", "--path", str(target), "--public"])
    assert result.exit_code == 1
    assert (target / "README.md").is_file()
    assert (target / "AGENTS.md").is_file()
    assert "criação do repositório remoto" in result.output
    assert "não confirmado" in result.output
    assert client.create_repository.call_args.kwargs["is_private"] is False
    result = runner.invoke(app, ["create", "demo", "--path", str(target)])
    assert result.exit_code == 2


def test_AC_4_push_failure_reports_remote_created(tmp_path: Path, monkeypatch):
    _prepare(monkeypatch)
    monkeypatch.setattr(
        local_repo, "_push_with_credential", Mock(side_effect=RuntimeError("failed"))
    )
    target = tmp_path / "demo"
    result = runner.invoke(app, ["create", "demo", "--path", str(target)])
    assert result.exit_code == 1
    assert "envio da branch inicial" in result.output
    assert "remoto: criado" in result.output
    assert (target / ".git").is_dir()


def test_AC_4_push_uses_secret_askpass_without_credential_in_arguments(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(local_repo, "get_credential", lambda _: "person@example.test:private-token")

    def run_git(path, *args, env):
        assert path == tmp_path
        assert "private-token" not in str(args)
        assert "http.followRedirects=false" in args
        assert env["GIT_CONFIG_GLOBAL"] == os.devnull
        script = env["GIT_ASKPASS"]
        username = subprocess.run(
            [script, "Username:"], env=env, capture_output=True, text=True, check=True
        )
        password = subprocess.run(
            [script, "Password:"], env=env, capture_output=True, text=True, check=True
        )
        assert username.stdout.strip() == "person@example.test"
        assert password.stdout.strip() == "private-token"

    monkeypatch.setattr(local_repo, "_run_git", run_git)
    local_repo._push_with_credential(tmp_path, "bitbucket", "https://bitbucket.org/acme/demo.git")


def test_AC_5_edit_description(monkeypatch):
    client, _, _ = _prepare(monkeypatch)
    monkeypatch.setattr(local_repo, "detect_git_remote_details", lambda: ("github", "test", "demo"))
    result = runner.invoke(app, ["edit", "--description", "Nova descrição"])
    assert result.exit_code == 0, result.output
    client.update_repository_description.assert_called_once_with(
        "demo", "Nova descrição", workspace="test"
    )
