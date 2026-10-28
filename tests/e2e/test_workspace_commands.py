"""Testes E2E para os comandos de workspace do Bitbucket (`neo workspace`)."""

import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app

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
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
    ):
        yield tmp_path


def test_AC_6_workspace_without_credentials():
    with (
        patch("neo.integrations.resolver.get_credential", return_value=None),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
    ):
        result = runner.invoke(app, ["workspace", "list"])
        assert result.exit_code == 1
        assert "Credenciais do Bitbucket não configuradas" in result.output


@respx.mock
def test_AC_1_workspace_list_human_and_json(mock_bitbucket_auth: Path):
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    # Modo humano
    res_human = runner.invoke(app, ["workspace", "list"])
    assert res_human.exit_code == 0
    assert "Acme Corp" in res_human.output
    assert "acme_corp" in res_human.output
    assert "Personal Workspace" in res_human.output
    assert "Ativo" in res_human.output

    # Modo JSON
    res_json = runner.invoke(app, ["--json", "workspace", "list"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert len(data) == 2
    assert data[0]["slug"] == "acme_corp"
    assert data[0]["is_admin"] is True
    assert data[0]["is_active"] is True
    assert data[1]["slug"] == "personal_ws"
    assert data[1]["is_active"] is False


@respx.mock
def test_AC_2_workspace_current(mock_bitbucket_auth: Path):
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    # 1. Sem config (auto API)
    res = runner.invoke(app, ["workspace", "current"])
    assert res.exit_code == 0
    assert "acme_corp" in res.output
    assert "Detectado automaticamente via API" in res.output

    res_json = runner.invoke(app, ["--json", "workspace", "current"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert data["workspace"] == "acme_corp"
    assert data["source"] == "api_auto"

    # 2. Com config salvo
    from neo.config import set_default_workspace_config

    set_default_workspace_config("personal_ws", config_dir=mock_bitbucket_auth)

    res_cfg = runner.invoke(app, ["workspace", "current"])
    assert res_cfg.exit_code == 0
    assert "personal_ws" in res_cfg.output
    assert "Configuração local" in res_cfg.output


@respx.mock
def test_AC_3_workspace_select_by_slug(mock_bitbucket_auth: Path):
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    # Slug válido
    res = runner.invoke(app, ["workspace", "select", "--slug", "personal_ws"])
    assert res.exit_code == 0
    assert "Workspace ativo" in res.output and "personal_ws" in res.output

    from neo.config import get_default_workspace_config

    assert get_default_workspace_config(config_dir=mock_bitbucket_auth) == "personal_ws"

    # Atalho `neo workspace set`
    res_set = runner.invoke(app, ["workspace", "set", "acme_corp"])
    assert res_set.exit_code == 0
    assert get_default_workspace_config(config_dir=mock_bitbucket_auth) == "acme_corp"

    # Slug inexistente
    res_err = runner.invoke(app, ["workspace", "select", "--slug", "nao-existe"])
    assert res_err.exit_code == 1
    assert "Workspace 'nao-existe' não encontrado" in res_err.output


@respx.mock
def test_AC_4_workspace_select_interactive(mock_bitbucket_auth: Path):
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(200, json=MOCK_WORKSPACES_PAYLOAD)
    )

    # Seleção interativa digitando opção 2
    res = runner.invoke(app, ["workspace", "select"], input="2\n")
    assert res.exit_code == 0
    assert "personal_ws" in res.output

    from neo.config import get_default_workspace_config

    assert get_default_workspace_config(config_dir=mock_bitbucket_auth) == "personal_ws"

    # Modo JSON sem slug falha amigavelmente
    res_json_err = runner.invoke(app, ["--json", "workspace", "select"])
    assert res_json_err.exit_code == 1
    assert "--slug" in res_json_err.output


@respx.mock
def test_AC_5_workspace_precedence_in_repo_list(mock_bitbucket_auth: Path):
    from neo.config import set_default_workspace_config

    set_default_workspace_config("configured_ws", config_dir=mock_bitbucket_auth)

    respx.get("https://api.bitbucket.org/2.0/repositories/configured_ws").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Configured Repo",
                        "slug": "configured-repo",
                        "is_private": True,
                        "updated_on": "2026-10-27T10:00:00Z",
                    }
                ]
            },
        )
    )
    respx.get("https://api.bitbucket.org/2.0/repositories/explicit_ws").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Explicit Repo",
                        "slug": "explicit-repo",
                        "is_private": False,
                        "updated_on": "2026-10-27T10:00:00Z",
                    }
                ]
            },
        )
    )

    with patch("neo.integrations.resolver.get_credential", return_value="user:token"):
        # 1. Sem flag -> usa configured_ws
        res_default = runner.invoke(app, ["repo", "list"])
        assert res_default.exit_code == 0
        assert "Configured" in res_default.output

        # 2. Com flag -> tem precedência e usa explicit_ws
        res_flag = runner.invoke(app, ["repo", "list", "--workspace", "explicit_ws"])
        assert res_flag.exit_code == 0
        assert "Explicit" in res_flag.output
