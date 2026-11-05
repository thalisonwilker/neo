"""Ação de config."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    ExitCode,
    list_agent_config_values,
)
from neo.output import print_error, print_json, print_table


def agent_config_list(
    ctx: typer.Context,
    json_flag: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Lista todas as chaves da seção `[agent]` com seus valores e origens."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        values = list_agent_config_values()
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    if as_json:
        print_json(values)
    else:
        columns = ["Chave", "Valor", "Origem"]
        rows = [
            [k, str(info["value"]) if info["value"] else "(não definido)", str(info["source"])]
            for k, info in values.items()
        ]
        print_table("Configurações do Agente ([agent])", columns, rows)
