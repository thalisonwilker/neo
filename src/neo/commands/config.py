"""Comandos de visão geral e preferências de agente do Neo (`neo config`)."""

from __future__ import annotations

import contextlib
import re
import shutil
from typing import Any

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import _inspect_local_git_status
from neo.config import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_TASK_SERVICE,
    ExitCode,
    get_agent_config_value,
    get_all_services_status,
    get_default_provider_config,
    get_task_columns_config,
    list_agent_config_values,
    set_agent_config_value,
    unset_agent_config_value,
    validate_agent_config_key,
)
from neo.integrations.resolver import (
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table
from neo.services.agent_validator import AgentValidationError, validate_agent_executable

config_app = typer.Typer(
    name="config",
    help="Visão geral das configurações do Neo (`neo git`, `neo tasks` e `neo config agent`).",
    no_args_is_help=True,
)

agent_config_app = typer.Typer(
    name="agent",
    help="Gerencia preferências do agente de codificação (command, model, sdd-provider, adapter).",
    no_args_is_help=True,
)
config_app.add_typer(agent_config_app, name="agent")


@agent_config_app.command("set")
def agent_config_set(
    ctx: typer.Context,
    key: str = Argument(
        ...,
        help="Chave de configuração (command, model, sdd-provider, adapter).",
    ),
    value: str = Argument(
        ...,
        help="Valor da chave de configuração.",
    ),
) -> None:
    """Define uma preferência do agente na seção `[agent]` de `config.toml`."""
    as_json = is_json_mode(ctx)
    try:
        valid_key = validate_agent_config_key(key)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    if valid_key == "command":
        _, current_adapter, _ = get_agent_config_value("adapter")
        try:
            check = validate_agent_executable(
                value,
                adapter=current_adapter or "antigravity",
                timeout=3.0,
                not_found_exit_code=int(ExitCode.USAGE_ERROR),
            )
        except (AgentValidationError, ValueError) as exc:
            code = getattr(exc, "exit_code", int(ExitCode.USAGE_ERROR))
            print_error(str(exc), as_json=as_json, code=code)
            raise typer.Exit(code=code) from exc

        try:
            saved_key, saved_val = set_agent_config_value(valid_key, value)
        except ValueError as exc:
            print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
            raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

        print_success(
            f"Configuração do agente atualizada: [bold]{saved_key}[/bold] = [cyan]{saved_val}[/cyan] "
            f"(versão detectada: {check['version']})",
            as_json=as_json,
            json_payload={
                "status": "success",
                "key": saved_key,
                "value": saved_val,
                "resolved_path": check["resolved_path"],
                "version": check["version"],
            },
        )
        return

    try:
        saved_key, saved_val = set_agent_config_value(valid_key, value)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    print_success(
        f"Configuração do agente atualizada: [bold]{saved_key}[/bold] = [cyan]{saved_val}[/cyan]",
        as_json=as_json,
        json_payload={
            "status": "success",
            "key": saved_key,
            "value": saved_val,
        },
    )


@agent_config_app.command("get")
def agent_config_get(
    ctx: typer.Context,
    key: str = Argument(
        ...,
        help="Chave a consultar (command, model, sdd-provider, adapter).",
    ),
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o valor efetivo de uma chave de configuração do agente e sua origem."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        valid_key, val, source = get_agent_config_value(key)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    if as_json:
        print_json({"key": valid_key, "value": val, "source": source})
    else:
        display_val = f"[cyan]{val}[/cyan]" if val else "[dim](não definido)[/dim]"
        print_panel(
            f"Configuração do Agente: {valid_key}",
            f"[bold]Chave:[/bold] {valid_key}\n"
            f"[bold]Valor:[/bold] {display_val}\n"
            f"[bold]Origem:[/bold] {source}",
        )


@agent_config_app.command("list")
def agent_config_list(
    ctx: typer.Context,
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Lista todas as chaves da seção `[agent]` com seus valores e origens."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        values = list_agent_config_values()
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    if as_json:
        print_json(values)
    else:
        columns = ["Chave", "Valor", "Origem"]
        rows = [
            [k, str(info["value"]) if info["value"] else "(não definido)", str(info["source"])]
            for k, info in values.items()
        ]
        print_table("Configurações do Agente ([agent])", columns, rows)


@agent_config_app.command("unset")
def agent_config_unset(
    ctx: typer.Context,
    key: str = Argument(
        ...,
        help="Chave a remover da seção [agent] (command, model, sdd-provider, adapter).",
    ),
) -> None:
    """Remove uma chave personalizada da seção `[agent]` de `config.toml`."""
    as_json = is_json_mode(ctx)
    try:
        valid_key = validate_agent_config_key(key)
        existed = unset_agent_config_value(valid_key)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    msg = (
        f"Chave [bold]{valid_key}[/bold] removida da seção [agent] (restaurada para o padrão)."
        if existed
        else f"Chave [bold]{valid_key}[/bold] já estava com o valor padrão."
    )
    print_success(
        msg,
        as_json=as_json,
        json_payload={
            "status": "success",
            "key": valid_key,
            "unset": True,
            "existed": existed,
        },
    )


def _detect_current_task_info(
    branch: str | None,
    tasks_configured: bool,
) -> tuple[str, str, dict[str, Any] | None]:
    """Descobre a tarefa ativa para os blocos Git e Tasks.

    Retorna (task_id_for_git, current_task_for_tasks, task_data_for_json).
    """
    if not tasks_configured:
        return "-", "-", None

    candidate_id: int | None = None
    if branch:
        match = re.search(r"(?:^|/|-|_|[a-zA-Z])(\d{3,7})(?:$|/|-|_|[a-zA-Z])", branch)
        if match:
            try:
                candidate_id = int(match.group(1))
            except ValueError:
                pass

    from neo.config import get_credential
    from neo.integrations.shortcut import ShortcutClient, ShortcutError

    token = get_credential("shortcut")
    if not token:
        return "-", "-", None

    client = ShortcutClient(token=token, timeout=2.0)

    # 1. Se encontrou candidate_id na branch
    if candidate_id:
        with contextlib.suppress(ShortcutError, httpx.RequestError, ValueError, KeyError):
            story = client.get_story(candidate_id)
            task_git = f"#{story.id}"
            if story.tasks:
                done_cnt = sum(1 for t in story.tasks if t.complete)
                task_full = f"#{story.id} {story.name} {done_cnt}/{len(story.tasks)}"
            else:
                task_full = f"#{story.id} {story.name}"
            json_info: dict[str, Any] = {
                "id": story.id,
                "title": story.name,
                "checklist": {
                    "completed": sum(1 for t in story.tasks if t.complete),
                    "total": len(story.tasks),
                }
                if story.tasks
                else None,
            }
            return task_git, task_full, json_info

    # 2. Fallback: primeira story atribuída a mim ou em andamento
    with contextlib.suppress(ShortcutError, httpx.RequestError, ValueError, KeyError):
        member = client.get_current_member()
        stories = client.list_stories()
        my_stories = [s for s in stories if member.id in s.owner_ids]
        target = my_stories[0] if my_stories else (stories[0] if stories else None)
        if target:
            full = client.get_story(target.id)
            task_git = f"#{full.id}"
            if full.tasks:
                done_cnt = sum(1 for t in full.tasks if t.complete)
                task_full = f"#{full.id} {full.name} {done_cnt}/{len(full.tasks)}"
            else:
                task_full = f"#{full.id} {full.name}"
            json_info = {
                "id": full.id,
                "title": full.name,
                "checklist": {
                    "completed": sum(1 for t in full.tasks if t.complete),
                    "total": len(full.tasks),
                }
                if full.tasks
                else None,
            }
            return task_git, task_full, json_info

    return "-", "-", None


@config_app.command("show")
def config_show(
    ctx: typer.Context,
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o status geral das configurações do Neo em blocos (Git, Tasks, Agents e Serviços)."""
    as_json = is_json_mode(ctx, json_flag)
    statuses = get_all_services_status()

    # 1. Bloco Git
    local_git = _inspect_local_git_status()
    is_git_repo = bool(local_git.get("is_git_repo"))
    git_branch = str(local_git.get("current_branch") or "-") if is_git_repo else "-"

    try:
        git_provider, _ = resolve_git_provider_and_source()
    except (ValueError, KeyError, OSError):
        git_provider = get_default_provider_config() or "github"

    git_ws, _ = resolve_git_workspace_and_source(git_provider)
    git_ws_str = git_ws or "-"
    git_status_str = "Ativo" if is_git_repo else "Inativo"

    # 2. Bloco Tasks
    tasks_service = DEFAULT_TASK_SERVICE
    tasks_configured = bool(statuses.get(tasks_service, {}).get("configured"))
    tasks_status_str = "Configurado" if tasks_configured else "Não configurado"
    tasks_ws_str = git_ws_str

    columns_cfg = get_task_columns_config(service=tasks_service)
    todo_lines: list[str] = []
    if columns_cfg:
        if "todo" in columns_cfg:
            todo_lines.append(
                f"A fazer: {', '.join(columns_cfg['todo']) if columns_cfg['todo'] else '-'}"
            )
        if "doing" in columns_cfg:
            todo_lines.append(
                f"Fazendo: {', '.join(columns_cfg['doing']) if columns_cfg['doing'] else '-'}"
            )
        if "done" in columns_cfg:
            todo_lines.append(
                f"Feito: {', '.join(columns_cfg['done']) if columns_cfg['done'] else '-'}"
            )
    todo_list_display = "\n".join(todo_lines) if todo_lines else "Não configurado"

    task_git, task_full, task_json = _detect_current_task_info(
        git_branch if is_git_repo else None, tasks_configured
    )

    # 3. Bloco Agents
    agent_values = list_agent_config_values()
    agent_cmd = str(agent_values["command"]["value"] or "agy")
    agent_model = agent_values["model"]["value"]
    agent_sdd = str(agent_values["sdd-provider"]["value"] or "spec-driven")
    agent_adapter = str(agent_values["adapter"]["value"] or "antigravity")
    agent_available = shutil.which(agent_cmd) is not None

    agent_data: dict[str, Any] = {
        "adapter": agent_adapter,
        "command": agent_cmd,
        "model": agent_model,
        "sdd_provider": agent_sdd,
        "code_agent": agent_cmd,
        "code_agent_model": agent_model or "-",
        "available": agent_available,
    }

    # 4. Serviços configurados (somente configurados)
    configured_services = [svc for svc, info in statuses.items() if info["configured"]]

    if as_json:
        print_json(
            {
                "config_file": str(DEFAULT_CONFIG_FILE),
                "git": {
                    "status": git_status_str,
                    "provider": git_provider,
                    "workspace": git_ws_str,
                    "branch": git_branch,
                    "tasks": task_git,
                },
                "tasks": {
                    "service": tasks_service,
                    "status": tasks_status_str,
                    "provider": tasks_service,
                    "workspace": tasks_ws_str,
                    "todo_list": columns_cfg or {},
                    "current_task": task_json,
                },
                "agent": agent_data,
                "agents": agent_data,
                "services": [
                    {"service": svc, "status": "Configurado"} for svc in configured_services
                ],
                "all_services": statuses,
            }
        )
        return

    # Tabela 1: Git (Status | Provedor | Workspace | Branch | Tasks)
    git_cols = ["Status", "Provedor", "Workspace", "Branch", "Tasks"]
    git_status_badge = "[bold green]Ativo[/bold green]" if is_git_repo else "[dim]Inativo[/dim]"
    git_rows = [[git_status_badge, git_provider, git_ws_str, git_branch, task_git]]
    print_table("Git", git_cols, git_rows)

    # Tabela 2: Tasks (Status | Provedor | Workspace | To-Do-List | Tarefa atual)
    tasks_cols = ["Status", "Provedor", "Workspace", "To-Do-List", "Tarefa atual"]
    tasks_status_badge = (
        "[bold green]Configurado[/bold green]" if tasks_configured else "[dim]Não configurado[/dim]"
    )
    tasks_rows = [[tasks_status_badge, tasks_service, tasks_ws_str, todo_list_display, task_full]]
    print_table("Tasks", tasks_cols, tasks_rows)

    # Tabela 3: Agents (Code-Agent | Code-Agent-Model)
    agent_cols = ["Code-Agent", "Code-Agent-Model"]
    agent_rows = [[agent_cmd, str(agent_model or "-")]]
    print_table("Agents", agent_cols, agent_rows)

    # Tabela 4: Serviços configurados (Serviço | Status)
    svc_cols = ["Serviço", "Status"]
    svc_rows = [[svc, "[bold green]Configurado[/bold green]"] for svc in configured_services]
    if svc_rows:
        print_table("Serviços configurados", svc_cols, svc_rows)
    else:
        print_panel(
            "Serviços configurados",
            "Nenhum serviço com credencial configurada no momento.",
        )
