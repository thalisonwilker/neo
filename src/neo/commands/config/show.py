"""Ação de config."""

from __future__ import annotations

import shutil
from typing import Any

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.config import _common as common
from neo.commands.git import _inspect_local_git_status
from neo.config import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_TASK_SERVICE,
    get_all_services_status,
    get_default_provider_config,
    get_task_columns_config,
    list_agent_config_values,
)
from neo.integrations.git.resolver import (
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)
from neo.output import print_json, print_panel, print_table


def config_show(
    ctx: typer.Context,
    json_flag: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Exibe o status geral das configurações do Neo em blocos (Git, Tasks, Agents e Serviços)."""
    as_json = is_json_mode(ctx, json_flag)
    statuses = get_all_services_status()
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
    tasks_service = DEFAULT_TASK_SERVICE
    tasks_configured = bool(statuses.get(tasks_service, {}).get("configured"))
    tasks_status_str = "Configurado" if tasks_configured else "Não configurado"
    tasks_ws_str = git_ws_str
    columns_cfg = get_task_columns_config(service=tasks_service)
    todo_lines: list[str] = []
    if columns_cfg:
        if "todo" in columns_cfg:
            todo_lines.append(
                f"A fazer: {(', '.join(columns_cfg['todo']) if columns_cfg['todo'] else '-')}"
            )
        if "doing" in columns_cfg:
            todo_lines.append(
                f"Fazendo: {(', '.join(columns_cfg['doing']) if columns_cfg['doing'] else '-')}"
            )
        if "done" in columns_cfg:
            todo_lines.append(
                f"Feito: {(', '.join(columns_cfg['done']) if columns_cfg['done'] else '-')}"
            )
    todo_list_display = "\n".join(todo_lines) if todo_lines else "Não configurado"
    task_git, task_full, task_json = common._detect_current_task_info(
        git_branch if is_git_repo else None, tasks_configured
    )
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
    git_cols = ["Status", "Provedor", "Workspace", "Branch", "Tasks"]
    git_status_badge = "[bold green]Ativo[/bold green]" if is_git_repo else "[dim]Inativo[/dim]"
    git_rows = [[git_status_badge, git_provider, git_ws_str, git_branch, task_git]]
    print_table("Git", git_cols, git_rows)
    tasks_cols = ["Status", "Provedor", "Workspace", "To-Do-List", "Tarefa atual"]
    tasks_status_badge = (
        "[bold green]Configurado[/bold green]" if tasks_configured else "[dim]Não configurado[/dim]"
    )
    tasks_rows = [[tasks_status_badge, tasks_service, tasks_ws_str, todo_list_display, task_full]]
    print_table("Tasks", tasks_cols, tasks_rows)
    agent_cols = ["Code-Agent", "Code-Agent-Model"]
    agent_rows = [[agent_cmd, str(agent_model or "-")]]
    print_table("Agents", agent_cols, agent_rows)
    svc_cols = ["Serviço", "Status"]
    svc_rows = [[svc, "[bold green]Configurado[/bold green]"] for svc in configured_services]
    if svc_rows:
        print_table("Serviços configurados", svc_cols, svc_rows)
    else:
        print_panel(
            "Serviços configurados", "Nenhum serviço com credencial configurada no momento."
        )
