"""Testes E2E para o diagnóstico `neo agent status` (feature 0015)."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


def test_AC_10_agent_status_available_and_missing(tmp_path: Path):
    """AC-10 (0015): Diagnostica dependências presentes e ausentes com orientação de correção."""
    proj_dir = tmp_path / "meu-projeto"
    proj_dir.mkdir()

    # 1. Quando o binário está ausente e o projeto ainda não tem AGENTS.md
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {}, clear=True),
        patch("shutil.which", return_value=None),
    ):
        res_missing = runner.invoke(app, ["agent", "status", "--dir", str(proj_dir), "--json"])
        assert res_missing.exit_code == 0
        data_missing = json.loads(res_missing.output)
        assert data_missing["executable_available"] is False
        assert len(data_missing["issues"]) >= 2
        assert any("antigravity.google" in i["suggestion"] for i in data_missing["issues"])
        assert any("neo agent setup" in i["suggestion"] for i in data_missing["issues"])

        res_human = runner.invoke(app, ["agent", "status", "--dir", str(proj_dir)])
        assert res_human.exit_code == 0
        assert "Orientações de Correção" in res_human.output

    # 2. Quando o binário está disponível e o projeto possui AGENTS.md e skills
    (proj_dir / "AGENTS.md").write_text("# Regras\n", encoding="utf-8")
    skill_dir = proj_dir / ".agents" / "skills" / "nova-feature"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: nova-feature\ndescription: x\n---\n", encoding="utf-8"
    )

    mock_ok = MagicMock(returncode=0, stdout="Antigravity CLI v2.0.1\n", stderr="")
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {"NEO_AGENT_MODEL": "Gemini 3.8 Flash"}, clear=True),
        patch("shutil.which", return_value="/usr/local/bin/agy"),
        patch("subprocess.run", return_value=mock_ok),
    ):
        res_ready = runner.invoke(app, ["agent", "status", "--dir", str(proj_dir), "--json"])
        assert res_ready.exit_code == 0
        data_ready = json.loads(res_ready.output)
        assert data_ready["executable_available"] is True
        assert data_ready["version"] == "Antigravity CLI v2.0.1"
        assert data_ready["model"] == "Gemini 3.8 Flash"
        assert data_ready["project"]["ready"] is True
        assert "nova-feature" in data_ready["project"]["discovered_skills"]
        assert data_ready["issues"] == []
