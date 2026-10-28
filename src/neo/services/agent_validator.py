"""Validação segura de executáveis de agentes de codificação."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any

from neo.config import ExitCode, validate_agent_adapter

SHELL_METACHARACTERS = frozenset({";", "|", "&", "$", "`", ">", "<", "\n", "\r", "(", ")"})


class AgentValidationError(Exception):
    """Exceção lançada quando o executável do agente é ausente, inválido ou incompatível."""

    exit_code: int = int(ExitCode.USAGE_ERROR)

    def __init__(
        self,
        message: str,
        *,
        suggestion: str | None = None,
        exit_code: int = int(ExitCode.USAGE_ERROR),
    ) -> None:
        final_msg = f"{message} Sugestão: {suggestion}" if suggestion else message
        super().__init__(final_msg)
        self.raw_message = message
        self.suggestion = suggestion
        self.exit_code = exit_code


def validate_executable_syntax(command: str) -> str:
    """Garante que o comando representa apenas o nome/caminho de um executável, sem shell arbitrário."""
    clean_cmd = command.strip()
    if not clean_cmd:
        raise AgentValidationError(
            "O comando do executável do agente não pode ser vazio.",
            suggestion="Informe o nome do executável (ex.: `neo config agent set command agy`).",
            exit_code=int(ExitCode.USAGE_ERROR),
        )

    if any(ch in clean_cmd for ch in SHELL_METACHARACTERS) or any(ch.isspace() for ch in clean_cmd):
        raise AgentValidationError(
            f"Comando inválido: '{command}'. Informe apenas o nome ou caminho do executável, "
            "sem argumentos extras ou operadores de shell.",
            suggestion="Use apenas o binário (ex.: `agy` ou `/usr/local/bin/agy`).",
            exit_code=int(ExitCode.USAGE_ERROR),
        )

    return clean_cmd


def validate_agent_executable(
    command: str,
    adapter: str = "antigravity",
    timeout: float = 3.0,
    not_found_exit_code: int = int(ExitCode.USAGE_ERROR),
) -> dict[str, Any]:
    """Verifica disponibilidade no PATH e compatibilidade do executável via `--version` (sem shell=True).

    Retorna um dicionário com `command`, `resolved_path`, `version` e `adapter`.
    """
    valid_adapter = validate_agent_adapter(adapter)
    clean_cmd = validate_executable_syntax(command)

    resolved_path = shutil.which(clean_cmd)
    if not resolved_path:
        raise AgentValidationError(
            f"O executável '{clean_cmd}' não foi encontrado no PATH do ambiente atual.",
            suggestion=(
                "Instale o Google Antigravity CLI (`agy`) conforme "
                "https://antigravity.google/product/antigravity-cli e garanta que o binário esteja no PATH."
            ),
            exit_code=not_found_exit_code,
        )

    try:
        completed = subprocess.run(
            [resolved_path, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise AgentValidationError(
            f"A verificação de versão de '{clean_cmd}' excedeu o tempo limite de {timeout:.1f}s.",
            suggestion=(
                "Verifique se o executável responde a `--version` sem aguardar entrada interativa."
            ),
            exit_code=int(ExitCode.USAGE_ERROR),
        ) from exc
    except OSError as exc:
        raise AgentValidationError(
            f"Não foi possível executar '{clean_cmd}' ({resolved_path}): {exc}.",
            suggestion="Verifique as permissões de execução (`chmod +x`) e a integridade do binário.",
            exit_code=int(ExitCode.USAGE_ERROR),
        ) from exc

    if completed.returncode != 0:
        stderr_snippet = (completed.stderr or completed.stdout or "").strip().splitlines()
        detail = f" ({stderr_snippet[0]})" if stderr_snippet else ""
        raise AgentValidationError(
            f"O executável '{clean_cmd}' retornou código {completed.returncode} ao consultar `--version`{detail}, "
            f"sendo incompatível com o adaptador '{valid_adapter}'.",
            suggestion="Confirme que o comando aponta para o binário oficial `agy` do Antigravity CLI.",
            exit_code=int(ExitCode.USAGE_ERROR),
        )

    raw_output = (completed.stdout or completed.stderr or "").strip()
    first_line = raw_output.splitlines()[0].strip() if raw_output else "ok"

    return {
        "adapter": valid_adapter,
        "command": clean_cmd,
        "resolved_path": resolved_path,
        "version": first_line,
    }
