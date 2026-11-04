"""AC-3 (0023): branches locais do repositório selecionado."""

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from neo.commands.branch import branch_app


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=path, check=True, capture_output=True, text=True
    ).stdout.strip()


def test_AC_3_branch_lifecycle_and_safe_delete(tmp_path: Path) -> None:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "commit", "--allow-empty", "-m", "Initial")
    runner = CliRunner()
    with patch("neo.commands.branch.resolve_repo_path", return_value=tmp_path):
        assert runner.invoke(branch_app, ["create", "feature/test"]).exit_code == 0
        listing = runner.invoke(branch_app, ["list", "--json"])
        assert listing.exit_code == 0
        assert {x["name"]: x["active"] for x in json.loads(listing.output)} == {
            "main": True,
            "feature/test": False,
        }
        assert runner.invoke(branch_app, ["select", "feature/test"]).exit_code == 0
        assert git(tmp_path, "branch", "--show-current") == "feature/test"
        assert runner.invoke(branch_app, ["delete", "feature/test", "--yes"]).exit_code != 0
        assert runner.invoke(branch_app, ["select", "main"]).exit_code == 0
        assert runner.invoke(branch_app, ["delete", "feature/test"], input="n\n").exit_code != 0
        assert git(tmp_path, "show-ref", "--verify", "refs/heads/feature/test")
        assert runner.invoke(branch_app, ["delete", "feature/test", "--yes"]).exit_code == 0


def test_AC_3_unmerged_branch_not_forced(tmp_path: Path) -> None:
    git(tmp_path, "init", "-b", "main")
    git(tmp_path, "config", "user.name", "Test")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "commit", "--allow-empty", "-m", "Initial")
    git(tmp_path, "switch", "-c", "unmerged")
    git(tmp_path, "commit", "--allow-empty", "-m", "Extra")
    git(tmp_path, "switch", "main")
    with patch("neo.commands.branch.resolve_repo_path", return_value=tmp_path):
        result = CliRunner().invoke(branch_app, ["delete", "unmerged", "--yes"])
    assert result.exit_code != 0
    assert git(tmp_path, "show-ref", "--verify", "refs/heads/unmerged")
