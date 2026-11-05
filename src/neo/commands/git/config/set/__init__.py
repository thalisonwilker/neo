"""Ação de configuração Git."""

from __future__ import annotations

from pathlib import Path

import typer
from typer import Argument

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common
from neo.commands.git.branch import select_branch
from neo.commands.git.config.set.api_key import _set_api_key
from neo.commands.git.config.set.provider import set_provider
from neo.commands.git.config.set.workspace import _set_workspace
from neo.config import SUPPORTED_GIT_CONFIG_KEYS, set_git_config_value
from neo.git_context import select_repo, set_task
from neo.output import print_success


def git_config_set(
    ctx: typer.Context,
    key: str = Argument(
        ..., help=f"Chave de configuração ({', '.join(SUPPORTED_GIT_CONFIG_KEYS)})."
    ),
    value: str | None = Argument(None, help="Valor a ser atribuído à chave (exceto api-key)."),
) -> None:
    """Define o valor de uma chave na seção [git] do config.toml."""
    as_json = is_json_mode(ctx)
    normalized = key.strip().lower()
    if normalized == "api-key":
        if value is not None:
            common._fail_usage(
                "Não informe a chave como argumento; ela será solicitada com entrada oculta.",
                as_json,
            )
        _set_api_key(as_json)
        return
    if normalized == "workspace":
        _set_workspace(value, as_json)
        return
    if value is None:
        common._fail_usage("Informe o valor da configuração.", as_json)
    if normalized == "provider":
        set_provider(key, value, as_json)
        return
    if normalized in ("repo", "task", "branch"):
        try:
            if normalized == "repo":
                value = str(select_repo(Path(value)))
            elif normalized == "task":
                set_task(value)
            else:
                select_branch(value)
        except (ValueError, OSError) as exc:
            common._fail_usage(str(exc), as_json)
        print_success(
            f"Configuração Git atualizada: {normalized} = {value}",
            as_json=as_json,
            json_payload={"status": "success", "key": normalized, "value": value},
        )
        return
    try:
        valid_key, clean_val = set_git_config_value(key, value)
    except ValueError as e:
        common._fail_usage(str(e), as_json=as_json)
    print_success(
        f"Configuração Git atualizada: [bold]{valid_key}[/bold] = [cyan]{clean_val}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "value": clean_val},
    )
