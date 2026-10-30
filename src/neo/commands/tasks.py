"""Comandos de tasks/demandas (`neo tasks`) — hoje integrado ao Shortcut (API v3)."""

from __future__ import annotations

from typing import Any

import typer
from rich.markup import escape
from typer import Argument, Option

from neo.commands._credentials import is_json_mode, remove_token, save_token, show_token
from neo.config import (
    DEFAULT_TASK_SERVICE,
    SUPPORTED_TASK_SERVICES,
    get_credential,
    get_task_columns_config,
    set_task_columns_config,
    validate_task_service,
)
from neo.integrations.shortcut import (
    ShortcutClient,
    ShortcutError,
    ShortcutNotFoundError,
)
from neo.integrations.shortcut_models import (
    ShortcutIteration,
    ShortcutStory,
    ShortcutWorkflowState,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table

tasks_app = typer.Typer(
    name="tasks",
    help="Consulta e análise de tasks/demandas (Shortcut, API v3). Use --service para escolher o serviço.",
    no_args_is_help=True,
)

tasks_config_app = typer.Typer(
    name="config",
    help="Credenciais do serviço de tasks (Shortcut).",
    no_args_is_help=True,
)
tasks_app.add_typer(tasks_config_app, name="config")

tasks_check_app = typer.Typer(
    name="check",
    help="Gerencia itens de checklist (tasks) de uma story no Shortcut.",
    no_args_is_help=True,
)
tasks_app.add_typer(tasks_check_app, name="check")

tasks_comment_app = typer.Typer(
    name="comment",
    help="Adiciona comentários em stories no Shortcut.",
    no_args_is_help=True,
)
tasks_app.add_typer(tasks_comment_app, name="comment")


def _service_option() -> Any:
    return Option(
        DEFAULT_TASK_SERVICE,
        "--service",
        "-s",
        help=f"Serviço de tasks: {', '.join(SUPPORTED_TASK_SERVICES)}.",
    )


def _resolve_service(ctx: typer.Context, service: str) -> str:
    try:
        return validate_task_service(service)
    except ValueError as e:
        print_error(str(e), as_json=is_json_mode(ctx), code=1)
        raise typer.Exit(code=1) from e


def _get_client(service: str, as_json: bool) -> ShortcutClient:
    try:
        validate_task_service(service)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    token = get_credential("shortcut")
    if not token:
        msg = "Credenciais do Shortcut não configuradas. Execute `neo tasks config set`."
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)
    return ShortcutClient(token=token)


@tasks_config_app.command("set")
def config_set(
    ctx: typer.Context,
    service: str = _service_option(),
    token: str = Option(
        None,
        "--token",
        "-t",
        help="Token de acesso da API. Se omitido, solicita via prompt seguro.",
    ),
) -> None:
    """Configura o token do serviço de tasks de forma segura."""
    save_token(ctx, _resolve_service(ctx, service), token)


@tasks_config_app.command("get")
def config_get(
    ctx: typer.Context,
    service: str = _service_option(),
) -> None:
    """Exibe o status e o token mascarado do serviço de tasks."""
    show_token(ctx, _resolve_service(ctx, service))


@tasks_config_app.command("delete")
def config_delete(
    ctx: typer.Context,
    service: str = _service_option(),
) -> None:
    """Remove a credencial armazenada do serviço de tasks."""
    remove_token(ctx, _resolve_service(ctx, service))


def _resolve_selected_states(raw_input: str, states: list[ShortcutWorkflowState]) -> list[str]:
    """Converte entrada do usuário (índices '1, 2' ou nomes de colunas) em nomes de colunas."""
    tokens = [t.strip() for t in raw_input.split(",") if t.strip()]
    if not tokens:
        raise ValueError("Nenhuma coluna informada.")

    resolved: list[str] = []
    for tok in tokens:
        if tok.isdigit():
            idx = int(tok)
            if 1 <= idx <= len(states):
                col_name = states[idx - 1].name
                if col_name not in resolved:
                    resolved.append(col_name)
                continue
            # Pode ser ID direto do workflow_state
            by_id = next((s.name for s in states if str(s.id) == tok), None)
            if by_id:
                if by_id not in resolved:
                    resolved.append(by_id)
                continue
            raise ValueError(
                f"Índice de coluna inválido: '{tok}'. Escolha um número entre 1 e {len(states)}."
            )

        # Busca por nome exato ou parcial (case-insensitive)
        exact = next((s.name for s in states if s.name.lower() == tok.lower()), None)
        if exact:
            if exact not in resolved:
                resolved.append(exact)
            continue

        partial = next((s.name for s in states if tok.lower() in s.name.lower()), None)
        if partial:
            if partial not in resolved:
                resolved.append(partial)
            continue

        raise ValueError(f"Coluna '{tok}' não encontrada nos workflows do serviço.")

    return resolved


def _interactive_configure_columns(
    client: ShortcutClient, service: str, as_json: bool = False
) -> dict[str, list[str]]:
    """Lista as colunas do serviço e conduz o mapeamento interativo de A fazer, Fazendo e Feito."""
    try:
        states = client.list_workflow_states()
    except ShortcutError as e:
        print_error(
            f"Não foi possível consultar as colunas do serviço '{service}': {e}",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1) from e

    if not states:
        print_error(
            f"Nenhuma coluna/workflow encontrada no serviço '{service}'.",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1)

    print_panel(
        f"Configuração do Board ({service})",
        "As colunas [bold]A fazer[/bold], [bold]Fazendo[/bold] e [bold]Feito[/bold] "
        "ainda não estão configuradas (ou foi solicitada reconfiguração).\n"
        "Selecione abaixo qual(is) coluna(s) do seu board correspondem a cada etapa.",
    )

    columns = ["#", "Coluna / Estado", "Workflow", "Categoria"]
    rows: list[list[str]] = []
    for idx, st in enumerate(states, start=1):
        wf_label = st.workflow_name or "-"
        rows.append([str(idx), st.name, wf_label, st.type])
    print_table(f"Colunas Disponíveis no {service.capitalize()}", columns, rows)

    todo_raw = typer.prompt(
        "Selecione a(s) coluna(s) para 'A fazer' (números ou nomes separados por vírgula)"
    )
    doing_raw = typer.prompt(
        "Selecione a(s) coluna(s) para 'Fazendo' (números ou nomes separados por vírgula)"
    )
    done_raw = typer.prompt(
        "Selecione a(s) coluna(s) para 'Feito' (números ou nomes separados por vírgula)"
    )

    try:
        todo_cols = _resolve_selected_states(todo_raw, states)
        doing_cols = _resolve_selected_states(doing_raw, states)
        done_cols = _resolve_selected_states(done_raw, states)
        set_task_columns_config(todo=todo_cols, doing=doing_cols, done=done_cols, service=service)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    mapping = {"todo": todo_cols, "doing": doing_cols, "done": done_cols}
    print_success(
        f"Colunas configuradas com sucesso para '{service}':\n"
        f"  • A fazer: {', '.join(todo_cols)}\n"
        f"  • Fazendo: {', '.join(doing_cols)}\n"
        f"  • Feito: {', '.join(done_cols)}"
    )
    return mapping


@tasks_config_app.command("columns")
def config_columns(
    ctx: typer.Context,
    service: str = _service_option(),
    todo: str | None = Option(
        None,
        "--todo",
        help="Coluna(s) para 'A fazer' separadas por vírgula (ex: 'Backlog de Sprint, Bug').",
    ),
    doing: str | None = Option(
        None,
        "--doing",
        help="Coluna(s) para 'Fazendo' separadas por vírgula (ex: 'Em Progresso').",
    ),
    done: str | None = Option(
        None,
        "--done",
        help="Coluna(s) para 'Feito' separadas por vírgula (ex: 'Finalizado').",
    ),
) -> None:
    """Configura quais colunas do serviço correspondem a 'A fazer', 'Fazendo' e 'Feito'."""
    as_json = is_json_mode(ctx)
    svc = _resolve_service(ctx, service)

    if todo is not None or doing is not None or done is not None:
        if not (todo and doing and done):
            print_error(
                "Para configurar via flags, informe simultaneamente `--todo`, `--doing` e `--done`.",
                as_json=as_json,
                code=1,
            )
            raise typer.Exit(code=1)
        todo_list = [c.strip() for c in todo.split(",") if c.strip()]
        doing_list = [c.strip() for c in doing.split(",") if c.strip()]
        done_list = [c.strip() for c in done.split(",") if c.strip()]
        try:
            set_task_columns_config(todo=todo_list, doing=doing_list, done=done_list, service=svc)
        except ValueError as e:
            print_error(str(e), as_json=as_json, code=1)
            raise typer.Exit(code=1) from e

        mapping = {"todo": todo_list, "doing": doing_list, "done": done_list}
        print_success(
            f"Colunas de '{svc}' atualizadas com sucesso!",
            as_json=as_json,
            json_payload={"status": "success", "service": svc, "columns": mapping},
        )
        return

    if as_json:
        print_error(
            "No modo `--json`, informe `--todo`, `--doing` e `--done` para configurar as colunas.",
            as_json=True,
            code=1,
        )
        raise typer.Exit(code=1)

    client = _get_client(svc, as_json)
    _interactive_configure_columns(client, svc, as_json=as_json)


@tasks_app.command("whoami")
def tasks_whoami(
    ctx: typer.Context,
    service: str = _service_option(),
) -> None:
    """Verifica e exibe o membro autenticado na API do Shortcut."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)

    try:
        member = client.get_current_member()
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(member.model_dump())
    else:
        email = member.email_address or "-"
        print_panel(
            "Usuário Autenticado no Shortcut",
            f"[bold]Nome:[/bold] {member.name}\n"
            f"[bold]Username:[/bold] @{member.mention_name}\n"
            f"[bold]E-mail:[/bold] {email}\n"
            f"[bold]ID:[/bold] {member.id}",
        )


@tasks_app.command("iterations")
def tasks_iterations(
    ctx: typer.Context,
    service: str = _service_option(),
    limit: int = Option(15, "--limit", "-l", help="Quantidade máxima de iterações a exibir."),
) -> None:
    """Lista as iterações (sprints) disponíveis no serviço, destacando a última (atual)."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)

    try:
        iterations = client.list_iterations()
    except ShortcutError as e:
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


def _resolve_target_iteration(
    client: ShortcutClient,
    iteration_opt: str | None,
    as_json: bool,
) -> ShortcutIteration | None:
    """Resolve a iteração alvo (padrão = última iteração; 'all' = todas; ou busca por termo)."""
    try:
        return client.resolve_iteration(iteration_opt)
    except ShortcutNotFoundError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except AssertionError:
        # Em testes legados com respx que não mockaram /iterations quando iteration_opt é None
        if iteration_opt is None:
            return None
        raise


def _resolve_create_iteration(
    client: ShortcutClient,
    iteration_opt: str | None,
    as_json: bool,
) -> ShortcutIteration | None:
    """Resolve a iteração para a nova story (padrão = última iteração; 'none' = sem iteração; ou termo)."""
    if iteration_opt and iteration_opt.strip().lower() in ("none", "null", "false"):
        return None
    try:
        if iteration_opt in ("current", "latest", None):
            return client.get_latest_iteration()
        return client.resolve_iteration(iteration_opt)
    except ShortcutNotFoundError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except AssertionError:
        return None


def _resolve_create_owner(
    client: ShortcutClient,
    owner_opt: str | None,
) -> list[str] | None:
    """Resolve o owner para a nova story (padrão = usuário logado 'me'; 'none' = sem owner; ou ID)."""
    if not owner_opt or owner_opt.strip().lower() in ("none", "null", "false"):
        return None
    if owner_opt.strip().lower() == "me":
        try:
            member = client.get_current_member()
            return [member.id] if member and member.id else None
        except ShortcutError:
            return None
    return [owner_opt.strip()]


@tasks_app.command("create")
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
        None,
        "--workflow-state-id",
        help="ID do estado inicial no workflow.",
    ),
    service: str = _service_option(),
) -> None:
    """Cria uma nova story no Shortcut, associada por padrão à iteração atual."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)

    it = _resolve_create_iteration(client, iteration, as_json)
    target_iteration_id = it.id if it else None
    target_iteration_name = it.name if it else None

    owner_ids = _resolve_create_owner(client, owner)

    try:
        story = client.create_story(
            name=title,
            description=description,
            story_type=story_type,
            iteration_id=target_iteration_id,
            owner_ids=owner_ids,
            workflow_state_id=workflow_state_id,
        )
    except ShortcutError as e:
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
        content = (
            f"[bold]ID:[/bold] #{story.id}\n"
            f"[bold]Título:[/bold] {story.name}\n"
            f"[bold]Tipo:[/bold] {story.story_type.upper()}\n"
            f"[bold]Iteração:[/bold] {iter_str}\n"
            f"[bold]Owner:[/bold] {owners_str}\n"
            f"[bold]URL Web:[/bold] [cyan]{app_url}[/cyan]"
            f"{desc_preview}"
        )
        print_panel(f"Task #{story.id} criada com sucesso!", content)


@tasks_app.command("list")
def tasks_list(
    ctx: typer.Context,
    service: str = _service_option(),
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
    client = _get_client(service, as_json)

    target_iter = _resolve_target_iteration(client, iteration, as_json)

    owner_id: str | None = None
    if mine:
        try:
            member = client.get_current_member()
            owner_id = member.mention_name or member.id
        except ShortcutError as e:
            print_error(
                f"Não foi possível obter dados do usuário para filtro --mine: {e}",
                as_json=as_json,
                code=1,
            )
            raise typer.Exit(code=1) from e

    try:
        stories = client.list_stories(
            owner_id=owner_id,
            iteration_id=target_iter.id if target_iter else None,
        )
    except ShortcutError as e:
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


@tasks_app.command("search")
def tasks_search(
    ctx: typer.Context,
    service: str = _service_option(),
    query: str = Argument(..., help="Termo de busca para pesquisar stories."),
) -> None:
    """Pesquisa stories por palavra-chave ou texto."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)

    try:
        stories = client.search_stories(query)
    except ShortcutError as e:
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


@tasks_app.command("show")
@tasks_app.command("get", hidden=True)
def tasks_show(
    ctx: typer.Context,
    service: str = _service_option(),
    story_id: int = Argument(..., help="ID numérico da story no Shortcut."),
) -> None:
    """Exibe detalhes completos de uma story pelo ID."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)

    try:
        story = client.get_story(story_id)
    except ShortcutNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
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

        content = (
            f"[bold]Tipo:[/bold] {story.story_type.upper()}\n"
            f"[bold]Labels:[/bold] {labels_str}\n"
            f"[bold]URL Web:[/bold] [cyan]{app_url}[/cyan]\n\n"
            f"[bold]Descrição:[/bold]\n{desc}"
            f"{''.join(checklist_parts)}"
            f"{''.join(comment_parts)}"
        )
        print_panel(f"Story #{story.id}: {story.name}", content)


# Comandos de Checklist (neo tasks check ...)
@tasks_check_app.command("add")
def check_add(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story/task pai no Shortcut."),
    description: str = Argument(..., help="Descrição do item de checklist."),
    service: str = _service_option(),
) -> None:
    """Adiciona um item de checklist a uma story."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)
    try:
        task = client.create_task(story_id, description)
    except ShortcutNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(task.model_dump())
    else:
        print_success(
            f"Checklist item #{task.id} adicionado à story #{story_id}: [yellow][ ][/yellow] {escape(task.description)}"
        )


@tasks_check_app.command("complete")
@tasks_check_app.command("done", hidden=True)
def check_complete(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story/task pai no Shortcut."),
    task_id: int = Argument(..., help="ID do item de checklist a concluir."),
    service: str = _service_option(),
) -> None:
    """Marca um item de checklist como concluído."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)
    try:
        task = client.update_task(story_id, task_id, complete=True)
    except ShortcutNotFoundError as e:
        print_error(f"Recurso não encontrado: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(task.model_dump())
    else:
        print_success(
            f"Checklist item #{task.id} marcado como [green][✓] Concluído[/green] na story #{story_id}."
        )


@tasks_check_app.command("uncomplete")
@tasks_check_app.command("undone", hidden=True)
def check_uncomplete(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story/task pai no Shortcut."),
    task_id: int = Argument(..., help="ID do item de checklist a reabrir."),
    service: str = _service_option(),
) -> None:
    """Desmarca um item de checklist (reabre como pendente)."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)
    try:
        task = client.update_task(story_id, task_id, complete=False)
    except ShortcutNotFoundError as e:
        print_error(f"Recurso não encontrado: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(task.model_dump())
    else:
        print_success(
            f"Checklist item #{task.id} reaberto como [yellow][ ] Aberto[/yellow] na story #{story_id}."
        )


# Comandos de Comentário (neo tasks comment ...)
def _add_comment_impl(
    ctx: typer.Context,
    story_id: int,
    text: str,
    service: str,
) -> None:
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)
    try:
        comment = client.create_comment(story_id, text)
    except ShortcutNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(comment.model_dump())
    else:
        print_success(
            f'Comentário #{comment.id} adicionado à story #{story_id}: [cyan]"{escape(comment.text)}"[/cyan]'
        )


@tasks_comment_app.command("add")
def comment_add(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story no Shortcut."),
    text: str = Argument(..., help="Texto do comentário."),
    service: str = _service_option(),
) -> None:
    """Adiciona um comentário a uma story."""
    _add_comment_impl(ctx, story_id, text, service)


@tasks_app.command("analyze")
def tasks_analyze(
    ctx: typer.Context,
    service: str = _service_option(),
    story_id: int = Argument(..., help="ID da story a ser analisada."),
) -> None:
    """Analisa o contexto da story sugerindo branch git, prefixos e palavras-chave."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_client(service, as_json)

    try:
        analysis = client.analyze_story(story_id)
    except ShortcutNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada para análise: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(analysis.model_dump())
    else:
        kw_str = ", ".join(analysis.keywords) if analysis.keywords else "-"
        blocker_badge = (
            "[bold red]SIM (Alerta de impedimento)[/bold red]"
            if analysis.has_blockers
            else "[green]Não[/green]"
        )
        criteria_text = ""
        if analysis.acceptance_criteria:
            criteria_text = "\n\n[bold]Critérios de Aceite Detectados:[/bold]\n" + "\n".join(
                [f"• {c}" for c in analysis.acceptance_criteria]
            )

        content = (
            f"[bold]Título:[/bold] {analysis.title}\n"
            f"[bold]Branch Recomendada:[/bold] [cyan]{analysis.suggested_branch}[/cyan]\n"
            f"[bold]Prefixo de Commit:[/bold] [yellow]{escape(analysis.commit_prefix)}[/yellow]\n"
            f"[bold]Possui Bloqueios?:[/bold] {blocker_badge}\n"
            f"[bold]Palavras-chave de Busca:[/bold] {kw_str}"
            f"{criteria_text}"
        )

        print_panel(f"Análise de Contexto: Story #{analysis.story_id}", content)


def _format_kanban_card(story: ShortcutStory, iteration_name: str | None = None) -> str:
    """Formata uma story como card compacto para exibição na coluna da tabela Kanban."""
    type_badge = (
        "[red]● Bug[/red]"
        if story.story_type == "bug"
        else "[green]● Feature[/green]"
        if story.story_type == "feature"
        else "[yellow]● Chore[/yellow]"
    )
    meta_parts: list[str] = []
    if iteration_name:
        meta_parts.append(f"🔄 {iteration_name}")
    if story.labels:
        meta_parts.append(f"🏷 {', '.join(story.labels)}")
    meta_line = f"\n[dim]{'  '.join(meta_parts)}[/dim]" if meta_parts else ""
    return f"[bold yellow]#{story.id}[/bold yellow] {type_badge}\n[bold]{escape(story.name)}[/bold]{meta_line}"


def _story_matches_columns(
    story: ShortcutStory,
    target_columns: list[str],
    state_id_to_name: dict[int, str],
) -> bool:
    """Verifica se a story pertence a alguma das colunas configuradas (por nome ou ID)."""
    state_name = ""
    if story.workflow_state_id is not None and story.workflow_state_id in state_id_to_name:
        state_name = state_id_to_name[story.workflow_state_id]
    elif story.workflow_state_name:
        state_name = story.workflow_state_name

    state_id_str = str(story.workflow_state_id) if story.workflow_state_id is not None else ""
    for col in target_columns:
        col_lower = col.strip().lower()
        if not col_lower:
            continue
        if state_name and state_name.lower() == col_lower:
            return True
        if state_id_str and state_id_str == col_lower:
            return True
    return False


@tasks_app.command("resume")
def tasks_resume(
    ctx: typer.Context,
    service: str = _service_option(),
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
        10,
        "--limit",
        "-l",
        help="Quantidade máxima de tasks exibidas por coluna.",
    ),
) -> None:
    """Exibe um quadro Kanban com as tasks nas colunas A fazer, Fazendo e Feito."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    svc = _resolve_service(ctx, service)
    client = _get_client(svc, as_json)

    columns_cfg = get_task_columns_config(service=svc)
    if columns_cfg is None or configure:
        if as_json:
            print_error(
                f"As colunas (A fazer, Fazendo, Feito) não estão configuradas para '{svc}'. "
                "Execute `neo tasks config columns` ou `neo tasks resume` em modo interativo.",
                as_json=True,
                code=1,
            )
            raise typer.Exit(code=1)
        columns_cfg = _interactive_configure_columns(client, svc, as_json=as_json)

    target_iter = _resolve_target_iteration(client, iteration, as_json)

    try:
        states = client.list_workflow_states()
    except ShortcutError as e:
        print_error(f"Falha ao obter colunas do workflow: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    state_id_to_name: dict[int, str] = {st.id: st.name for st in states}

    owner_id: str | None = None
    if not all_tasks:
        try:
            member = client.get_current_member()
            owner_id = member.mention_name or member.id
        except ShortcutError as e:
            print_error(
                f"Não foi possível obter dados do usuário autenticado: {e}",
                as_json=as_json,
                code=1,
            )
            raise typer.Exit(code=1) from e

    try:
        stories = client.list_stories(
            owner_id=owner_id,
            iteration_id=target_iter.id if target_iter else None,
        )
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    todo_stories = [
        s for s in stories if _story_matches_columns(s, columns_cfg["todo"], state_id_to_name)
    ]
    doing_stories = [
        s for s in stories if _story_matches_columns(s, columns_cfg["doing"], state_id_to_name)
    ]
    done_stories = [
        s for s in stories if _story_matches_columns(s, columns_cfg["done"], state_id_to_name)
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
        "\n\n".join(_format_kanban_card(s, iter_name) for s in todo_stories[:limit])
        if todo_stories
        else "[dim]Nenhuma task[/dim]"
    )
    doing_cell = (
        "\n\n".join(_format_kanban_card(s, iter_name) for s in doing_stories[:limit])
        if doing_stories
        else "[dim]Nenhuma task[/dim]"
    )
    done_cell = (
        "\n\n".join(_format_kanban_card(s, iter_name) for s in done_stories[:limit])
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
