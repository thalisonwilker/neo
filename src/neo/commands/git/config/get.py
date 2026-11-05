"""Ação de configuração Git."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common
from neo.commands.git.branch import current_branch
from neo.config import (
    SUPPORTED_GIT_CONFIG_KEYS,
    get_git_config_value,
)
from neo.git_context import (
    get_task,
    selected_repo,
)
from neo.output import (
    print_json,
    print_panel,
)


def git_config_get(
    ctx: typer.Context,
    key: str = Argument(
        ..., help=f"Chave de configuração ({', '.join(SUPPORTED_GIT_CONFIG_KEYS)})."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Exibe o valor atual e a origem de uma chave de configuração Git."""
    as_json = is_json_mode(ctx, json_output)
    if key.strip().lower() == "api-key":
        info = common._api_key_info()
        if as_json:
            print_json({"key": "api-key", **info})
        else:
            print_panel(
                "Configuração Git: api-key",
                f"Estado: {info['value'] or 'Não configurado'}\nOrigem: {info['source']}",
            )
        return
    normalized = key.strip().lower()
    if normalized in ("repo", "task", "branch"):
        try:
            if normalized == "repo":
                selected = selected_repo()
                val = str(selected) if selected else None
            elif normalized == "task":
                val = get_task()
            else:
                val = current_branch()
        except ValueError as exc:
            common._fail_usage(str(exc), as_json)
        if as_json:
            print_json({"key": normalized, "value": val, "source": "context"})
        else:
            print_panel(f"Configuração Git: {normalized}", f"Valor: {val or '-'}\nOrigem: context")
        return
    try:
        valid_key, val, source = get_git_config_value(key)
    except ValueError as e:
        common._fail_usage(str(e), as_json=as_json)
    if as_json:
        print_json({"key": valid_key, "value": val, "source": source})
    else:
        display_val = f"[cyan]{val}[/cyan]" if val is not None else "[dim]não definido[/dim]"
        print_panel(
            f"Configuração Git: {valid_key}",
            f"[bold]Chave:[/bold] {valid_key}\n[bold]Valor:[/bold] {display_val}\n[bold]Origem:[/bold] {source}",
        )
