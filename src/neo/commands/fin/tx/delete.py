"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import console, print_error, print_json, print_success
from neo.services.finance import (
    TransactionNotFoundError,
)


def tx_delete(
    ctx: typer.Context,
    tx_id: int = Argument(..., help="ID da transação a ser removida."),
    yes: bool = Option(False, "--yes", "-y", help="Pula confirmação interativa."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exclui uma transação financeira existente."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        tx = service.get_transaction(tx_id)
    except TransactionNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    if not yes and (not as_json):
        confirm = typer.confirm(
            f"Deseja realmente remover a transação #{tx.id} ({tx.description} - R$ {tx.amount:.2f})?"
        )
        if not confirm:
            console.print("[yellow]Operação cancelada pelo usuário.[/yellow]")
            return
    service.delete_transaction(tx_id)
    if as_json:
        print_json({"status": "success", "message": f"Transação #{tx_id} removida com sucesso."})
    else:
        print_success(f"Transação #{tx_id} excluída com sucesso.")
