"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_success
from neo.services.finance import (
    DuplicateEntityError,
)


def bank_create(
    ctx: typer.Context,
    slug: str = Argument(..., help="Identificador único da conta (ex: nubank, inter, carteira)."),
    name: str = Option(..., "--name", "-n", help="Nome de exibição da conta."),
    account_type: str = Option(
        "checking",
        "--type",
        "-t",
        help="Tipo de conta (checking, savings, investment, credit, cash, other).",
    ),
    balance: float = Option(0.0, "--balance", "-b", help="Saldo inicial da conta (default: 0.0)."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Cadastra uma nova conta bancária ou carteira."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        acc = service.create_account(
            slug=slug, name=name, account_type=account_type, initial_balance=balance
        )
    except DuplicateEntityError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    if as_json:
        print_json(acc.to_dict())
    else:
        print_success(
            f"Conta '{acc.name}' ({acc.slug}) criada com saldo inicial de R$ {acc.initial_balance:.2f}."
        )
