"""Testes unitários para o adaptador do Antigravity CLI (feature 0015)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from neo.config import ExitCode
from neo.integrations.agents.antigravity import (
    AntigravityAdapter,
    UnsupportedAgentCombinationError,
)


def test_AC_6_build_run_args_forwards_model():
    """AC-6 (0015): Encaminha o modelo selecionado via opção oficial --model."""
    assert AntigravityAdapter.build_run_args("/usr/local/bin/agy", model=None) == [
        "/usr/local/bin/agy"
    ]
    assert AntigravityAdapter.build_run_args("/usr/local/bin/agy", model="Gemini 3.8 Flash") == [
        "/usr/local/bin/agy",
        "--model",
        "Gemini 3.8 Flash",
    ]


def test_AC_9_validate_compatibility_rejects_unsupported():
    """AC-9 (0015): Informa combinações incompatíveis com código de saída 5."""
    AntigravityAdapter.validate_compatibility("antigravity", "spec-driven")
    AntigravityAdapter.validate_compatibility("antigravity", "spec-kit")

    with pytest.raises(UnsupportedAgentCombinationError) as exc_agent:
        AntigravityAdapter.validate_compatibility("claude-code", "spec-driven")
    assert exc_agent.value.exit_code == int(ExitCode.UNSUPPORTED)

    with pytest.raises(UnsupportedAgentCombinationError) as exc_sdd:
        AntigravityAdapter.validate_compatibility("antigravity", "outro-sdd")
    assert exc_sdd.value.exit_code == int(ExitCode.UNSUPPORTED)


def test_AC_15_run_interactive_session_handles_sigint_without_orphans(tmp_path: Path):
    """AC-15 (0015): Cancela a execução repassando sinal e encerrando o subprocesso sem deixar órfãos."""
    mock_proc = MagicMock()
    mock_proc.poll.side_effect = [None, 0]
    mock_proc.wait.side_effect = [KeyboardInterrupt(), 0]

    with patch("subprocess.Popen", return_value=mock_proc) as mock_popen:
        rc = AntigravityAdapter.run_interactive_session(
            ["/usr/local/bin/agy", "--model", "Gemini 3.8 Flash"],
            cwd=tmp_path,
        )
        assert rc == 130
        mock_popen.assert_called_once_with(
            ["/usr/local/bin/agy", "--model", "Gemini 3.8 Flash"],
            cwd=str(tmp_path.resolve()),
            shell=False,
        )
        mock_proc.send_signal.assert_called_once()
