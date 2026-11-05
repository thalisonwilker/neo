"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel, print_table
from neo.services.tasks.errors import TaskProviderError


def tasks_search(
    ctx: typer.Context,
    service: str = common._service_option(),
    query: str = Argument(..., help="Termo de busca para pesquisar stories."),
) -> None:
    """Pesquisa stories por palavra-chave ou texto."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        stories = client.search_stories(query)
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json([s.model_dump() for s in stories])
    else:
        if not stories:
            print_panel(f"Busca: '{query}'", "Nenhuma story encontrada para o termo pesquisado.")
            return
        columns = ["ID", "Tipo", "Título", "Labels"]
        rows: list[list[str]] = []
        for s in stories:
            type_badge = (
                "[red]Bug[/red]"
                if s.story_type == "bug"
                else "[green]Feature[/green]"
                if s.story_type == "feature"
                else "[yellow]Chore[/yellow]"
            )
            labels_str = ", ".join(s.labels) if s.labels else "-"
            rows.append([f"[bold yellow]#{s.id}[/bold yellow]", type_badge, s.name, labels_str])
        print_table(f"Stories encontradas para '{query}'", columns, rows)
