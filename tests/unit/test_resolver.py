"""Testes unitários para o resolvedor de provedores Git."""

from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from neo.integrations.bitbucket import BitbucketClient
from neo.integrations.github import GitHubClient
from neo.integrations.resolver import (
    detect_git_remote_info,
    resolve_git_provider,
)


def test_detect_git_remote_info_github():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "git@github.com:my-org/my-project.git\n"

        prov, slug = detect_git_remote_info()
        assert prov == "github"
        assert slug == "my-project"


def test_detect_git_remote_info_bitbucket():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "https://bitbucket.org/my-ws/api-service.git\n"

        prov, slug = detect_git_remote_info()
        assert prov == "bitbucket"
        assert slug == "api-service"


def test_detect_git_remote_info_unknown():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        prov, slug = detect_git_remote_info()
        assert prov is None
        assert slug is None


def test_resolve_git_provider_explicit_flag():
    with patch("neo.integrations.resolver.get_credential", return_value="mock-token"):
        prov, client = resolve_git_provider("github")
        assert prov == "github"
        assert isinstance(client, GitHubClient)

        prov2, client2 = resolve_git_provider("bitbucket")
        assert prov2 == "bitbucket"
        assert isinstance(client2, BitbucketClient)


def test_resolve_git_provider_invalid_flag():
    with pytest.raises(typer.Exit):
        resolve_git_provider("invalid-provider")


def test_resolve_git_provider_auto_detect():
    with (
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("github", "repo")),
        patch("neo.integrations.resolver.get_credential", return_value="mock-token"),
    ):
        prov, client = resolve_git_provider()
        assert prov == "github"
        assert isinstance(client, GitHubClient)


def test_resolve_git_provider_config_fallback(tmp_path: Path):
    with (
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=(None, None)),
        patch("neo.integrations.resolver.get_default_provider_config", return_value="github"),
        patch("neo.integrations.resolver.get_credential", return_value="mock-token"),
    ):
        prov, client = resolve_git_provider()
        assert prov == "github"
        assert isinstance(client, GitHubClient)


def test_resolve_git_provider_without_credentials():
    with (
        patch("neo.integrations.resolver.detect_git_remote_info", return_value=("github", "repo")),
        patch("neo.integrations.resolver.get_credential", return_value=None),
        pytest.raises(typer.Exit),
    ):
        resolve_git_provider()
