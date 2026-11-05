"""Ação de agent."""

from __future__ import annotations

from pathlib import Path

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.agent import _common as common
from neo.config import (
    ExitCode,
    validate_agent_adapter,
    validate_sdd_provider,
)
from neo.integrations.agents.antigravity import (
    AntigravityAdapter,
    UnsupportedAgentCombinationError,
)
from neo.output import print_error
from neo.services.agent_validator import AgentValidationError, validate_agent_executable


def agent_run(
    ctx: typer.Context,
    agent: str | None = Option(
        None,
        "--agent",
        help="Identidade do adaptador do agente apenas para esta execução (ex.: antigravity).",
    ),
    command: str | None = Option(
        None, "--command", help="Executável do agente apenas para esta execução (ex.: agy)."
    ),
    model: str | None = Option(
        None,
        "--model",
        help="Identificador do modelo encaminhado ao agente apenas para esta execução.",
    ),
    sdd_provider: str | None = Option(
        None,
        "--sdd-provider",
        help="Provedor SDD considerado apenas para esta execução (spec-driven ou spec-kit).",
    ),
    directory: str = Option(
        ".", "--dir", help="Diretório de trabalho onde a sessão do agente será iniciada."
    ),
) -> None:
    """Inicia uma sessão interativa do agente no diretório escolhido com overrides locais."""
    if is_json_mode(ctx):
        print_error(
            "O comando `neo agent run` inicia uma sessão interativa de terminal e não suporta `--json`.",
            as_json=True,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    try:
        runtime = common.resolve_agent_runtime(
            agent_arg=agent, command_arg=command, model_arg=model, sdd_provider_arg=sdd_provider
        )
    except ValueError as exc:
        print_error(str(exc), as_json=False, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    eff_adapter = runtime["adapter"]
    eff_command = runtime["command"]
    eff_model = runtime["model"]
    eff_sdd = runtime["sdd_provider"]
    try:
        AntigravityAdapter.validate_compatibility(eff_adapter, eff_sdd)
        validate_agent_adapter(eff_adapter)
        validate_sdd_provider(eff_sdd)
    except UnsupportedAgentCombinationError as exc:
        print_error(str(exc), as_json=False, code=exc.exit_code)
        raise typer.Exit(code=exc.exit_code) from exc
    except ValueError as exc:
        print_error(str(exc), as_json=False, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    target_dir = Path(directory).expanduser().resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        print_error(
            f"Diretório de trabalho não encontrado: '{directory}'.",
            as_json=False,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    try:
        check = validate_agent_executable(
            eff_command,
            adapter=eff_adapter,
            timeout=3.0,
            not_found_exit_code=int(ExitCode.NOT_FOUND),
        )
    except AgentValidationError as exc:
        print_error(str(exc), as_json=False, code=exc.exit_code)
        raise typer.Exit(code=exc.exit_code) from exc
    args = AntigravityAdapter.build_run_args(check["resolved_path"], model=eff_model)
    return_code = AntigravityAdapter.run_interactive_session(args, cwd=target_dir)
    if return_code != 0:
        raise typer.Exit(code=return_code)
