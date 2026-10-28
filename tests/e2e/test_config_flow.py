"""Testes E2E para `neo config`, `neo git config`, `neo git auth` e `neo tasks config` (features 0002, 0009, 0014)."""

import json
import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


def test_AC_1_help_and_version():
    """AC-1 (0002, 0014): neo --help exibe descrição e comandos; neo --version exibe versão."""
    res_help = runner.invoke(app, ["--help"])
    assert res_help.exit_code == 0
    assert "Neo — Sua vida organizada, a um comando de distância." in res_help.output

    res_ver = runner.invoke(app, ["--version"])
    assert res_ver.exit_code == 0
    assert "0.2.0" in res_ver.output


def test_AC_1_no_short_flags_in_git_commands():
    """AC-1 (0014): Nenhum comando sob `neo git` aceita atalhos de uma letra (-p, -w, -r, -q, -l)."""
    for args in (
        ["git", "auth", "status", "-p", "github"],
        ["git", "workspace", "list", "-p", "github"],
        ["git", "repo", "list", "-w", "org"],
        ["git", "repo", "search", "-q", "termo"],
        ["git", "commits", "list", "-r", "repo"],
        ["git", "commits", "list", "-l", "5"],
    ):
        res = runner.invoke(app, args)
        assert res.exit_code == int(ExitCode.USAGE_ERROR), f"Esperado código 2 para {args}"


def test_AC_2_git_config_set_get_list_unset(tmp_path: Path):
    """AC-2 (0014): Gerenciamento de configuração `neo git config set|get|list|unset` e bloqueio de `token`."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch.dict(os.environ, {}, clear=True),
    ):
        # 1. Definir chaves válidas
        res_set = runner.invoke(app, ["git", "config", "set", "provider", "github"])
        assert res_set.exit_code == 0
        assert "provider" in res_set.output and "github" in res_set.output

        res_ws = runner.invoke(app, ["git", "config", "set", "workspace", "minha-org"])
        assert res_ws.exit_code == 0

        res_branch = runner.invoke(app, ["git", "config", "set", "default-branch", "develop"])
        assert res_branch.exit_code == 0

        # 2. Consultar com `get` (humano e --json)
        res_get = runner.invoke(app, ["git", "config", "get", "provider"])
        assert res_get.exit_code == 0
        assert "github" in res_get.output

        res_get_json = runner.invoke(app, ["git", "config", "get", "workspace", "--json"])
        assert res_get_json.exit_code == 0
        data_get = json.loads(res_get_json.output)
        assert data_get == {"key": "workspace", "value": "minha-org", "source": "config"}

        # 3. Listar todas as chaves (`list`)
        res_list = runner.invoke(app, ["git", "config", "list"])
        assert res_list.exit_code == 0
        assert "default-branch" in res_list.output
        assert "branch-pattern" in res_list.output
        assert "commit-format" in res_list.output

        res_list_json = runner.invoke(app, ["git", "config", "list", "--json"])
        assert res_list_json.exit_code == 0
        data_list = json.loads(res_list_json.output)
        assert data_list["provider"]["value"] == "github"
        assert data_list["default-branch"]["value"] == "develop"

        # 4. Remover chave (`unset`)
        res_unset = runner.invoke(app, ["git", "config", "unset", "default-branch"])
        assert res_unset.exit_code == 0
        res_after = runner.invoke(app, ["git", "config", "get", "default-branch", "--json"])
        assert json.loads(res_after.output)["value"] == "main"

        # 5. Bloqueio explícito da chave `token` (código 2)
        for subcmd in (
            ["git", "config", "set", "token", "segredo"],
            ["git", "config", "get", "token"],
            ["git", "config", "unset", "token"],
        ):
            res_tok = runner.invoke(app, subcmd)
            assert res_tok.exit_code == int(ExitCode.USAGE_ERROR)
            assert "neo git auth login" in res_tok.output


def test_AC_3_git_auth_login_status_logout(tmp_path: Path):
    """AC-3 e AC-6 (0014): `neo git auth login|status|logout` sem --token e sem expor segredos."""
    stored: dict[str, str] = {}

    def mock_set(service, username, password):
        stored[username] = password

    def mock_get(service, username):
        return stored.get(username)

    def mock_del(service, username):
        stored.pop(username, None)

    with (
        patch("keyring.set_password", side_effect=mock_set),
        patch("keyring.get_password", side_effect=mock_get),
        patch("keyring.delete_password", side_effect=mock_del),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CREDENTIALS_FILE", tmp_path / "credentials.toml"),
        patch.dict(os.environ, {}, clear=True),
    ):
        # 1. Login GitHub (prompt oculto)
        res_gh = runner.invoke(
            app,
            ["git", "auth", "login", "--provider", "github"],
            input="ghp_super_secret_token\n",
        )
        assert res_gh.exit_code == 0
        assert "GitHub" in res_gh.output
        assert "ghp_super_secret_token" not in res_gh.output

        # 2. Login Bitbucket Cloud (pede e-mail + API Token e avisa sobre App Passwords)
        res_bb = runner.invoke(
            app,
            ["git", "auth", "login", "--provider", "bitbucket"],
            input="dev@acme.com\nbb_api_token_secret\n",
        )
        assert res_bb.exit_code == 0
        assert "App Passwords" in res_bb.output
        assert "Bitbucket Cloud" in res_bb.output
        assert "bb_api_token_secret" not in res_bb.output

        # 3. `auth login` nunca aceita `--token`
        res_no_token_flag = runner.invoke(
            app, ["git", "auth", "login", "--provider", "github", "--token", "abc"]
        )
        assert res_no_token_flag.exit_code == int(ExitCode.USAGE_ERROR)

        # 4. `auth status` (humano e --json) nunca expõe o token
        res_status = runner.invoke(app, ["git", "auth", "status"])
        assert res_status.exit_code == 0
        assert "github" in res_status.output
        assert "bitbucket" in res_status.output
        assert "dev@acme.com" in res_status.output
        assert "ghp_super_secret_token" not in res_status.output
        assert "bb_api_token_secret" not in res_status.output

        res_status_json = runner.invoke(
            app, ["git", "auth", "status", "--provider", "bitbucket", "--json"]
        )
        assert res_status_json.exit_code == 0
        status_data = json.loads(res_status_json.output)
        assert status_data["provider"] == "bitbucket"
        assert status_data["authenticated"] is True
        assert status_data["source"] == "keyring"
        assert status_data["email"] == "dev@acme.com"
        assert "token" not in status_data
        assert "masked_token" not in status_data

        # 5. `auth logout` pede confirmação ou aceita `--yes`
        res_cancel = runner.invoke(
            app, ["git", "auth", "logout", "--provider", "github"], input="n\n"
        )
        assert res_cancel.exit_code == int(ExitCode.ERROR)
        assert "github" in stored

        res_logout = runner.invoke(app, ["git", "auth", "logout", "--provider", "github", "--yes"])
        assert res_logout.exit_code == 0
        assert "github" not in stored

        # Logout de provedor já desconectado retorna código 4 (NOT_FOUND)
        res_logout_again = runner.invoke(
            app, ["git", "auth", "logout", "--provider", "github", "--yes"]
        )
        assert res_logout_again.exit_code == int(ExitCode.NOT_FOUND)


def test_AC_4_and_AC_5_tasks_and_global_config_show():
    """AC-4 e AC-5 (0002/0009): `neo tasks config` e `neo config show` continuam funcionando."""
    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "token-sh-123456"}, clear=True):
        res = runner.invoke(app, ["--json", "tasks", "config", "get"])
        assert res.exit_code == 0
        data = json.loads(res.output)
        assert data["service"] == "shortcut"
        assert data["configured"] is True
        assert data["source"] == "env"
        assert "token-sh-123456" not in res.output

    res_show = runner.invoke(app, ["--json", "config", "show"])
    assert res_show.exit_code == 0
    show_data = json.loads(res_show.output)
    assert "services" in show_data
    assert "bitbucket" in show_data["services"]
    assert "shortcut" in show_data["services"]
    assert "git" in show_data
    assert "tasks" in show_data
    assert show_data["tasks"]["service"] == "shortcut"

    res_show_human = runner.invoke(app, ["config", "show"])
    assert res_show_human.exit_code == 0
    assert "Status de Git & Tasks" in res_show_human.output
    assert "Provedor de Git (git):" in res_show_human.output
    assert "Gerenciador de Tarefas (tasks):" in res_show_human.output
    assert "shortcut" in res_show_human.output


def test_AC_8_legacy_git_config_commands_fail_with_hint():
    """AC-8 (0014): Comandos antigos de config/auth falham com código 2 apontando o novo comando."""
    for legacy_cmd, expected_hint in (
        (["git", "config", "auth", "set", "github"], "neo git auth login"),
        (["git", "config", "set-provider", "github"], "neo git config set provider"),
        (["git", "config", "get-provider"], "neo git config get provider"),
    ):
        res = runner.invoke(app, legacy_cmd)
        assert res.exit_code == int(ExitCode.USAGE_ERROR)
        assert expected_hint in res.output
