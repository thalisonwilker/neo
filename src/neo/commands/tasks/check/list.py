"""Ação de tarefas."""

from __future__ import annotations

import typer
from rich.markup import escape
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel, print_table
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError


def check_list(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story/task pai no Shortcut."),
    service: str = common._service_option(),
) -> None:
    """Lista todos os itens de checklist de uma story."""
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
        print_json([t.model_dump() for t in story.tasks])
        return
    if not story.tasks:
        print_panel(
            f"Checklist da Story #{story.id}",
            'Nenhum item de checklist encontrado nesta story.\nUse `neo tasks check add <id> "descrição"` para adicionar.',
        )
        return
    done_cnt = sum(1 for t in story.tasks if t.complete)
    columns = ["ID", "Status", "Descrição"]
    rows: list[list[str]] = []
    for t in story.tasks:
        status_label = (
            "[bold green][✓] Concluído[/bold green]"
            if t.complete
            else "[bold yellow][ ] Aberto[/bold yellow]"
        )
        rows.append([f"#{t.id}", status_label, escape(t.description)])
    print_table(
        f"Checklist da Story #{story.id} ({done_cnt}/{len(story.tasks)} concluídos)", columns, rows
    )
