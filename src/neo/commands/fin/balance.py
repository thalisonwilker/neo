"""Ação financeira."""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.output import console, print_json


def fin_balance(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe o balanço financeiro consolidado de todas as contas."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    bal = service.get_balance_summary()
    if as_json:
        print_json(bal.to_dict())
    else:
        table = Table(
            title="Balanço Consolidado por Conta", show_header=True, header_style="bold cyan"
        )
        table.add_column("Slug")
        table.add_column("Nome")
        table.add_column("Tipo")
        table.add_column("Saldo Inicial", justify="right")
        table.add_column("Saldo Atual", justify="right")
        for a in bal.accounts:
            cor_saldo = "green" if a.current_balance >= 0 else "red"
            table.add_row(
                a.slug,
                a.name,
                a.account_type,
                f"R$ {a.initial_balance:.2f}",
                f"[{cor_saldo}]R$ {a.current_balance:.2f}[/{cor_saldo}]",
            )
        console.print(table)
        cor_patr = "green" if bal.total_current >= 0 else "red"
        totais_text = f"[bold]Total Inicial:[/bold] R$ {bal.total_initial:.2f}\n[bold]Total Receitas:[/bold] [green]+R$ {bal.total_income:.2f}[/green]\n[bold]Total Despesas:[/bold] [red]-R$ {bal.total_expense:.2f}[/red]\n[bold]Patrimônio Consolidado:[/bold] [{cor_patr}]R$ {bal.total_current:.2f}[/{cor_patr}]"
        console.print(
            Panel(totais_text, title="[bold cyan]Totais Gerais[/bold cyan]", border_style="cyan")
        )
