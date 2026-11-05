"""Ação de config."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands._credentials import is_json_mode
from neo.config import (
    ExitCode,
    get_agent_config_value,
    set_agent_config_value,
    validate_agent_config_key,
)
from neo.output import print_error, print_success
from neo.services.agent_validator import AgentValidationError, validate_agent_executable


def agent_config_set(
    ctx: typer.Context,
    key: str = Argument(..., help="Chave de configuração (command, model, sdd-provider, adapter)."),
    value: str = Argument(..., help="Valor da chave de configuração."),
) -> None:
    """Define uma preferência do agente na seção `[agent]` de `config.toml`."""
    as_json = is_json_mode(ctx)
    try:
        valid_key = validate_agent_config_key(key)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    if valid_key == "command":
        _, current_adapter, _ = get_agent_config_value("adapter")
        try:
            check = validate_agent_executable(
                value,
                adapter=current_adapter or "antigravity",
                timeout=3.0,
                not_found_exit_code=int(ExitCode.USAGE_ERROR),
            )
        except (AgentValidationError, ValueError) as exc:
            code = getattr(exc, "exit_code", int(ExitCode.USAGE_ERROR))
            print_error(str(exc), as_json=as_json, code=code)
            raise typer.Exit(code=code) from exc
        try:
            saved_key, saved_val = set_agent_config_value(valid_key, value)
        except ValueError as exc:
            print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
            raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
        print_success(
            f"Configuração do agente atualizada: [bold]{saved_key}[/bold] = [cyan]{saved_val}[/cyan] (versão detectada: {check['version']})",
            as_json=as_json,
            json_payload={
                "status": "success",
                "key": saved_key,
                "value": saved_val,
                "resolved_path": check["resolved_path"],
                "version": check["version"],
            },
        )
        return
    try:
        saved_key, saved_val = set_agent_config_value(valid_key, value)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    print_success(
        f"Configuração do agente atualizada: [bold]{saved_key}[/bold] = [cyan]{saved_val}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "key": saved_key, "value": saved_val},
    )
