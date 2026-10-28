"""Testes unitários para o resolvedor de provedores Git (features 0006 e 0014)."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from neo.config import ExitCode
from neo.integrations.bitbucket import BitbucketClient
from neo.integrations.github import GitHubClient
from neo.integrations.resolver import (
    detect_git_remote_details,
    detect_git_remote_info,
    resolve_git_provider,
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)


def test_detect_git_remote_info_github():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "git@github.com:my-org/my-project.git\n"

        prov, ws, slug = detect_git_remote_details()
        assert prov == "github"
        assert ws == "my-org"
        assert slug == "my-project"
        assert detect_git_remote_info() == ("github", "my-project")


def test_detect_git_remote_info_bitbucket():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "https://bitbucket.org/my-ws/api-service.git\n"

        prov, ws, slug = detect_git_remote_details()
        assert prov == "bitbucket"
        assert ws == "my-ws"
        assert slug == "api-service"
        assert detect_git_remote_info() == ("bitbucket", "api-service")


def test_detect_git_remote_info_unknown():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        prov, slug = detect_git_remote_info()
        assert prov is None
        assert slug is None


def test_AC_2_resolve_git_provider_precedence():
    """AC-2 (0014): Precedência CLI > NEO_GIT_PROVIDER > [git] config.toml > remote > default."""
    with (
        patch.dict(os.environ, {"NEO_GIT_PROVIDER": "bitbucket"}, clear=True),
        patch("neo.integrations.resolver.get_default_provider_config", return_value="github"),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("github", "repo")),
    ):
        # 1. CLI ganha de todos
        assert resolve_git_provider_and_source("github") == ("github", "cli")
        # 2. ENV ganha de config e remote
        assert resolve_git_provider_and_source(None) == ("bitbucket", "env")

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.get_default_provider_config", return_value="github"),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("bitbucket", "r")),
    ):
        # 3. Config ganha de remote
        assert resolve_git_provider_and_source(None) == ("github", "config")

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.get_default_provider_config", return_value=None),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("github", "r")),
    ):
        # 4. Remote ganha de default
        assert resolve_git_provider_and_source(None) == ("github", "remote")


def test_AC_2_resolve_git_workspace_precedence():
    """AC-2 (0014): Precedência de workspace CLI > NEO_GIT_WORKSPACE > config > remote > default."""
    with (
        patch.dict(os.environ, {"NEO_GIT_WORKSPACE": "env-ws"}, clear=True),
        patch("neo.integrations.resolver.get_default_workspace_config", return_value="cfg-ws"),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=("github", "rem-ws", "repo"),
        ),
    ):
        assert resolve_git_workspace_and_source("github", "cli-ws") == ("cli-ws", "cli")
        assert resolve_git_workspace_and_source("github", None) == ("env-ws", "env")

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.get_default_workspace_config", return_value="cfg-ws"),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=("github", "rem-ws", "repo"),
        ),
    ):
        assert resolve_git_workspace_and_source("github", None) == ("cfg-ws", "config")

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.get_default_workspace_config", return_value=None),
        patch(
            "neo.integrations.resolver.detect_git_remote_details",
            return_value=("github", "rem-ws", "repo"),
        ),
    ):
        assert resolve_git_workspace_and_source("github", None) == ("rem-ws", "remote")


def test_resolve_git_provider_explicit_flag():
    with patch("neo.integrations.resolver.get_credential", return_value="mock-token"):
        prov, client = resolve_git_provider("github")
        assert prov == "github"
        assert isinstance(client, GitHubClient)

        prov2, client2 = resolve_git_provider("bitbucket")
        assert prov2 == "bitbucket"
        assert isinstance(client2, BitbucketClient)


def test_resolve_git_provider_invalid_flag():
    with pytest.raises(typer.Exit) as exc_info:
        resolve_git_provider("invalid-provider")
    assert exc_info.value.exit_code == int(ExitCode.USAGE_ERROR)


def test_resolve_git_provider_auto_detect():
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.get_default_provider_config", return_value=None),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("github", "repo")),
        patch("neo.integrations.resolver.get_credential", return_value="mock-token"),
    ):
        prov, client = resolve_git_provider()
        assert prov == "github"
        assert isinstance(client, GitHubClient)


def test_resolve_git_provider_config_fallback(tmp_path: Path):
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
        patch("neo.integrations.resolver.get_default_provider_config", return_value="github"),
        patch("neo.integrations.resolver.get_credential", return_value="mock-token"),
    ):
        prov, client = resolve_git_provider()
        assert prov == "github"
        assert isinstance(client, GitHubClient)


def test_resolve_git_provider_without_credentials():
    """AC-3 e AC-8 (0014): Falha sem credenciais encerra com código 3 (AUTH_ERROR)."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("neo.integrations.resolver.get_default_provider_config", return_value=None),
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("github", "repo")),
        patch("neo.integrations.resolver.get_credential", return_value=None),
        pytest.raises(typer.Exit) as exc_info,
    ):
        resolve_git_provider()
    assert exc_info.value.exit_code == int(ExitCode.AUTH_ERROR)
