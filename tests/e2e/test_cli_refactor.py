"""Testes E2E da spec 0009 — refactor da CLI em `neo git` e `neo tasks`."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


@pytest.fixture
def isolated_config(tmp_path: Path):
    """Isola Keyring e config.toml para os testes."""
    stored: dict[str, str] = {}
    with (
        patch("keyring.set_password", lambda s, u, p: stored.__setitem__(u, p)),
        patch("keyring.get_password", lambda s, u: stored.get(u)),
        patch("keyring.delete_password", lambda s, u: stored.pop(u, None)),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch.dict("os.environ", {}, clear=False),
    ):
        yield stored


def test_AC_1_git_help_lists_subgroups():
    """0009 AC-1 / 0014 AC-1: `neo git --help` lista config, auth, workspace, repo, commits e status."""
    res = runner.invoke(app, ["git", "--help"])
    assert res.exit_code == 0
    for sub in ("config", "auth", "workspace", "repo", "commits", "status"):
        assert sub in res.output


def test_AC_2_git_auth_rejects_shortcut_with_hint():
    """0009 AC-2 / 0014 AC-3: `neo git auth login --provider shortcut` falha (código 2) e orienta `neo tasks config`."""
    res = runner.invoke(app, ["git", "auth", "login", "--provider", "shortcut"])
    assert res.exit_code == 2
    assert "neo tasks config" in " ".join(res.output.split())


def test_AC_3_tasks_invalid_service_lists_supported():
    """0009 AC-3: serviço inválido em `neo tasks` falha listando os suportados."""
    res = runner.invoke(app, ["tasks", "list", "--service", "jira"])
    assert res.exit_code == 1
    assert "jira" in res.output
    assert "shortcut" in res.output


def test_AC_3_tasks_default_service_requires_credentials(isolated_config):
    """0009 AC-3/AC-7: sem --service assume shortcut e orienta `neo tasks config set`."""
    with patch.dict("os.environ", {"SHORTCUT_API_TOKEN": "", "SHORTCUT_TOKEN": ""}):
        res = runner.invoke(app, ["tasks", "list"])
    assert res.exit_code == 1
    assert "neo tasks config set" in " ".join(res.output.split())


def test_AC_4_tasks_config_set_get_delete(isolated_config):
    """0009 AC-4: `neo tasks config set|get|delete` gerencia o token do Shortcut."""
    res_set = runner.invoke(app, ["tasks", "config", "set", "--token", "tok-shortcut-1234"])
    assert res_set.exit_code == 0
    assert isolated_config.get("shortcut") == "tok-shortcut-1234"

    res_get = runner.invoke(app, ["tasks", "config", "get", "-s", "shortcut"])
    assert res_get.exit_code == 0
    assert "Configurado" in res_get.output
    assert "tok-shortcut-1234" not in res_get.output

    res_del = runner.invoke(app, ["tasks", "config", "delete"])
    assert res_del.exit_code == 0
    assert "shortcut" not in isolated_config


def test_AC_4_tasks_config_set_json_requires_token():
    """0009 AC-4: em --json sem --token, `tasks config set` falha com código 1."""
    res = runner.invoke(app, ["--json", "tasks", "config", "set"])
    assert res.exit_code == 1
    assert "--token" in res.output


def test_AC_5_config_only_exposes_show():
    """0009 AC-5: `neo config` não expõe mais auth, set-provider nem get-provider."""
    res = runner.invoke(app, ["config", "--help"])
    assert res.exit_code == 0
    assert "show" in res.output
    for removed in ("auth", "set-provider", "get-provider"):
        assert removed not in res.output.replace("credenciais", "")
    for removed in ("auth", "set-provider", "get-provider"):
        assert runner.invoke(app, ["config", removed]).exit_code == 2


def test_AC_5_config_show_aggregates_all_services(isolated_config):
    """0009 AC-5: `neo config show` lista serviços git e tasks."""
    res = runner.invoke(app, ["--json", "config", "show"])
    assert res.exit_code == 0
    for svc in ("bitbucket", "github", "shortcut"):
        assert svc in res.output


@pytest.mark.parametrize("old", ["repo", "workspace", "commits", "story"])
def test_AC_6_old_commands_removed(old: str):
    """0009 AC-6: comandos antigos retornam 'No such command' (exit 2)."""
    res = runner.invoke(app, [old])
    assert res.exit_code == 2
    assert "No such command" in res.output


def test_AC_6_top_level_lists_only_config_git_tasks():
    """0009 AC-6: `neo --help` lista apenas config, git e tasks."""
    res = runner.invoke(app, ["--help"])
    assert res.exit_code == 0
    for removed in (" repo ", " workspace ", " commits ", " story "):
        assert removed not in res.output
    for present in ("config", "git", "tasks"):
        assert present in res.output
