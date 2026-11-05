"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands.tasks import _common as common
from neo.config import (
    get_task_columns_config,
)
from neo.output import print_error, print_json, print_table
from neo.services.tasks.errors import TaskProviderError
from neo.services.tasks.provider import require_workflows


def tasks_resume(
    ctx: typer.Context,
    service: str = common._service_option(),
    all_tasks: bool = Option(
        False,
        "--all",
        "-a",
        help="Exibe tasks de todos os membros do board (padrão: apenas minhas tasks).",
    ),
    iteration: str | None = Option(
        None,
        "--iteration",
        "-i",
        help="Filtra pela iteração informada (nome, número, ID ou 'all'). Padrão: última iteração.",
    ),
    configure: bool = Option(
        False,
        "--configure",
        "-c",
        help="Abre a configuração interativa das colunas (A fazer, Fazendo, Feito).",
    ),
    limit: int = Option(
        10, "--limit", "-l", help="Quantidade máxima de tasks exibidas por coluna."
    ),
) -> None:
    """Exibe um quadro Kanban com as tasks nas colunas A fazer, Fazendo e Feito."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    svc = common._resolve_service(ctx, service)
    client = common._get_client(svc, as_json)
    columns_cfg = get_task_columns_config(service=svc)
    if columns_cfg is None or configure:
        if as_json:
            print_error(
                f"As colunas (A fazer, Fazendo, Feito) não estão configuradas para '{svc}'. Execute `neo tasks config columns` ou `neo tasks resume` em modo interativo.",
                as_json=True,
                code=1,
            )
            raise typer.Exit(code=1)
        columns_cfg = common._interactive_configure_columns(client, svc, as_json=as_json)
    target_iter = common._resolve_target_iteration(client, iteration, as_json)
    try:
        states = require_workflows(client).list_workflow_states()
    except TaskProviderError as e:
        print_error(f"Falha ao obter colunas do workflow: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    state_id_to_name: dict[int, str] = {st.id: st.name for st in states}
    owner_id: str | None = None
    if not all_tasks:
        try:
            member = client.get_current_member()
            owner_id = member.mention_name or member.id
        except TaskProviderError as e:
            print_error(
                f"Não foi possível obter dados do usuário autenticado: {e}", as_json=as_json, code=1
            )
            raise typer.Exit(code=1) from e
    try:
        stories = client.list_stories(
            owner_id=owner_id, iteration_id=target_iter.id if target_iter else None
        )
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    todo_stories = [
        s
        for s in stories
        if common._story_matches_columns(s, columns_cfg["todo"], state_id_to_name)
    ]
    doing_stories = [
        s
        for s in stories
        if common._story_matches_columns(s, columns_cfg["doing"], state_id_to_name)
    ]
    done_stories = [
        s
        for s in stories
        if common._story_matches_columns(s, columns_cfg["done"], state_id_to_name)
    ]
    if as_json:
        print_json(
            {
                "service": svc,
                "filter": "all" if all_tasks else "mine",
                "iteration": target_iter.model_dump() if target_iter else None,
                "column_mapping": columns_cfg,
                "todo": [s.model_dump() for s in todo_stories[:limit]],
                "doing": [s.model_dump() for s in doing_stories[:limit]],
                "done": [s.model_dump() for s in done_stories[:limit]],
            }
        )
        return
    iter_name = target_iter.name if target_iter else None
    todo_cell = (
        "\n\n".join(common._format_kanban_card(s, iter_name) for s in todo_stories[:limit])
        if todo_stories
        else "[dim]Nenhuma task[/dim]"
    )
    doing_cell = (
        "\n\n".join(common._format_kanban_card(s, iter_name) for s in doing_stories[:limit])
        if doing_stories
        else "[dim]Nenhuma task[/dim]"
    )
    done_cell = (
        "\n\n".join(common._format_kanban_card(s, iter_name) for s in done_stories[:limit])
        if done_stories
        else "[dim]Nenhuma task[/dim]"
    )
    headers = [
        f"📝 A fazer ({len(todo_stories)})\n[dim]{', '.join(columns_cfg['todo'])}[/dim]",
        f"🚧 Fazendo ({len(doing_stories)})\n[dim]{', '.join(columns_cfg['doing'])}[/dim]",
        f"✅ Feito ({len(done_stories)})\n[dim]{', '.join(columns_cfg['done'])}[/dim]",
    ]
    scope_label = "Todas as Tasks do Board" if all_tasks else "Minhas Tasks"
    iter_suffix = f" — {target_iter.name}" if target_iter else ""
    print_table(
        f"Quadro Resumo ({svc.capitalize()} — {scope_label}{iter_suffix})",
        headers,
        [[todo_cell, doing_cell, done_cell]],
    )
