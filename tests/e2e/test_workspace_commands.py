"""Testes E2E para os comandos de workspace (`neo git workspace list|select|show`, features 0005 e 0014)."""

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode, get_default_workspace_config, set_default_workspace_config

runner = CliRunner()

MOCK_WORKSPACES_PAYLOAD = {
    "values": [
        {
            "type": "workspace_access",
            "administrator": True,
            "workspace": {
                "name": "Acme Corp",
                "slug": "acme_corp",
                "uuid": "{uuid-1}",
            },
        },
        {
            "type": "workspace_access",
            "administrator": False,
            "workspace": {
                "name": "Personal Workspace",
                "slug": "personal_ws",
                "uuid": "{uuid-2}",
            },
        },
    ]
}


@pytest.fixture
def mock_bitbucket_auth(tmp_path: Path):
    with (
        patch("neo.integrations.resolver.get_credential", return_value="user:token"),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=(None, None, None),
        ),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
    ):
        yield tmp_path


def test_AC_4_workspace_without_credentials():
    """AC-4 e AC-8 (0014): Sem credenciais retorna código 3 (AUTH_ERROR) apontando `neo git auth login`."""
    with (
        patch("neo.integrations.resolver.get_credential", return_value=None),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
    ):
        result = runner.invoke(app, ["git", "workspace", "list"])
        assert result.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git auth login --provider bitbucket" in result.output


@respx.mock
def test_AC_4_workspace_list_human_and_json(mock_bitbucket_auth: Path):
    """AC-4 (0014): `neo git workspace list` em formato Rich e `--json`."""
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    res_human = runner.invoke(app, ["git", "workspace", "list"])
    assert res_human.exit_code == 0
    assert "Acme Corp" in res_human.output
    assert "acme_corp" in res_human.output
    assert "Personal Workspace" in res_human.output
    assert "Ativo" in res_human.output

    res_json = runner.invoke(app, ["git", "workspace", "list", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert len(data) == 2
    assert data[0]["slug"] == "acme_corp"
    assert data[0]["is_admin"] is True
    assert data[0]["is_active"] is True


@respx.mock
def test_AC_4_workspace_show(mock_bitbucket_auth: Path):
    """AC-4 (0014): `neo git workspace show` exibe detalhes e origem da resolução."""
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    # 1. Sem config (auto API)
    res = runner.invoke(app, ["git", "workspace", "show"])
    assert res.exit_code == 0
    assert "acme_corp" in res.output
    assert "Detectado automaticamente via API" in res.output

    res_json = runner.invoke(app, ["git", "workspace", "show", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert data["workspace"] == "acme_corp"
    assert data["source"] == "default"

    # 2. Com config salvo
    set_default_workspace_config("personal_ws", config_dir=mock_bitbucket_auth)

    res_cfg = runner.invoke(app, ["git", "workspace", "show"])
    assert res_cfg.exit_code == 0
    assert "personal_ws" in res_cfg.output
    assert "Configuração local" in res_cfg.output

    # 3. Workspace inexistente via --workspace retorna código 4 (NOT_FOUND)
    res_404 = runner.invoke(app, ["git", "workspace", "show", "--workspace", "inexistente"])
    assert res_404.exit_code == int(ExitCode.NOT_FOUND)


@respx.mock
def test_AC_4_workspace_select(mock_bitbucket_auth: Path):
    """AC-4 (0014): `neo git workspace select` via `--workspace` e interativo."""
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    # 1. Direto por --workspace
    res = runner.invoke(app, ["git", "workspace", "select", "--workspace", "personal_ws"])
    assert res.exit_code == 0
    assert "personal_ws" in res.output
    assert get_default_workspace_config(config_dir=mock_bitbucket_auth) == "personal_ws"

    # 2. Interativo pelo teclado
    res_inter = runner.invoke(app, ["git", "workspace", "select"], input="1\n")
    assert res_inter.exit_code == 0
    assert get_default_workspace_config(config_dir=mock_bitbucket_auth) == "acme_corp"

    # 3. Workspace inexistente retorna código 4 (NOT_FOUND)
    res_err = runner.invoke(app, ["git", "workspace", "select", "--workspace", "nao-existe"])
    assert res_err.exit_code == int(ExitCode.NOT_FOUND)

    # 4. Modo --json sem --workspace retorna código 2 (USAGE_ERROR)
    res_json_err = runner.invoke(app, ["git", "workspace", "select", "--json"])
    assert res_json_err.exit_code == int(ExitCode.USAGE_ERROR)


def test_AC_8_legacy_workspace_commands_fail_with_hint():
    """AC-8 (0014): `workspace current` e `workspace set` falham com código 2 apontando o novo comando."""
    res_curr = runner.invoke(app, ["git", "workspace", "current"])
    assert res_curr.exit_code == int(ExitCode.USAGE_ERROR)
    assert "neo git workspace show" in res_curr.output

    res_set = runner.invoke(app, ["git", "workspace", "set", "acme_corp"])
    assert res_set.exit_code == int(ExitCode.USAGE_ERROR)
    assert "neo git config set workspace" in res_set.output
