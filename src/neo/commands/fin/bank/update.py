"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_success
from neo.services.finance import (
    AccountNotFoundError,
)


def bank_update(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da conta a editar."),
    name: str | None = Option(None, "--name", "-n", help="Novo nome de exibição da conta."),
    account_type: str | None = Option(None, "--type", "-t", help="Novo tipo da conta."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Atualiza metadados de uma conta existente."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        acc = service.update_account(slug=slug, name=name, account_type=account_type)
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    if as_json:
        print_json(acc.to_dict())
    else:
        print_success(
            f"Conta '{acc.slug}' atualizada com sucesso para '{acc.name}' ({acc.account_type})."
        )
