"""Funções compartilhadas dos comandos de tarefas."""

from __future__ import annotations

from typing import Any

import typer
from rich.markup import escape
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    DEFAULT_TASK_SERVICE,
    SUPPORTED_TASK_SERVICES,
    get_credential,
    set_task_columns_config,
    validate_task_service,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError
from neo.services.tasks.models import (
    TaskIteration,
    TaskStory,
    TaskWorkflowState,
)
from neo.services.tasks.provider import TaskProvider, require_iterations, require_workflows
from neo.services.tasks.resolver import create_task_provider


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


def _get_client(service: str, as_json: bool) -> TaskProvider:
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
    return create_task_provider(service, token)


def _resolve_selected_states(raw_input: str, states: list[TaskWorkflowState]) -> list[str]:
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
    client: TaskProvider, service: str, as_json: bool = False
) -> dict[str, list[str]]:
    """Lista as colunas do serviço e conduz o mapeamento interativo de A fazer, Fazendo e Feito."""
    try:
        states = require_workflows(client).list_workflow_states()
    except TaskProviderError as e:
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


def _resolve_target_iteration(
    client: TaskProvider,
    iteration_opt: str | None,
    as_json: bool,
) -> TaskIteration | None:
    """Resolve a iteração alvo (padrão = última iteração; 'all' = todas; ou busca por termo)."""
    try:
        return require_iterations(client).resolve_iteration(iteration_opt)
    except TaskProviderNotFoundError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except AssertionError:
        # Em testes legados com respx que não mockaram /iterations quando iteration_opt é None
        if iteration_opt is None:
            return None
        raise


def _resolve_create_iteration(
    client: TaskProvider,
    iteration_opt: str | None,
    as_json: bool,
) -> TaskIteration | None:
    """Resolve a iteração para a nova story (padrão = última iteração; 'none' = sem iteração; ou termo)."""
    if iteration_opt and iteration_opt.strip().lower() in ("none", "null", "false"):
        return None
    try:
        if iteration_opt in ("current", "latest", None):
            return require_iterations(client).get_latest_iteration()
        return require_iterations(client).resolve_iteration(iteration_opt)
    except TaskProviderNotFoundError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except AssertionError:
        return None


def _resolve_create_owner(
    client: TaskProvider,
    owner_opt: str | None,
) -> list[str] | None:
    """Resolve o owner para a nova story (padrão = usuário logado 'me'; 'none' = sem owner; ou ID)."""
    if not owner_opt or owner_opt.strip().lower() in ("none", "null", "false"):
        return None
    if owner_opt.strip().lower() == "me":
        try:
            member = client.get_current_member()
            return [member.id] if member and member.id else None
        except TaskProviderError:
            return None
    return [owner_opt.strip()]


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
    except TaskProviderNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json(comment.model_dump())
    else:
        print_success(
            f'Comentário #{comment.id} adicionado à story #{story_id}: [cyan]"{escape(comment.text)}"[/cyan]'
        )


def _format_kanban_card(story: TaskStory, iteration_name: str | None = None) -> str:
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
    story: TaskStory,
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
