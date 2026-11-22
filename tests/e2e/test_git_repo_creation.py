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


def _prepare(monkeypatch, tmp_path):
    for key, value in {
        "GIT_AUTHOR_NAME": "Neo Test",
        "GIT_AUTHOR_EMAIL": "neo@example.test",
        "GIT_COMMITTER_NAME": "Neo Test",
        "GIT_COMMITTER_EMAIL": "neo@example.test",
    }.items():
        monkeypatch.setenv(key, value)
    bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)
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
    client.get_repository.return_value = GitRepo(name="demo", slug="demo", main_branch="main")
    selected = Mock()
    monkeypatch.setattr(local_repo, "select_repo", selected)
    events = []
    client.validate_auth.side_effect = lambda: events.append("validate")

    def create(*args, **kwargs):
        events.append("create")
        return client.create_repository.return_value

    client.create_repository.side_effect = create

    def clone(parent, target, provider, remote_url):
        events.append("clone")
        subprocess.run(["git", "clone", str(bare), str(target)], check=True, capture_output=True)

    monkeypatch.setattr(local_repo, "_clone_with_credential", clone)

    def push(target, provider, remote_url):
        events.append("push")
        subprocess.run(
            ["git", "-C", str(target), "push", "-u", "origin", "HEAD"],
            check=True,
            capture_output=True,
        )

    monkeypatch.setattr(local_repo, "_push_with_credential", push)
    selected.side_effect = lambda target: events.append("select")
    return client, selected, events, bare


def test_AC_1_2_3_4_default_flow(tmp_path: Path, monkeypatch):
    client, selected, events, bare = _prepare(monkeypatch, tmp_path)
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["create", "demo"])
    target = tmp_path / "demo"
    assert result.exit_code == 0, result.output
    assert events == ["validate", "create", "clone", "push", "select"]
    assert (target / "README.md").read_text() == "# demo\n"
    assert (target / "AGENTS.md").read_text() == ""
    assert (
        subprocess.check_output(
            ["git", "-C", str(target), "branch", "--show-current"], text=True
        ).strip()
        == "main"
    )
    assert (
        subprocess.check_output(
            ["git", "-C", str(bare), "log", "main", "-1", "--format=%s"], text=True
        ).strip()
        == "first commit"
    )
    client.create_repository.assert_called_once_with(
        "demo", workspace="test", is_private=True, description=None
    )
    selected.assert_called_once_with(target)
    assert "cd " in result.output


def test_AC_1_2_3_4_options(tmp_path: Path, monkeypatch):
    client, _, _, bare = _prepare(monkeypatch, tmp_path)
    parent = tmp_path / "my projects"
    parent.mkdir()
    result = runner.invoke(
        app,
        [
            "create",
            "demo",
            "--path",
            str(parent),
            "--public",
            "--description",
            "Hello",
            "--default-branch",
            "develop",
        ],
    )
    assert result.exit_code == 0, result.output
    assert (parent / "demo" / "README.md").read_text() == "# demo\n\nHello\n"
    assert (
        subprocess.check_output(
            ["git", "-C", str(bare), "log", "develop", "-1", "--format=%s"], text=True
        ).strip()
        == "first commit"
    )
    assert client.create_repository.call_args.kwargs == {
        "workspace": "test",
        "is_private": False,
        "description": "Hello",
    }
    client.set_default_branch.assert_called_once_with("demo", "develop", workspace="test")
    assert "'" in result.output


def test_AC_5_validation_failure_before_remote(tmp_path: Path, monkeypatch):
    client, selected, _, _ = _prepare(monkeypatch, tmp_path)
    client.validate_auth.side_effect = httpx.ConnectError("secret")
    result = runner.invoke(app, ["create", "demo", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "validação da conexão" in result.output and "secret" not in result.output
    client.create_repository.assert_not_called()
    selected.assert_not_called()


def test_AC_5_existing_destination_and_invalid_branch(tmp_path: Path, monkeypatch):
    client, _, _, _ = _prepare(monkeypatch, tmp_path)
    (tmp_path / "demo").mkdir()
    assert runner.invoke(app, ["create", "demo", "--path", str(tmp_path)]).exit_code == 2
    assert (
        runner.invoke(
            app, ["create", "other", "--path", str(tmp_path), "--default-branch", "bad branch"]
        ).exit_code
        == 2
    )
    client.create_repository.assert_not_called()


def test_AC_5_push_failure_preserves_clone(tmp_path: Path, monkeypatch):
    _, selected, _, _ = _prepare(monkeypatch, tmp_path)
    monkeypatch.setattr(
        local_repo, "_push_with_credential", Mock(side_effect=RuntimeError("secret"))
    )
    result = runner.invoke(app, ["create", "demo", "--path", str(tmp_path)])
    assert result.exit_code == 1
    assert "push da branch inicial" in result.output and "remoto: criado" in result.output
    assert "secret" not in result.output
    assert (tmp_path / "demo" / ".git").is_dir()
    selected.assert_not_called()


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


def test_AC_5_edit_description(monkeypatch, tmp_path):
    client, _, _, _ = _prepare(monkeypatch, tmp_path)
    monkeypatch.setattr(local_repo, "detect_git_remote_details", lambda: ("github", "test", "demo"))
    result = runner.invoke(app, ["edit", "--description", "Nova descrição"])
    assert result.exit_code == 0, result.output
    client.update_repository_description.assert_called_once_with(
        "demo", "Nova descrição", workspace="test"
    )


def test_bitbucket_token_uses_documented_git_username(tmp_path, monkeypatch):
    monkeypatch.setattr(local_repo, "get_credential", lambda _: "private-token")

    def run_git(path, *args, env):
        assert env["NEO_PUSH_USERNAME"] == "x-bitbucket-api-token-auth"
        assert env["NEO_PUSH_PASSWORD"] == "private-token"
        assert "private-token" not in str(args)

    monkeypatch.setattr(local_repo, "_run_git", run_git)
    local_repo._clone_with_credential(
        tmp_path, tmp_path / "demo", "bitbucket", "https://bitbucket.org/acme/demo.git"
    )
