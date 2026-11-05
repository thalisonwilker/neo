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
    CategoryNotFoundError,
)


def shortcut_income(
    ctx: typer.Context,
    amount: float = Argument(..., help="Valor da receita (positivo)."),
    description: str = Argument(..., help="Descrição da receita."),
    account: str | None = Option(
        None, "--account", "-a", help="Slug da conta bancária (padrão: primeira conta)."
    ),
    category: str | None = Option(
        None,
        "--category",
        "-c",
        help="Slug da categoria de receita (padrão: 'salario' ou 'outros').",
    ),
    date_str: str | None = Option(
        None, "--date", "-d", help="Data no formato YYYY-MM-DD (padrão: hoje)."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Atalho rápido para registrar uma receita."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        tx = service.create_transaction(
            amount=amount,
            description=description,
            transaction_type="income",
            account_slug=account,
            category_slug=category,
            date_str=date_str,
        )
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    except (AccountNotFoundError, CategoryNotFoundError) as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    if as_json:
        print_json(tx.to_dict())
    else:
        print_success(
            f"Receita registrada: [green]+R$ {tx.amount:.2f}[/green] na conta '{tx.account_name}' ({tx.category_name} - {tx.description})."
        )
