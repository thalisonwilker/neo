"""Testes E2E para `neo agent setup` e preservação de artefatos SDD (feature 0015)."""

import json
import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


def test_AC_7_AC_11_AC_12_sdd_setup_idempotent_and_preserves_customizations(tmp_path: Path):
    """AC-7, AC-11 e AC-12 (0015): Prepara spec-driven e spec-kit de forma idempotente e sem apagar arquivos."""
    proj_dir = tmp_path / "repo-sdd"
    proj_dir.mkdir()

    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {}, clear=True),
    ):
        # 1. Setup inicial spec-driven
        res_sd = runner.invoke(
            app,
            [
                "agent",
                "setup",
                "--sdd-provider",
                "spec-driven",
                "--dir",
                str(proj_dir),
                "--yes",
                "--json",
            ],
        )
        assert res_sd.exit_code == 0
        data_sd = json.loads(res_sd.output)
        assert data_sd["provider"] == "spec-driven"
        assert "AGENTS.md" in data_sd["created_files"]
        assert (proj_dir / "AGENTS.md").exists()
        assert (proj_dir / ".agents" / "skills" / "nova-feature" / "SKILL.md").exists()

        # Personaliza AGENTS.md e garante que repetição do setup preserva a customização (AC-11)
        custom_text = "# Meu AGENTS.md Customizado\nRegra especial do time.\n"
        (proj_dir / "AGENTS.md").write_text(custom_text, encoding="utf-8")

        res_sd_repeat = runner.invoke(
            app,
            [
                "agent",
                "setup",
                "--sdd-provider",
                "spec-driven",
                "--dir",
                str(proj_dir),
                "--yes",
                "--json",
            ],
        )
        assert res_sd_repeat.exit_code == 0
        data_repeat = json.loads(res_sd_repeat.output)
        assert data_repeat["created_files"] == []
        assert "AGENTS.md" in data_repeat["preserved_files"]
        assert (proj_dir / "AGENTS.md").read_text(encoding="utf-8") == custom_text

        # 2. Trocar provedor configurado não migra nem apaga artefatos existentes (AC-12)
        res_switch = runner.invoke(app, ["config", "agent", "set", "sdd-provider", "spec-kit"])
        assert res_switch.exit_code == 0
        assert (proj_dir / "AGENTS.md").read_text(encoding="utf-8") == custom_text
        assert (proj_dir / ".agents" / "skills" / "nova-feature" / "SKILL.md").exists()

        # 3. Setup spec-kit cria skills speckit-* preservando AGENTS.md e nova-feature (AC-7, AC-11)
        res_sk = runner.invoke(
            app,
            [
                "agent",
                "setup",
                "--sdd-provider",
                "spec-kit",
                "--dir",
                str(proj_dir),
                "--yes",
                "--json",
            ],
        )
        assert res_sk.exit_code == 0
        data_sk = json.loads(res_sk.output)
        assert data_sk["provider"] == "spec-kit"
        assert (proj_dir / ".speckit" / "config.toml").exists()
        assert (proj_dir / ".agents" / "skills" / "speckit-specify" / "SKILL.md").exists()
        assert (proj_dir / "AGENTS.md").read_text(encoding="utf-8") == custom_text


def test_AC_9_sdd_setup_rejects_incompatible_agent(tmp_path: Path):
    """AC-9 (0015): Informa combinação incompatível antes de alterar arquivos."""
    proj_dir = tmp_path / "repo-vazio"
    proj_dir.mkdir()

    res = runner.invoke(
        app,
        [
            "agent",
            "setup",
            "--agent",
            "agente-nao-suportado",
            "--sdd-provider",
            "spec-driven",
            "--dir",
            str(proj_dir),
            "--yes",
        ],
    )
    assert res.exit_code == int(ExitCode.UNSUPPORTED)
    assert list(proj_dir.iterdir()) == []
