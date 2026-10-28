"""Testes unitários para validação de executável do agente (feature 0015)."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from neo.config import ExitCode
from neo.services.agent_validator import (
    AgentValidationError,
    validate_agent_executable,
    validate_executable_syntax,
)


def test_AC_1_and_AC_2_validate_executable_success():
    """AC-1 e AC-2 (0015): Executável presente no PATH e compatível com --version é validado com sucesso."""
    mock_completed = MagicMock(returncode=0, stdout="Antigravity CLI v2.0.1\n", stderr="")
    with (
        patch("shutil.which", return_value="/usr/local/bin/agy"),
        patch("subprocess.run", return_value=mock_completed) as mock_run,
    ):
        result = validate_agent_executable("agy", adapter="antigravity", timeout=3.0)
        assert result["command"] == "agy"
        assert result["resolved_path"] == "/usr/local/bin/agy"
        assert result["version"] == "Antigravity CLI v2.0.1"
        mock_run.assert_called_once_with(
            ["/usr/local/bin/agy", "--version"],
            capture_output=True,
            text=True,
            timeout=3.0,
            check=False,
            shell=False,
        )


def test_AC_2_validate_executable_rejects_shell_injection_and_spaces():
    """AC-2 (0015): Rejeita comandos vazios, com espaços ou metacaracteres de shell sem executar subprocesso."""
    with pytest.raises(AgentValidationError, match="não pode ser vazio"):
        validate_executable_syntax("   ")

    for unsafe in ("agy; rm -rf /", "agy --flag", "agy | cat", "agy && echo oi", "$(whoami)"):
        with pytest.raises(
            AgentValidationError, match="sem argumentos extras ou operadores de shell"
        ):
            validate_executable_syntax(unsafe)


def test_AC_2_validate_executable_missing_in_path():
    """AC-2 (0015): Executável ausente no PATH levanta AgentValidationError com sugestão."""
    with (
        patch("shutil.which", return_value=None),
        pytest.raises(AgentValidationError) as exc_info,
    ):
        validate_agent_executable("agy-inexistente")
    assert exc_info.value.exit_code == int(ExitCode.USAGE_ERROR)
    assert "não foi encontrado no PATH" in str(exc_info.value)
    assert "antigravity.google" in str(exc_info.value)


def test_AC_2_validate_executable_timeout_and_nonzero():
    """AC-2 (0015): Trata timeout e retorno diferente de zero na verificação de versão."""
    with (
        patch("shutil.which", return_value="/usr/local/bin/agy"),
        patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(
                cmd=["/usr/local/bin/agy", "--version"], timeout=3.0
            ),
        ),
        pytest.raises(AgentValidationError, match="excedeu o tempo limite"),
    ):
        validate_agent_executable("agy", timeout=3.0)

    mock_failed = MagicMock(returncode=1, stdout="", stderr="unknown option --version")
    with (
        patch("shutil.which", return_value="/usr/local/bin/agy"),
        patch("subprocess.run", return_value=mock_failed),
        pytest.raises(AgentValidationError, match="incompatível com o adaptador"),
    ):
        validate_agent_executable("agy")
