"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.output import console, print_json, print_table


def bank_list(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Lista todas as contas bancárias cadastradas e seus saldos atuais."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    accounts = service.list_accounts()
    if as_json:
        print_json([a.to_dict() for a in accounts])
    else:
        if not accounts:
            console.print(
                "[yellow]Nenhuma conta bancária cadastrada. Use 'neo fin bank create' para criar uma.[/yellow]"
            )
            return
        rows = [
            [
                a.slug,
                a.name,
                a.account_type,
                f"R$ {a.initial_balance:.2f}",
                f"R$ {a.current_balance:.2f}",
            ]
            for a in accounts
        ]
        print_table(
            "Contas Bancárias e Carteiras",
            ["Slug", "Nome", "Tipo", "Saldo Inicial", "Saldo Atual"],
            rows,
        )
