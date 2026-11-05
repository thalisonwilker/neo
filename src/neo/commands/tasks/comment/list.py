"""Ação de tarefas."""

from __future__ import annotations

import typer
from rich.markup import escape
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel, print_table
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError


def comment_list(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story no Shortcut."),
    service: str = common._service_option(),
) -> None:
    """Lista todos os comentários de uma story."""
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
        print_json([c.model_dump() for c in story.comments])
        return
    if not story.comments:
        print_panel(
            f"Comentários da Story #{story.id}",
            'Nenhum comentário encontrado nesta story.\nUse `neo tasks comment add <id> "texto"` para adicionar.',
        )
        return
    columns = ["ID", "Autor", "Comentário"]
    rows: list[list[str]] = []
    for c in story.comments:
        author = c.author_id or "-"
        rows.append([f"#{c.id}", author, escape(c.text)])
    print_table(f"Comentários da Story #{story.id} ({len(story.comments)})", columns, rows)
