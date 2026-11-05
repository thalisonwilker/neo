"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel, print_table
from neo.services.tasks.errors import TaskProviderError
from neo.services.tasks.provider import require_iterations


def tasks_iterations(
    ctx: typer.Context,
    service: str = common._service_option(),
    limit: int = Option(15, "--limit", "-l", help="Quantidade máxima de iterações a exibir."),
) -> None:
    """Lista as iterações (sprints) disponíveis no serviço, destacando a última (atual)."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        iterations = require_iterations(client).list_iterations()
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json([it.model_dump() for it in iterations[:limit]])
        return
    if not iterations:
        print_panel("Iterações", "Nenhuma iteração (sprint) encontrada no serviço.")
        return
    columns = ["ID", "Nome", "Status", "Período"]
    rows: list[list[str]] = []
    for idx, it in enumerate(iterations[:limit]):
        name_label = f"[bold green]{it.name} [● Atual][/bold green]" if idx == 0 else it.name
        period = f"{it.start_date} → {it.end_date}" if it.start_date or it.end_date else "-"
        rows.append([str(it.id), name_label, it.status, period])
    print_table("Iterações no Shortcut", columns, rows)
