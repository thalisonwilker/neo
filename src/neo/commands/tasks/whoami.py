"""Ação de tarefas."""

from __future__ import annotations

import typer

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel
from neo.services.tasks.errors import TaskProviderError


def tasks_whoami(ctx: typer.Context, service: str = common._service_option()) -> None:
    """Verifica e exibe o membro autenticado na API do Shortcut."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        member = client.get_current_member()
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json(member.model_dump())
    else:
        email = member.email_address or "-"
        print_panel(
            "Usuário Autenticado no Shortcut",
            f"[bold]Nome:[/bold] {member.name}\n[bold]Username:[/bold] @{member.mention_name}\n[bold]E-mail:[/bold] {email}\n[bold]ID:[/bold] {member.id}",
        )
