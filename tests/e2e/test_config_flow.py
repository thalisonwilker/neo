"""Testes E2E para `neo config`, `neo git config`, `neo git config` e `neo tasks config` (features 0002, 0009, 0014)."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode
from neo.integrations.bitbucket_models import BitbucketWorkspace

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

        mock_client = Mock()
        mock_client.list_workspaces.return_value = [
            BitbucketWorkspace(uuid="1", name="Minha Org", slug="minha-org", is_admin=True)
        ]
        with patch("neo.commands.git.resolve_git_provider", return_value=("github", mock_client)):
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
            assert "neo git config set api-key" in res_tok.output


def test_AC_3_git_config_api_key_status_and_unset(tmp_path: Path):
    """AC-6 (0023): consulta e remoção de credenciais sem exposição de segredos."""
    from neo.config import set_credential

    stored: dict[str, str] = {}
    with (
        patch("keyring.set_password", lambda service, key, value: stored.__setitem__(key, value)),
        patch("keyring.get_password", lambda service, key: stored.get(key)),
        patch("keyring.delete_password", lambda service, key: stored.pop(key, None)),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CREDENTIALS_FILE", tmp_path / "credentials.toml"),
        patch.dict(os.environ, {}, clear=True),
    ):
        set_credential("github", "ghp_super_secret_token")
        set_credential("bitbucket", "bb_api_token_secret", email="dev@acme.com")
        assert runner.invoke(app, ["git", "config", "set", "provider", "github"]).exit_code == 0
        result = runner.invoke(app, ["git", "config", "get", "api-key", "--json"])
        assert result.exit_code == 0
        assert json.loads(result.output)["value"] == "Configurado"
        assert "ghp_super_secret_token" not in result.output
        assert runner.invoke(app, ["git", "config", "unset", "api-key"], input="n\n").exit_code != 0
        assert "github" in stored
        assert runner.invoke(app, ["git", "config", "unset", "api-key", "--yes"]).exit_code == 0
        assert "github" not in stored
        assert "bitbucket" in stored


def test_AC_4_and_AC_5_tasks_and_global_config_show():
    """AC-4 e AC-5 (0002/0009/0022): `neo tasks config` e `neo config show` em 4 blocos tabulares."""
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
        assert "git" in show_data
        assert "tasks" in show_data
        assert "agents" in show_data
        assert "services" in show_data
        assert show_data["tasks"]["provider"] == "shortcut"
        assert show_data["tasks"]["status"] == "Configurado"

        res_show_human = runner.invoke(app, ["config", "show"])
        assert res_show_human.exit_code == 0
        # 4 tabelas
        assert "Git" in res_show_human.output
        assert "Tasks" in res_show_human.output
        assert "Agents" in res_show_human.output
        assert "Serviços configurados" in res_show_human.output
        # Colunas esperadas
        assert "Provedor" in res_show_human.output
        assert "Workspace" in res_show_human.output
        assert "Branch" in res_show_human.output
        assert "To-Do-List" in res_show_human.output
        assert "Tarefa atual" in res_show_human.output
        assert "Code-Agent" in res_show_human.output
        assert "Code-Agent-Model" in res_show_human.output


def test_AC_8_legacy_git_config_commands_fail_with_hint():
    """AC-8 (0014): Comandos antigos de config/auth falham com código 2 apontando o novo comando."""
    for legacy_cmd, expected_hint in (
        (["git", "config", "auth", "set", "github"], "neo git config set api-key"),
        (["git", "config", "set-provider", "github"], "neo git config set provider"),
        (["git", "config", "get-provider"], "neo git config get provider"),
    ):
        res = runner.invoke(app, legacy_cmd)
        assert res.exit_code == int(ExitCode.USAGE_ERROR)
        assert expected_hint in res.output


@respx.mock
def test_feature_0022_config_show_tables_and_task_detection(tmp_path: Path):
    """Valida as 4 tabelas da feature 0022, detecção de task com checklist e ocultação de serviços desconectados."""
    respx.get("https://api.app.shortcut.com/api/v3/stories/2182").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 2182,
                "name": "Plano de Ataque",
                "story_type": "feature",
                "tasks": [
                    {"id": 1, "description": "Step 1", "complete": True},
                    {"id": 2, "description": "Step 2", "complete": False},
                ],
            },
        )
    )

    env_mock = {
        "SHORTCUT_API_TOKEN": "token-sc-xyz",
        "GITHUB_TOKEN": "",
        "BITBUCKET_TOKEN": "",
    }

    with (
        patch.dict(os.environ, env_mock, clear=True),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("keyring.get_password", return_value=None),
        patch(
            "neo.commands.config._inspect_local_git_status",
            return_value={
                "is_git_repo": True,
                "current_branch": "feature/2182-plano-de-ataque",
                "clean": True,
                "modified_files": 0,
            },
        ),
        patch(
            "neo.commands.config.get_task_columns_config",
            return_value={
                "todo": ["A Fazer", "Backlog"],
                "doing": ["Em Andamento"],
                "done": ["Concluído"],
            },
        ),
    ):
        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

        # Bloco Git com #2182
        assert "Ativo" in result.output
        assert "feature/2182-plano-de-ataque" in result.output
        assert "#2182" in result.output

        # Bloco Tasks com To-Do-List e Tarefa atual com checklist
        assert "A fazer:" in result.output
        assert "Fazendo:" in result.output
        assert "Feito:" in result.output
        assert "#2182" in result.output
        assert "Plano de" in result.output
        assert "1/2" in result.output

        # Bloco Serviços configurados só deve ter o shortcut configurado
        assert "shortcut" in result.output

        # Teste com --json
        res_json = runner.invoke(app, ["--json", "config", "show"])
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert data["git"]["tasks"] == "#2182"
        assert data["tasks"]["current_task"]["id"] == 2182
        assert data["tasks"]["current_task"]["checklist"] == {"completed": 1, "total": 2}
        assert len(data["services"]) == 1
        assert data["services"][0]["service"] == "shortcut"
