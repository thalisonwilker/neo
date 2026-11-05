"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_panel
from neo.services.finance import (
    AccountNotFoundError,
)


def bank_get(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da conta bancária."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe detalhes de uma conta bancária específica."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        acc = service.get_account(slug)
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    if as_json:
        print_json(acc.to_dict())
    else:
        cor_saldo = "green" if acc.current_balance >= 0 else "red"
        text = f"[bold]Slug:[/bold] {acc.slug}\n[bold]Nome:[/bold] {acc.name}\n[bold]Tipo:[/bold] {acc.account_type}\n[bold]Saldo Inicial:[/bold] R$ {acc.initial_balance:.2f}\n[bold]Saldo Atual:[/bold] [{cor_saldo}]R$ {acc.current_balance:.2f}[/{cor_saldo}]\n[bold]Criado em:[/bold] {acc.created_at}"
        print_panel(f"Conta: {acc.name}", text)
