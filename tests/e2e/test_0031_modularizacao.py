"""Critérios executáveis da feature 0031."""

from pathlib import Path

from typer.testing import CliRunner

from neo.cli import app
from neo.commands.tasks import _common
from neo.integrations.git.api.bitbucket.client import BitbucketClient
from neo.integrations.git.api.github.client import GitHubClient
from neo.integrations.git.provider import GitProvider
from neo.services.tasks.api.shortcut.client import ShortcutClient
from neo.services.tasks.provider import TaskProvider

ROOT = Path(__file__).resolve().parents[2] / "src" / "neo"


def test_AC_1_commands_are_modular_and_cli_loads() -> None:
    paths = (
        "commands/git/config/set/provider.py",
        "commands/git/config/set/api_key.py",
        "commands/git/config/set/workspace.py",
        "commands/git/repo/list.py",
        "commands/git/branch/create.py",
        "commands/git/pr/open.py",
        "commands/tasks/check/add.py",
        "commands/tasks/comment/add.py",
        "commands/agent/status.py",
        "commands/fin/bank/create.py",
    )
    assert all((ROOT / path).is_file() for path in paths)
    assert CliRunner().invoke(app, ["--help"]).exit_code == 0


def test_AC_2_existing_cli_aliases_and_groups_are_available() -> None:
    runner = CliRunner()
    for args in (
        ("git", "repo", "get", "--help"),
        ("tasks", "check", "done", "--help"),
        ("fin", "bank", "add", "--help"),
    ):
        assert runner.invoke(app, list(args)).exit_code == 0


def test_AC_3_git_adapters_implement_common_contract() -> None:
    assert isinstance(GitHubClient("token"), GitProvider)
    assert isinstance(BitbucketClient("token"), GitProvider)


def test_AC_4_shortcut_implements_common_contract() -> None:
    assert isinstance(ShortcutClient("token"), TaskProvider)
    for path in (ROOT / "commands/tasks").rglob("*.py"):
        assert "services.tasks.api.shortcut" not in path.read_text()


def test_AC_5_missing_optional_capability_returns_error(monkeypatch) -> None:
    monkeypatch.setattr(_common, "_get_client", lambda service, as_json: object())
    result = CliRunner().invoke(app, ["tasks", "iterations"])
    assert result.exit_code != 0
    assert "não oferece a capacidade de iterações" in result.output
    assert "trello" not in CliRunner().invoke(app, ["tasks", "--help"]).output.lower()


def test_AC_6_contracts_do_not_depend_on_adapters() -> None:
    for path in (
        ROOT / "integrations/git/provider.py",
        ROOT / "integrations/git/models.py",
        ROOT / "services/tasks/provider.py",
        ROOT / "services/tasks/models.py",
    ):
        source = path.read_text()
        assert "integrations.git.api" not in source
        assert "services.tasks.api" not in source
