import json
import os
from unittest.mock import patch

import httpx
import respx
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


def test_AC_6_commits_without_credentials():
    """AC-6: Erro amigável ao rodar comando de commits sem credenciais."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        res = runner.invoke(app, ["commits", "search", "--repo", "meu-repo"])
        assert res.exit_code == 1
        assert "Credenciais do Bitbucket não configuradas" in res.output


def test_commits_without_repo_and_no_git():
    """Erro quando nenhum repositório é passado e não há git origin local."""
    with (
        patch.dict(os.environ, {"BITBUCKET_TOKEN": "mock-token"}),
        patch("neo.commands.commits._infer_repo_slug_from_git", return_value=None),
    ):
        res = runner.invoke(app, ["commits", "search"])
        assert res.exit_code == 1
        assert "Repositório não informado" in res.output


@respx.mock
def test_AC_5_commits_search_human_and_json():
    """AC-5: Consulta de commits em formato Rich e JSON."""
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

    with patch.dict(os.environ, {"BITBUCKET_TOKEN": "mock-token"}):
        # Modo Humano
        res_human = runner.invoke(
            app,
            ["commits", "search", "--repo", "meu-repo", "--workspace", "my-workspace"],
        )
        assert res_human.exit_code == 0
        assert "abcdef1" in res_human.output
        assert "fix: resolve timeout na query" in res_human.output

        # Modo JSON
        res_json = runner.invoke(
            app,
            ["--json", "commits", "search", "--repo", "meu-repo", "--workspace", "my-workspace"],
        )
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert len(data) == 1
        assert data[0]["hash"] == "abcdef1234567890"
        assert "fix: resolve timeout na query" in data[0]["message"]
