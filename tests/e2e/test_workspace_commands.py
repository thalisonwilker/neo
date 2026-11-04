"""Testes E2E da configuração de workspace após remoção dos grupos Git."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


def test_AC_2_workspace_config_set_get_list_unset(tmp_path: Path):
    """Workspace permanece configurável, consultável e removível."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml"),
        patch.dict(os.environ, {}, clear=True),
    ):
        assert runner.invoke(app, ["git", "config", "set", "workspace", "acme"]).exit_code == 0
        result = runner.invoke(app, ["git", "config", "get", "workspace", "--json"])
        assert json.loads(result.output) == {
            "key": "workspace",
            "value": "acme",
            "source": "config",
        }
        result = runner.invoke(app, ["git", "config", "list", "--json"])
        assert json.loads(result.output)["workspace"]["value"] == "acme"
        assert runner.invoke(app, ["git", "config", "unset", "workspace"]).exit_code == 0
        result = runner.invoke(app, ["git", "config", "get", "workspace", "--json"])
        assert json.loads(result.output)["value"] is None


def test_workspace_environment_precedence(tmp_path: Path):
    """A variável de ambiente permanece prioritária sobre a configuração salva."""
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {"NEO_GIT_WORKSPACE": "environment"}, clear=True),
    ):
        assert runner.invoke(app, ["git", "config", "set", "workspace", "saved"]).exit_code == 0
        result = runner.invoke(app, ["git", "config", "get", "workspace", "--json"])
        assert json.loads(result.output) == {
            "key": "workspace",
            "value": "environment",
            "source": "env",
        }


@pytest.mark.parametrize("group", ["auth", "workspace"])
def test_AC_1_removed_git_groups_reject_invocation(group: str):
    assert runner.invoke(app, ["git", group]).exit_code == 2
