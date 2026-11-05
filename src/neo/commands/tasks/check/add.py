"""Ação de tarefas."""

from __future__ import annotations

import typer
from rich.markup import escape
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_success
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError


def check_add(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story/task pai no Shortcut."),
    description: str = Argument(..., help="Descrição do item de checklist."),
    service: str = common._service_option(),
) -> None:
    """Adiciona um item de checklist a uma story."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        task = client.create_task(story_id, description)
    except TaskProviderNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json(task.model_dump())
    else:
        print_success(
            f"Checklist item #{task.id} adicionado à story #{story_id}: [yellow][ ][/yellow] {escape(task.description)}"
        )
