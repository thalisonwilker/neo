"""Testes E2E para comandos de commits (`neo git commits list|search|show`, features 0003 e 0014)."""

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


@pytest.fixture(autouse=True)
def isolate_git_remote(tmp_path: Path):
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=(None, None, None),
        ),
        patch("neo.commands.commits.detect_git_remote_info", return_value=(None, None)),
    ):
        yield


def test_AC_6_commits_without_credentials():
    """AC-6 e AC-8 (0014): Erro código 3 ao rodar comando de commits sem credenciais."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        res = runner.invoke(app, ["git", "commits", "list", "--repo", "meu-repo"])
        assert res.exit_code == int(ExitCode.AUTH_ERROR)
        assert "neo git auth login --provider bitbucket" in res.output


def test_AC_6_commits_without_repo_and_no_git():
    """AC-6 e AC-8 (0014): Erro código 4 quando nenhum repositório é passado fora de um repo Git."""
    with (
        patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True),
        patch("neo.commands.commits._infer_repo_slug_from_git", return_value=None),
    ):
        res = runner.invoke(app, ["git", "commits", "list"])
        assert res.exit_code == int(ExitCode.NOT_FOUND)
        assert "Repositório não informado" in res.output


@respx.mock
def test_AC_6_commits_list_search_and_show():
    """AC-6 (0014): `neo git commits list`, `search --query` e `show <sha>` (Rich e `--json`)."""
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace/meu-repo/commits").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "hash": "abcdef1234567890",
                        "message": "fix: resolve timeout na query\n\nDetalhes extras",
                        "date": "2026-10-27T14:30:00Z",
                        "author": {"raw": "Thalyson <thalyson@exemplo.com>"},
                    }
                ]
            },
        )
    )
    respx.get(
        "https://api.bitbucket.org/2.0/repositories/my-workspace/meu-repo/commit/abcdef1"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "hash": "abcdef1234567890",
                "message": "fix: resolve timeout na query\n\nDetalhes extras",
                "date": "2026-10-27T14:30:00Z",
                "author": {"raw": "Thalyson <thalyson@exemplo.com>"},
                "links": {
                    "html": {
                        "href": "https://bitbucket.org/my-workspace/meu-repo/commits/abcdef1234567890"
                    }
                },
            },
        )
    )

    with patch.dict(os.environ, {"NEO_BITBUCKET_TOKEN": "mock-token"}, clear=True):
        # 1. `commits list` (humano e --json)
        res_list = runner.invoke(
            app,
            ["git", "commits", "list", "--repo", "meu-repo", "--workspace", "my-workspace"],
        )
        assert res_list.exit_code == 0
        assert "abcdef1" in res_list.output
        assert "fix: resolve timeout na query" in res_list.output

        res_list_json = runner.invoke(
            app,
            [
                "git",
                "commits",
                "list",
                "--repo",
                "meu-repo",
                "--workspace",
                "my-workspace",
                "--json",
            ],
        )
        assert res_list_json.exit_code == 0
        data_list = json.loads(res_list_json.output)
        assert len(data_list) == 1
        assert data_list[0]["hash"] == "abcdef1234567890"

        # 2. `commits search` sem `--query` falha com código 2
        res_search_no_q = runner.invoke(
            app,
            ["git", "commits", "search", "--repo", "meu-repo", "--workspace", "my-workspace"],
        )
        assert res_search_no_q.exit_code == int(ExitCode.USAGE_ERROR)

        # 3. `commits search --query` filtra pela mensagem
        res_search = runner.invoke(
            app,
            [
                "git",
                "commits",
                "search",
                "--query",
                "timeout",
                "--repo",
                "meu-repo",
                "--workspace",
                "my-workspace",
            ],
        )
        assert res_search.exit_code == 0
        assert "abcdef1" in res_search.output

        # 4. `commits show <sha>` exibe detalhes completos
        res_show = runner.invoke(
            app,
            [
                "git",
                "commits",
                "show",
                "abcdef1",
                "--repo",
                "meu-repo",
                "--workspace",
                "my-workspace",
            ],
        )
        assert res_show.exit_code == 0
        assert "abcdef1234567890" in res_show.output
        assert "Detalhes extras" in res_show.output

        res_show_json = runner.invoke(
            app,
            [
                "git",
                "commits",
                "show",
                "abcdef1",
                "--repo",
                "meu-repo",
                "--workspace",
                "my-workspace",
                "--json",
            ],
        )
        assert res_show_json.exit_code == 0
        show_data = json.loads(res_show_json.output)
        assert show_data["hash"] == "abcdef1234567890"
        assert show_data["short_hash"] == "abcdef1"
