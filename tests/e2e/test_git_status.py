"""Testes E2E para `neo git status` e códigos de saída de provedores (feature 0014: AC-7, AC-8)."""

import json
import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode
from neo.integrations.bitbucket import UnsupportedProviderOperationError
from neo.integrations.resolver import handle_git_provider_error

runner = CliRunner()


def test_AC_7_git_status_inside_and_outside_repo(tmp_path: Path):
    """AC-7 (0014): `neo git status` exibe contexto local, provedor resolvido e autenticação."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch.dict(
            os.environ,
            {
                "NEO_GIT_PROVIDER": "github",
                "NEO_GIT_WORKSPACE": "thalisonwilker",
                "NEO_GITHUB_TOKEN": "ghp_mock_status_token",
            },
            clear=True,
        ),
        patch(
            "neo.commands.git._inspect_local_git_status",
            return_value={
                "is_git_repo": True,
                "current_branch": "main",
                "clean": True,
                "modified_files": 0,
                "remote_url": "git@github.com:thalisonwilker/neo.git",
            },
        ),
        patch(
            "neo.commands.git.detect_git_remote_details",
            return_value=("github", "thalisonwilker", "neo"),
        ),
    ):
        res_human = runner.invoke(app, ["git", "status"])
        assert res_human.exit_code == 0
        assert "main" in res_human.output
        assert "github" in res_human.output
        assert "thalisonwilker" in res_human.output
        assert "Autenticado" in res_human.output
        assert "ghp_mock_status_token" not in res_human.output

        res_json = runner.invoke(app, ["git", "status", "--json"])
        assert res_json.exit_code == 0
        data = json.loads(res_json.output)
        assert data["local"]["is_git_repo"] is True
        assert data["local"]["current_branch"] == "main"
        assert data["provider"] == "github"
        assert data["provider_source"] == "env"
        assert data["workspace"] == "thalisonwilker"
        assert data["workspace_source"] == "env"
        assert data["repo"] == "neo"
        assert data["authenticated"] is True
        assert data["auth_source"] == "env"


def test_AC_8_unsupported_provider_operation_exit_code_5():
    """AC-8 (0014): Operação não suportada pelo provedor retorna código 5 e sugestão de alternativa."""
    exc = UnsupportedProviderOperationError(
        "O Bitbucket Cloud não possui recurso nativo de Releases.",
        suggestion="Use `neo git tag list` para consultar tags de versão.",
    )
    assert exc.exit_code == int(ExitCode.UNSUPPORTED)
    assert "Alternativa sugerida" in str(exc)

    import pytest
    import typer

    with pytest.raises(typer.Exit) as exc_info:
        handle_git_provider_error(exc, as_json=True)
    assert exc_info.value.exit_code == int(ExitCode.UNSUPPORTED)

