"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel
from neo.services.tasks.errors import TaskProviderError


def tasks_create(
    ctx: typer.Context,
    title: str = Argument(..., help="Título / nome da nova task (story)."),
    description: str | None = Option(
        None, "-d", "--description", help="Descrição detalhada da task."
    ),
    story_type: str = Option("feature", "--type", "-t", help="Tipo da story: feature, bug, chore."),
    iteration: str | None = Option(
        "current",
        "--iteration",
        "-i",
        help="Iteração (Sprint): 'current' (padrão), 'none' (sem iteração) ou ID/nome da iteração.",
    ),
    owner: str | None = Option(
        "me",
        "--owner",
        help="Responsável: 'me' (padrão, usuário logado), 'none' (sem owner) ou ID do membro.",
    ),
    workflow_state_id: int | None = Option(
        None, "--workflow-state-id", help="ID do estado inicial no workflow."
    ),
    service: str = common._service_option(),
) -> None:
    """Cria uma nova story no Shortcut, associada por padrão à iteração atual."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    it = common._resolve_create_iteration(client, iteration, as_json)
    target_iteration_id = it.id if it else None
    target_iteration_name = it.name if it else None
    owner_ids = common._resolve_create_owner(client, owner)
    try:
        story = client.create_story(
            name=title,
            description=description,
            story_type=story_type,
            iteration_id=target_iteration_id,
            owner_ids=owner_ids,
            workflow_state_id=workflow_state_id,
        )
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json(story.model_dump())
    else:
        app_url = story.app_url or f"https://app.shortcut.com/story/{story.id}"
        iter_str = (
            f"[cyan]{target_iteration_name}[/cyan] (#{target_iteration_id})"
            if target_iteration_id
            else "[dim]Nenhuma[/dim]"
        )
        owners_str = ", ".join(story.owner_ids) if story.owner_ids else "[dim]Nenhum[/dim]"
        desc_preview = (
            f"\n\n[bold]Descrição:[/bold]\n{story.description}" if story.description else ""
        )
        content = f"[bold]ID:[/bold] #{story.id}\n[bold]Título:[/bold] {story.name}\n[bold]Tipo:[/bold] {story.story_type.upper()}\n[bold]Iteração:[/bold] {iter_str}\n[bold]Owner:[/bold] {owners_str}\n[bold]URL Web:[/bold] [cyan]{app_url}[/cyan]{desc_preview}"
        print_panel(f"Task #{story.id} criada com sucesso!", content)
