"""Ação de tarefas."""

from __future__ import annotations

import typer
from rich.markup import escape
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError


def tasks_show(
    ctx: typer.Context,
    service: str = common._service_option(),
    story_id: int = Argument(..., help="ID numérico da story no Shortcut."),
) -> None:
    """Exibe detalhes completos de uma story pelo ID."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        story = client.get_story(story_id)
    except TaskProviderNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json(story.model_dump())
    else:
        desc = story.description or "[dim]Sem descrição.[/dim]"
        labels_str = ", ".join(story.labels) if story.labels else "Nenhuma"
        app_url = story.app_url or f"https://app.shortcut.com/story/{story.id}"
        checklist_parts: list[str] = []
        if story.tasks:
            done_cnt = sum(1 for t in story.tasks if t.complete)
            checklist_parts.append(f"\n\n[bold]Checklist ({done_cnt}/{len(story.tasks)}):[/bold]")
            for t in story.tasks:
                box = "[green][✓][/green]" if t.complete else "[yellow][ ][/yellow]"
                checklist_parts.append(f"\n  {box} #{t.id} {escape(t.description)}")
        comment_parts: list[str] = []
        if story.comments:
            comment_parts.append(f"\n\n[bold]Comentários ({len(story.comments)}):[/bold]")
            for c in story.comments:
                comment_parts.append(f"\n  [cyan]•[/cyan] #{c.id}: {escape(c.text)}")
        content = f"[bold]Tipo:[/bold] {story.story_type.upper()}\n[bold]Labels:[/bold] {labels_str}\n[bold]URL Web:[/bold] [cyan]{app_url}[/cyan]\n\n[bold]Descrição:[/bold]\n{desc}{''.join(checklist_parts)}{''.join(comment_parts)}"
        print_panel(f"Story #{story.id}: {story.name}", content)
