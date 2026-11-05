"""Ação de config."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands._credentials import is_json_mode
from neo.config import (
    ExitCode,
    unset_agent_config_value,
    validate_agent_config_key,
)
from neo.output import print_error, print_success


def agent_config_unset(
    ctx: typer.Context,
    key: str = Argument(
        ..., help="Chave a remover da seção [agent] (command, model, sdd-provider, adapter)."
    ),
) -> None:
    """Remove uma chave personalizada da seção `[agent]` de `config.toml`."""
    as_json = is_json_mode(ctx)
    try:
        valid_key = validate_agent_config_key(key)
        existed = unset_agent_config_value(valid_key)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc
    msg = (
        f"Chave [bold]{valid_key}[/bold] removida da seção [agent] (restaurada para o padrão)."
        if existed
        else f"Chave [bold]{valid_key}[/bold] já estava com o valor padrão."
    )
    print_success(
        msg,
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "unset": True, "existed": existed},
    )
