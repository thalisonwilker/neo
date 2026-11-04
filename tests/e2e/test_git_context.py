"""Aceite de contexto Git persistente (spec 0023)."""

import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from neo import config
from neo.cli import app

runner = CliRunner()


def init_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    (path / "README.md").write_text("test\n")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", "initial"], check=True)


@pytest.fixture
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(config, "DEFAULT_CONFIG_DIR", tmp_path / "config")
    return tmp_path


def test_AC_1_select_and_list_local_repos(isolated: Path) -> None:
    repo = isolated / "project"
    init_repo(repo)
    assert runner.invoke(app, ["git", "repo", "select", str(repo)]).exit_code == 0
    result = runner.invoke(app, ["--json", "git", "repo", "list"])
    assert json.loads(result.output) == [{"path": str(repo), "selected": True, "task": None}]
    assert runner.invoke(app, ["git", "repo", "select", str(isolated / "missing")]).exit_code != 0
    assert json.loads(runner.invoke(app, ["--json", "git", "config", "get", "repo"]).output)[
        "value"
    ] == str(repo)


def test_AC_2_task_is_per_repo(isolated: Path) -> None:
    one, two = isolated / "one", isolated / "two"
    init_repo(one)
    init_repo(two)
    for repo, task in [(one, "123"), (two, "456")]:
        assert runner.invoke(app, ["git", "repo", "select", str(repo)]).exit_code == 0
        assert runner.invoke(app, ["git", "config", "set", "task", task]).exit_code == 0
    runner.invoke(app, ["git", "repo", "select", str(one)])
    assert (
        json.loads(runner.invoke(app, ["--json", "git", "config", "get", "task"]).output)["value"]
        == "123"
    )
    assert runner.invoke(app, ["git", "config", "unset", "task"]).exit_code == 0
    runner.invoke(app, ["git", "repo", "select", str(two)])
    assert (
        json.loads(runner.invoke(app, ["--json", "git", "config", "get", "task"]).output)["value"]
        == "456"
    )


def test_AC_7_selected_repo_and_branch_config(isolated: Path) -> None:
    repo = isolated / "project"
    init_repo(repo)
    assert runner.invoke(app, ["git", "config", "set", "repo", str(repo)]).exit_code == 0
    assert runner.invoke(app, ["git", "branch", "create", "example"]).exit_code == 0
    assert runner.invoke(app, ["git", "config", "set", "branch", "example"]).exit_code == 0
    result = runner.invoke(app, ["--json", "git", "config", "list"])
    assert json.loads(result.output)["branch"]["value"] == "example"
    assert runner.invoke(app, ["git", "config", "unset", "branch"]).exit_code != 0
    assert runner.invoke(app, ["git", "config", "unset", "repo"]).exit_code == 0
    assert repo.exists()


def test_AC_7_status_and_remote_use_selected_repo_without_exposing_credentials(
    isolated: Path,
) -> None:
    repo = isolated / "project"
    init_repo(repo)
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "remote",
            "add",
            "origin",
            "https://user:secret@github.com/team/project.git?token=secret",
        ],
        check=True,
    )
    assert runner.invoke(app, ["git", "repo", "select", str(repo)]).exit_code == 0
    assert runner.invoke(app, ["git", "config", "set", "task", "42"]).exit_code == 0
    result = runner.invoke(app, ["--json", "git", "status"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["selected_repo"] == str(repo)
    assert data["task"] == "42"
    assert data["repo"] == "project"
    assert "secret" not in result.output
