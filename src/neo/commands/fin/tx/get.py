"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_panel
from neo.services.finance import (
    TransactionNotFoundError,
)


def tx_get(
    ctx: typer.Context,
    tx_id: int = Argument(..., help="ID numérico da transação."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe detalhes completos de uma transação específica."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        tx = service.get_transaction(tx_id)
    except TransactionNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    if as_json:
        print_json(tx.to_dict())
    else:
        tipo_lbl = (
            "[red]Despesa[/red]" if tx.transaction_type == "expense" else "[green]Receita[/green]"
        )
        val_str = (
            f"[red]-R$ {tx.amount:.2f}[/red]"
            if tx.transaction_type == "expense"
            else f"[green]+R$ {tx.amount:.2f}[/green]"
        )
        text = f"[bold]ID:[/bold] #{tx.id}\n[bold]Data:[/bold] {tx.date}\n[bold]Tipo:[/bold] {tipo_lbl}\n[bold]Valor:[/bold] {val_str}\n[bold]Descrição:[/bold] {tx.description}\n[bold]Conta:[/bold] {tx.account_name} ({tx.account_slug})\n[bold]Categoria:[/bold] {tx.category_name} ({tx.category_slug})\n[bold]Registrado em:[/bold] {tx.created_at}"
        print_panel(f"Transação #{tx.id}", text)
