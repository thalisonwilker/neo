"""Aceite da apresentação das configurações Git (feature 0032)."""

import importlib
import json
import re
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

from neo.cli import app
from neo.commands.git.config._display import git_config_panel

show = importlib.import_module("neo.commands.git.config.show")
runner = CliRunner()


def values(provider=None, workspace=None, api_key=None, repo=None, task=None):
    return {
        key: {"value": value, "source": "config"}
        for key, value in {
            "provider": provider,
            "workspace": workspace,
            "default-branch": "develop",
            "branch-pattern": "{type}/{id}-{slug}",
            "commit-format": "{type}: {message}",
            "api-key": api_key,
            "repo": repo,
            "task": task,
            "branch": "active-branch",
        }.items()
    }


def render(data):
    output = StringIO()
    Console(
        file=output, force_terminal=True, color_system="standard", no_color=False, width=120
    ).print(git_config_panel(data))
    return output.getvalue()


def test_AC_1_fields_and_default_branch(monkeypatch):
    data = values("github", "team", "Configurado", "/tmp/project", "42")
    monkeypatch.setattr(show, "list_git_config_values", lambda: data.copy())
    monkeypatch.setattr(show.common, "_api_key_info", lambda: data["api-key"])
    monkeypatch.setattr(show, "selected_repo", lambda: Path("/tmp/project"))
    monkeypatch.setattr(show, "get_task", lambda: "42")
    monkeypatch.setattr(show, "current_branch", lambda: "active-branch")
    result = runner.invoke(app, ["git", "config", "show"])
    assert result.exit_code == 0
    assert "Git" in result.output
    labels = [
        "provider:",
        "workspace:",
        "branch:",
        "branch-pattern:",
        "commit-format:",
        "api-key:",
        "repo:",
        "task:",
    ]
    assert [result.output.index(label) for label in labels] == sorted(
        result.output.index(label) for label in labels
    )
    assert "develop" in result.output
    assert "active-branch" not in result.output
    assert "Origem" not in result.output
    assert "/tmp/project" not in result.output


@pytest.mark.parametrize("provider", ["github", "bitbucket"])
def test_AC_2_configured_fields_and_colors(provider):
    output = render(values(provider, "[team]", "Configurado", "/tmp/[project]", "##42"))
    for text in (f"{provider} (Configurado)", "[team]", "Configurado", "[project]", "#42"):
        assert re.search(r"\x1b\[32m" + re.escape(text) + r" *\x1b\[0m", output)
    assert "{type}/{id}-{slug}" in output
    assert "{type}: {message}" in output


def test_AC_2_unconfigured_fields_and_colors():
    output = render(values(task="42"))
    assert len(re.findall(r"\x1b\[37mNão configurado *\x1b\[0m", output)) == 4
    assert re.search(r"\x1b\[37mSem task definida *\x1b\[0m", output)


def test_AC_3_json_compatibility_and_secret(monkeypatch):
    data = values("github", "team", "Configurado", "/tmp/project", "42")
    monkeypatch.setattr(
        show,
        "list_git_config_values",
        lambda: {k: v for k, v in data.items() if k not in ("api-key", "repo", "task", "branch")},
    )
    monkeypatch.setattr(show.common, "_api_key_info", lambda: data["api-key"])
    monkeypatch.setattr(show, "selected_repo", lambda: Path("/tmp/project"))
    monkeypatch.setattr(show, "get_task", lambda: "42")
    monkeypatch.setattr(show, "current_branch", lambda: "active-branch")
    expected = data | {
        "repo": {"value": "/tmp/project", "source": "context"},
        "task": {"value": "42", "source": "context"},
        "branch": {"value": "active-branch", "source": "context"},
    }
    for args in (["git", "config", "show", "--json"], ["--json", "git", "config", "show"]):
        result = runner.invoke(app, args)
        assert result.exit_code == 0
        assert json.loads(result.output) == expected
        assert "secret-token" not in result.output
