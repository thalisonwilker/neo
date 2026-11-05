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
    TransactionNotFoundError,
)


def tx_update(
    ctx: typer.Context,
    tx_id: int = Argument(..., help="ID da transação a ser editada."),
    amount: float | None = Option(None, "--amount", help="Novo valor da transação."),
    desc: str | None = Option(None, "--desc", help="Nova descrição da transação."),
    account: str | None = Option(None, "--account", "-a", help="Novo slug de conta."),
    category: str | None = Option(None, "--category", "-c", help="Novo slug de categoria."),
    date_str: str | None = Option(None, "--date", "-d", help="Nova data no formato YYYY-MM-DD."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Edita uma transação existente recalculando os saldos."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        tx = service.update_transaction(
            tx_id=tx_id,
            amount=amount,
            description=desc,
            date_str=date_str,
            account_slug=account,
            category_slug=category,
        )
    except TransactionNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except (AccountNotFoundError, CategoryNotFoundError) as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    if as_json:
        print_json(tx.to_dict())
    else:
        print_success(
            f"Transação #{tx.id} atualizada com sucesso (R$ {tx.amount:.2f} - {tx.description})."
        )
