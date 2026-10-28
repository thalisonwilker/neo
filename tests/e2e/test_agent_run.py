"""Testes E2E para `neo agent run` (overrides, modelo, diretório e erros — feature 0015)."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode, get_agent_config_value, set_agent_config_value

runner = CliRunner()


def test_AC_5_AC_6_AC_8_agent_run_applies_overrides_without_mutating_config(tmp_path: Path):
    """AC-5, AC-6 e AC-8 (0015): Aplica overrides na execução, encaminha --model e preserva config.toml."""
    proj_dir = tmp_path / "workspace-projeto"
    proj_dir.mkdir()
    (proj_dir / "AGENTS.md").write_text("# Regras\n", encoding="utf-8")

    mock_ver = MagicMock(returncode=0, stdout="Antigravity CLI v2.0.1\n", stderr="")
    mock_proc = MagicMock()
    mock_proc.poll.return_value = 0
    mock_proc.wait.return_value = 0

    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {}, clear=True),
    ):
        set_agent_config_value("command", "agy", config_dir=tmp_path)
        set_agent_config_value("model", "Modelo Persistido", config_dir=tmp_path)
        set_agent_config_value("sdd-provider", "spec-driven", config_dir=tmp_path)

        with (
            patch("shutil.which", return_value="/opt/bin/agy-override"),
            patch("subprocess.run", return_value=mock_ver),
            patch("subprocess.Popen", return_value=mock_proc) as mock_popen,
        ):
            res = runner.invoke(
                app,
                [
                    "agent",
                    "run",
                    "--command",
                    "agy-override",
                    "--model",
                    "Gemini 3.8 Flash",
                    "--sdd-provider",
                    "spec-kit",
                    "--dir",
                    str(proj_dir),
                ],
            )
            assert res.exit_code == 0
            mock_popen.assert_called_once_with(
                ["/opt/bin/agy-override", "--model", "Gemini 3.8 Flash"],
                cwd=str(proj_dir.resolve()),
                shell=False,
            )

        # Verifica que as preferências persistidas em config.toml não foram alteradas pelos overrides (AC-5)
        assert get_agent_config_value("command", config_dir=tmp_path)[1] == "agy"
        assert get_agent_config_value("model", config_dir=tmp_path)[1] == "Modelo Persistido"
        assert get_agent_config_value("sdd-provider", config_dir=tmp_path)[1] == "spec-driven"


def test_AC_9_and_not_found_and_json_rejection_in_agent_run(tmp_path: Path):
    """AC-9 e casos de borda (0015): Rejeita --json em agent run, agente incompatível (5) e binário ausente (4)."""
    # 1. --json não é suportado em sessão interativa
    res_json = runner.invoke(app, ["--json", "agent", "run"])
    assert res_json.exit_code == int(ExitCode.USAGE_ERROR)
    assert "não suporta `--json`" in res_json.output

    # 2. Combinação incompatível retorna código 5 antes de iniciar processo
    res_unsup = runner.invoke(app, ["agent", "run", "--agent", "cursor-cli"])
    assert res_unsup.exit_code == int(ExitCode.UNSUPPORTED)

    # 3. Executável ausente no momento do run retorna código 4 (NOT_FOUND)
    with (
        patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path),
        patch.dict(os.environ, {}, clear=True),
        patch("shutil.which", return_value=None),
    ):
        res_missing = runner.invoke(app, ["agent", "run", "--dir", str(tmp_path)])
        assert res_missing.exit_code == int(ExitCode.NOT_FOUND)

