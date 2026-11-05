"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_success
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError


def check_complete(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story/task pai no Shortcut."),
    task_id: int = Argument(..., help="ID do item de checklist a concluir."),
    service: str = common._service_option(),
) -> None:
    """Marca um item de checklist como concluído."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        task = client.update_task(story_id, task_id, complete=True)
    except TaskProviderNotFoundError as e:
        print_error(f"Recurso não encontrado: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json(task.model_dump())
    else:
        print_success(
            f"Checklist item #{task.id} marcado como [green][✓] Concluído[/green] na story #{story_id}."
        )
