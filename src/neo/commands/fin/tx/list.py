"""Ação financeira."""

from __future__ import annotations

import typer
from rich.table import Table
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.output import console, print_json


def tx_list(
    ctx: typer.Context,
    month: str | None = Option(None, "--month", "-m", help="Filtrar por mês no formato YYYY-MM."),
    account: str | None = Option(None, "--account", "-a", help="Filtrar pelo slug da conta."),
    category: str | None = Option(None, "--category", "-c", help="Filtrar pelo slug da categoria."),
    transaction_type: str | None = Option(
        None, "--type", "-t", help="Filtrar por tipo: 'expense' ou 'income'."
    ),
    limit: int = Option(50, "--limit", "-l", help="Quantidade máxima de registros a exibir."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Lista transações financeiras com opções de filtros."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    txs = service.list_transactions(
        month=month,
        account_slug=account,
        category_slug=category,
        transaction_type=transaction_type,
        limit=limit,
    )
    if as_json:
        print_json([t.to_dict() for t in txs])
    else:
        if not txs:
            console.print(
                "[yellow]Nenhuma transação encontrada para os filtros especificados.[/yellow]"
            )
            return
        table = Table(title="Extrato de Transações", show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right")
        table.add_column("Data")
        table.add_column("Tipo")
        table.add_column("Valor", justify="right")
        table.add_column("Descrição")
        table.add_column("Conta")
        table.add_column("Categoria")
        for t in txs:
            if t.transaction_type == "expense":
                tipo_str = "[red]Despesa[/red]"
                val_str = f"[red]-R$ {t.amount:.2f}[/red]"
            else:
                tipo_str = "[green]Receita[/green]"
                val_str = f"[green]+R$ {t.amount:.2f}[/green]"
            table.add_row(
                str(t.id),
                t.date,
                tipo_str,
                val_str,
                t.description,
                t.account_name or "",
                t.category_name or "",
            )
        console.print(table)
