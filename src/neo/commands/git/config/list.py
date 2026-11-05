"""Ação de configuração Git."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common
from neo.commands.git.branch import current_branch
from neo.config import (
    list_git_config_values,
)
from neo.git_context import (
    get_task,
    selected_repo,
)
from neo.output import (
    print_json,
    print_table,
)


def git_config_list(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Lista todas as chaves da seção [git] com seus valores e origens."""
    as_json = is_json_mode(ctx, json_output)
    values = list_git_config_values()
    values["api-key"] = common._api_key_info()
    try:
        selected = selected_repo()
        values["repo"] = {"value": str(selected) if selected else None, "source": "context"}
        values["task"] = {"value": get_task(), "source": "context"}
        values["branch"] = {"value": current_branch(), "source": "context"}
    except ValueError:
        values.setdefault("repo", {"value": None, "source": "context"})
        values["task"] = {"value": None, "source": "context"}
        values["branch"] = {"value": None, "source": "context"}
    if as_json:
        print_json(values)
    else:
        columns = ["Chave", "Valor", "Origem"]
        rows: list[list[str]] = []
        for k, info in values.items():
            val = info["value"]
            val_str = f"[cyan]{val}[/cyan]" if val is not None else "[dim]-[/dim]"
            rows.append([k, val_str, str(info["source"] or "default")])
        print_table("Configurações Git ([git])", columns, rows)
