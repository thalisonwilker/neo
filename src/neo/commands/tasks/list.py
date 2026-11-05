"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel, print_table
from neo.services.tasks.errors import TaskProviderError


def tasks_list(
    ctx: typer.Context,
    service: str = common._service_option(),
    mine: bool = Option(False, "--mine", "-m", help="Filtra apenas stories atribuídas a você."),
    iteration: str | None = Option(
        None,
        "--iteration",
        "-i",
        help="Filtra pela iteração informada (nome, número, ID ou 'all'). Padrão: última iteração.",
    ),
) -> None:
    """Lista stories ativas no workspace do Shortcut (filtrando pela última iteração por padrão)."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    target_iter = common._resolve_target_iteration(client, iteration, as_json)
    owner_id: str | None = None
    if mine:
        try:
            member = client.get_current_member()
            owner_id = member.mention_name or member.id
        except TaskProviderError as e:
            print_error(
                f"Não foi possível obter dados do usuário para filtro --mine: {e}",
                as_json=as_json,
                code=1,
            )
            raise typer.Exit(code=1) from e
    try:
        stories = client.list_stories(
            owner_id=owner_id, iteration_id=target_iter.id if target_iter else None
        )
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    if as_json:
        print_json([s.model_dump() for s in stories])
    else:
        iter_suffix = f" — {target_iter.name}" if target_iter else ""
        if not stories:
            print_panel(
                f"Stories{iter_suffix}",
                "Nenhuma story ativa encontrada para os filtros selecionados.",
            )
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
        base_title = "Minhas Stories no Shortcut" if mine else "Stories Ativas no Shortcut"
        print_table(f"{base_title}{iter_suffix}", columns, rows)
