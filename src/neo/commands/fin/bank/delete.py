"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_success
from neo.services.finance import (
    AccountInUseError,
    AccountNotFoundError,
)


def bank_delete(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da conta a remover."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Remove uma conta bancária sem movimentações associadas."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        service.delete_account(slug=slug)
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except AccountInUseError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))
    if as_json:
        print_json({"status": "success", "message": f"Conta '{slug}' removida com sucesso."})
    else:
        print_success(f"Conta '{slug}' removida com sucesso.")
