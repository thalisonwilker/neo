"""Ação de config."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    ExitCode,
    get_agent_config_value,
)
from neo.output import print_error, print_json, print_panel


def agent_config_get(
    ctx: typer.Context,
    key: str = Argument(..., help="Chave a consultar (command, model, sdd-provider, adapter)."),
    json_flag: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Exibe o valor efetivo de uma chave de configuração do agente e sua origem."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        valid_key, val, source = get_agent_config_value(key)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    if as_json:
        print_json({"key": valid_key, "value": val, "source": source})
    else:
        display_val = f"[cyan]{val}[/cyan]" if val else "[dim](não definido)[/dim]"
        print_panel(
            f"Configuração do Agente: {valid_key}",
            f"[bold]Chave:[/bold] {valid_key}\n[bold]Valor:[/bold] {display_val}\n[bold]Origem:[/bold] {source}",
        )
