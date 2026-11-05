"""Ação de configuração Git."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common
from neo.config import (
    SUPPORTED_GIT_CONFIG_KEYS,
    ExitCode,
    delete_credential,
    unset_git_config_value,
    validate_git_config_key,
)
from neo.git_context import (
    unset_repo,
    unset_task,
)
from neo.output import (
    print_error,
    print_success,
)


def git_config_unset(
    ctx: typer.Context,
    key: str = Argument(
        ..., help=f"Chave de configuração a remover ({', '.join(SUPPORTED_GIT_CONFIG_KEYS)})."
    ),
    yes: bool = Option(False, "--yes", help="Confirma a remoção da credencial armazenada."),
) -> None:
    """Remove uma chave personalizada da seção [git] do config.toml."""
    as_json = is_json_mode(ctx)
    normalized = key.strip().lower()
    if normalized in ("repo", "task", "branch"):
        if normalized == "branch":
            common._fail_usage(
                "A branch ativa é estado do Git e não pode ser removida; selecione outra branch.",
                as_json,
            )
        try:
            existed = unset_repo() if normalized == "repo" else unset_task()
        except (ValueError, OSError) as exc:
            common._fail_usage(str(exc), as_json)
        print_success(
            f"Configuração Git removida: {normalized}",
            as_json=as_json,
            json_payload={"status": "success", "key": normalized, "existed": existed},
        )
        return
    if key.strip().lower() == "api-key":
        provider = common._configured_provider(as_json)
        if not yes:
            if as_json:
                common._fail_usage(
                    "Use --yes para remover a credencial em modo JSON.", as_json=True
                )
            if not typer.confirm(f"Deseja remover a credencial salva de '{provider}'?"):
                print_error(
                    "Operação cancelada pelo usuário.", as_json=False, code=int(ExitCode.ERROR)
                )
                raise typer.Exit(code=int(ExitCode.ERROR))
        removed = delete_credential(provider)
        print_success(
            "Credencial armazenada removida."
            if removed
            else "Nenhuma credencial armazenada encontrada.",
            as_json=as_json,
            json_payload={"status": "success", "key": "api-key", "removed": removed},
        )
        return
    try:
        valid_key = validate_git_config_key(key)
    except ValueError as e:
        common._fail_usage(str(e), as_json=as_json)
    existed = unset_git_config_value(valid_key)
    print_success(
        f"Chave [bold]{valid_key}[/bold] removida de config.toml (restaurada para o padrão).",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "unset": True, "existed": existed},
    )
