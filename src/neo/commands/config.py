"""Comandos de visão geral das configurações do Neo (`neo config`).

A configuração de credenciais fica em `neo git config` (Bitbucket/GitHub) e
`neo tasks config` (Shortcut).
"""

from __future__ import annotations

import typer

from neo.commands._credentials import is_json_mode
from neo.config import (
    DEFAULT_CONFIG_FILE,
    get_all_services_status,
    get_default_provider_config,
)
from neo.output import print_json, print_panel, print_table

config_app = typer.Typer(
    name="config",
    help="Visão geral das configurações do Neo (`neo git` e `neo tasks`).",
    no_args_is_help=True,
)


@config_app.command("show")
def config_show(ctx: typer.Context) -> None:
    """Exibe o status geral das configurações e credenciais do Neo."""
    as_json = is_json_mode(ctx)
    statuses = get_all_services_status()
    default_provider = get_default_provider_config() or "bitbucket"

    if as_json:
        print_json(
            {
                "config_file": str(DEFAULT_CONFIG_FILE),
                "default_provider": default_provider,
                "services": statuses,
            }
        )
    else:
        columns = ["Serviço", "Status", "Origem", "Token Mascarado"]
        rows: list[list[str]] = []
        for svc, info in statuses.items():
            status_str = (
                "[bold green]Configurado[/bold green]"
                if info["configured"]
                else "[dim]Não configurado[/dim]"
            )
            source_str = str(info["source"]) if info["source"] else "-"
            token_str = str(info["masked_token"]) if info["masked_token"] else "-"
            rows.append([svc, status_str, source_str, token_str])

        print_table("Status de Autenticação do Neo", columns, rows)
        print_panel(
            "Provedor Git Ativo",
            f"[bold]Provedor padrão:[/bold] [cyan]{default_provider}[/cyan]",
        )
