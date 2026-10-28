"""Testes E2E para comandos com provedor GitHub (`neo git repo`, `neo git commits`, `neo git workspace`, features 0006 e 0014)."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


@pytest.fixture
def mock_github_env(tmp_path: Path):
    with (
        patch("neo.integrations.resolver.get_credential", return_value="ghp_mock_token"),
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=(None, None, None),
        ),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
    ):
        yield tmp_path


def test_AC_7_github_without_credentials():
    """Valida AC-7 (0006) e AC-8 (0014): Ausência de credenciais do GitHub retorna código 3."""
    with patch("neo.integrations.resolver.get_credential", return_value=None):
        res = runner.invoke(app, ["git", "repo", "list", "--provider", "github"])
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git auth login --provider github" in res.output


def test_AC_2_config_set_and_get_provider(tmp_path: Path):
    """AC-2 (0014): `neo git config set provider` e `neo git config get provider`."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch.dict(os.environ, {}, clear=True),
    ):
        res_set = runner.invoke(app, ["git", "config", "set", "provider", "github"])
        assert res_set.exit_code == 0
        assert "github" in res_set.output

        res_get = runner.invoke(app, ["git", "config", "get", "provider"])
        assert res_get.exit_code == 0
        assert "github" in res_get.output

        res_invalid = runner.invoke(app, ["git", "config", "set", "provider", "gitlab"])
        assert res_invalid.exit_code == int(ExitCode.USAGE_ERROR)
        assert "Provedor Git não suportado" in res_invalid.output


@respx.mock
def test_AC_5_repo_list_and_show_github(mock_github_env: Path):
    """AC-5 (0014): `neo git repo list` e `neo git repo show` no GitHub."""
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "octocat", "name": "The Octocat"})
    )
    respx.get("https://api.github.com/user/repos").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "octo-repo",
                    "private": True,
                    "description": "Repositório GitHub",
                    "default_branch": "main",
                    "updated_at": "2026-10-27T10:00:00Z",
                    "clone_url": "https://github.com/octocat/octo-repo.git",
                    "ssh_url": "git@github.com:octocat/octo-repo.git",
                    "owner": {"login": "octocat"},
                }
            ],
        )
    )
    respx.get("https://api.github.com/repos/octocat/octo-repo").mock(
        return_value=httpx.Response(
            200,
            json={
                "name": "octo-repo",
                "private": True,
                "description": "Repositório GitHub",
                "default_branch": "main",
                "updated_at": "2026-10-27T10:00:00Z",
                "clone_url": "https://github.com/octocat/octo-repo.git",
                "ssh_url": "git@github.com:octocat/octo-repo.git",
                "owner": {"login": "octocat"},
            },
        )
    )

    res_list = runner.invoke(app, ["git", "repo", "list", "--provider", "github"])
    assert res_list.exit_code == 0
    assert "octo-repo" in res_list.output
    assert "GitHub" in res_list.output

    res_show = runner.invoke(
        app,
        ["git", "repo", "show", "--repo", "octo-repo", "--provider", "github"],
    )
    assert res_show.exit_code == 0
    assert "octo-repo" in res_show.output
    assert "git@github.com:octocat/octo-repo.git" in res_show.output


@respx.mock
def test_AC_6_commits_search_and_show_github(mock_github_env: Path):
    """AC-6 (0014): `neo git commits search --query` e `neo git commits show <sha>` no GitHub."""
    respx.get("https://api.github.com/repos/octocat/octo-repo/commits").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "sha": "a1b2c3d4e5f6",
                    "commit": {
                        "message": "fix: bugfix no backend",
                        "author": {"name": "Dev", "date": "2026-10-27T12:00:00Z"},
                    },
                }
            ],
        )
    )
    respx.get("https://api.github.com/repos/octocat/octo-repo/commits/a1b2c3d").mock(
        return_value=httpx.Response(
            200,
            json={
                "sha": "a1b2c3d4e5f6",
                "html_url": "https://github.com/octocat/octo-repo/commit/a1b2c3d4e5f6",
                "commit": {
                    "message": "fix: bugfix no backend",
                    "author": {"name": "Dev", "date": "2026-10-27T12:00:00Z"},
                },
            },
        )
    )

    res = runner.invoke(
        app,
        [
            "git",
            "commits",
            "search",
            "--query",
            "bugfix",
            "--repo",
            "octo-repo",
            "--workspace",
            "octocat",
            "--provider",
            "github",
        ],
    )
    assert res.exit_code == 0
    assert "a1b2c3d" in res.output
    assert "fix: bugfix no backend" in res.output

    res_show = runner.invoke(
        app,
        [
            "git",
            "commits",
            "show",
            "a1b2c3d",
            "--repo",
            "octo-repo",
            "--workspace",
            "octocat",
            "--provider",
            "github",
        ],
    )
    assert res_show.exit_code == 0
    assert "a1b2c3d4e5f6" in res_show.output


@respx.mock
def test_AC_4_workspace_list_github(mock_github_env: Path):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json={"id": 1, "login": "octocat", "name": "The Octocat"})
    )
    respx.get("https://api.github.com/user/orgs").mock(
        return_value=httpx.Response(200, json=[{"id": 2, "login": "acme-corp"}])
    )

    res = runner.invoke(app, ["git", "workspace", "list", "--provider", "github"])
    assert res.exit_code == 0
    assert "octocat" in res.output
    assert "acme-corp" in res.output

    res_json = runner.invoke(app, ["git", "workspace", "list", "--provider", "github", "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert len(data) == 2
    assert data[0]["slug"] == "octocat"
    assert data[1]["slug"] == "acme-corp"
