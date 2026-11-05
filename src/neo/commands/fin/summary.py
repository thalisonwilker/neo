"""Ação financeira."""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.output import console, print_json


def fin_summary(
    ctx: typer.Context,
    month: str | None = Option(
        None, "--month", "-m", help="Mês de apuração no formato YYYY-MM (padrão: mês atual)."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe o resumo consolidado de um mês com detalhamento de despesas por categoria."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    summary = service.get_monthly_summary(month=month)
    if as_json:
        print_json(summary.to_dict())
    else:
        cor_liq = "green" if summary.net_balance >= 0 else "red"
        resumo_text = f"[bold]Mês de Referência:[/bold] {summary.month}\n[bold]Receitas:[/bold] [green]+R$ {summary.total_income:.2f}[/green]\n[bold]Despesas:[/bold] [red]-R$ {summary.total_expense:.2f}[/red]\n[bold]Resultado Líquido:[/bold] [{cor_liq}]R$ {summary.net_balance:.2f}[/{cor_liq}]"
        console.print(
            Panel(
                resumo_text,
                title=f"[bold cyan]Resumo Mensal ({summary.month})[/bold cyan]",
                border_style="cyan",
            )
        )
        if summary.expenses_by_category:
            cat_table = Table(
                title="Despesas por Categoria", show_header=True, header_style="bold cyan"
            )
            cat_table.add_column("Categoria")
            cat_table.add_column("Total Gasto", justify="right")
            cat_table.add_column("Participação", justify="right")
            for c in summary.expenses_by_category:
                cat_table.add_row(
                    c.category_name, f"[red]R$ {c.total:.2f}[/red]", f"{c.percentage:.1f}%"
                )
            console.print(cat_table)
        else:
            console.print("[dim]Nenhuma despesa registrada para este mês.[/dim]")
