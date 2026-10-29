"""Comandos de visão geral e preferências de agente do Neo (`neo config`)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_TASK_SERVICE,
    ExitCode,
    get_agent_config_value,
    get_all_services_status,
    get_credential,
    get_default_provider_config,
    list_agent_config_values,
    set_agent_config_value,
    unset_agent_config_value,
    validate_agent_config_key,
)
from neo.integrations.resolver import (
    detect_git_remote_details,
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)
from neo.integrations.shortcut import ShortcutClient, ShortcutError
from neo.output import print_error, print_json, print_panel, print_success, print_table
from neo.services.active_context import (
    count_task_commits,
    get_current_branch,
    get_git_dir,
    resolve_active_task_id,
)
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


@config_app.command("show")
def config_show(
    ctx: typer.Context,
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o status geral das configurações, demanda ativa e agente do Neo."""
    as_json = is_json_mode(ctx, json_flag)
    statuses = get_all_services_status()
    default_provider = get_default_provider_config() or "bitbucket"
    tasks_service = DEFAULT_TASK_SERVICE

    git_configured = bool(statuses.get(default_provider, {}).get("configured"))
    tasks_configured = bool(statuses.get(tasks_service, {}).get("configured"))

    # 1. Resolução Git
    prov, prov_src = resolve_git_provider_and_source(None)
    ws, ws_src = resolve_git_workspace_and_source(prov, None)
    _rem_prov, _rem_ws, detected_repo = detect_git_remote_details()

    is_git_repo = get_git_dir() is not None
    branch = get_current_branch() if is_git_repo else None
    repo_name = detected_repo or (Path.cwd().name if is_git_repo else None)

    active_task_id = resolve_active_task_id() if is_git_repo else None
    task_commits = count_task_commits(active_task_id) if is_git_repo else 0

    # 2. Resolução Demanda / Task Ativa
    story_title: str | None = None
    if active_task_id is not None:
        try:
            token = get_credential("shortcut")
            if token:
                client = ShortcutClient(token=token)
                story = client.get_story(active_task_id)
                story_title = story.name
        except (ShortcutError, OSError, ConnectionError, ValueError, TimeoutError):
            pass

    active_task_obj = (
        {"id": active_task_id, "title": story_title} if active_task_id is not None else None
    )

    # 3. Resolução Usuário e Workspace de Tasks
    shortcut_user: dict[str, Any] | None = None
    shortcut_user_display = "[dim]Não consultado (offline / não autenticado)[/dim]"
    tasks_workspace = "Shortcut Workspace"
    if tasks_configured:
        try:
            token = get_credential("shortcut")
            if token:
                client = ShortcutClient(token=token)
                member = client.get_current_member()
                shortcut_user = {
                    "name": member.name,
                    "mention_name": member.mention_name,
                    "email": member.email_address,
                }
                mention = f" (@{member.mention_name})" if member.mention_name else ""
                shortcut_user_display = f"[cyan]{member.name}{mention}[/cyan]"
        except (ShortcutError, OSError, ConnectionError, ValueError, TimeoutError):
            shortcut_user_display = "[dim]Conectado (offline / perfil não consultado)[/dim]"

    tasks_status_label = "Configurado" if tasks_configured else "Não configurado"

    # 4. Resolução Agente
    agent_values = list_agent_config_values()
    agent_cmd = str(agent_values["command"]["value"] or "agy")
    agent_model = agent_values["model"]["value"]
    agent_sdd = str(agent_values["sdd-provider"]["value"] or "spec-driven")
    agent_adapter = str(agent_values["adapter"]["value"] or "antigravity")

    agent_version: str | None = None
    agent_available = False
    try:
        check = validate_agent_executable(agent_cmd, adapter=agent_adapter, timeout=2.0)
        agent_available = True
        agent_version = check.get("version")
    except (AgentValidationError, OSError, ValueError):
        agent_available = shutil.which(agent_cmd) is not None

    usage_percent = 40
    filled_blocks = round(usage_percent / 100 * 20)
    bar_str = "█" * filled_blocks + "░" * (20 - filled_blocks)
    usage_display = f"[{bar_str}] {usage_percent}%"
    usage_obj = {"percent": usage_percent, "display": usage_display}

    if as_json:
        print_json(
            {
                "config_file": str(DEFAULT_CONFIG_FILE),
                "default_provider": default_provider,
                "default_task_service": tasks_service,
                "git": {
                    "provider": prov,
                    "provider_source": prov_src,
                    "configured": git_configured,
                    "workspace": ws,
                    "repo": repo_name,
                    "branch": branch,
                    "active_task": active_task_obj,
                },
                "tasks": {
                    "service": tasks_service,
                    "status": tasks_status_label,
                    "configured": tasks_configured,
                    "user": shortcut_user,
                    "workspace": tasks_workspace,
                    "active_repo": repo_name,
                    "task_commits": task_commits,
                },
                "agent": {
                    "adapter": agent_adapter,
                    "command": agent_cmd,
                    "model": agent_model,
                    "sdd_provider": agent_sdd,
                    "available": agent_available,
                    "version": agent_version,
                    "usage": usage_obj,
                    "roles": ["code", "refine", "review-pr", "review-task"],
                },
                "services": statuses,
            }
        )
    else:
        columns = ["Serviço", "Status", "Origem", "Token Mascarado"]
        rows: list[list[str]] = []
        for svc, info in statuses.items():
            status_str = (
                "[bold green]Configurado[/bold green]"
                if info["configured"]
                else "[dim]Não configurado[/dim]"
            )
            source_str = str(info["source"]) if info["source"] else "-"
            token_str = str(info["masked_token"]) if info["masked_token"] else "-"
            rows.append([svc, status_str, source_str, token_str])

        print_table("Status de Autenticação do Neo", columns, rows)

        # Painel 1: GIT
        repo_line = (
            f"[cyan]{repo_name}[/cyan]"
            if repo_name
            else "[dim]Não detectado (fora de repositório Git)[/dim]"
        )
        branch_line = (
            f"[cyan]{branch}[/cyan]"
            if branch
            else "[dim]Não detectado (fora de repositório Git)[/dim]"
        )
        if active_task_id is not None:
            task_suffix = f" — {story_title}" if story_title else ""
            task_line = f"[bold green]#{active_task_id}[/bold green]{task_suffix}"
        else:
            task_line = "[dim]Nenhuma vinculada[/dim]"
        ws_display = f"[cyan]{ws}[/cyan] ({ws_src})" if ws else "[dim]-[/dim]"

        print_panel(
            "GIT : STATUS CONFIGURAÇÃO",
            f"[bold]PROVEDOR:[/bold] [cyan]{prov}[/cyan] ({prov_src})\n"
            f"[bold]WORKSPACE:[/bold] {ws_display}\n"
            f"[bold]REPOSITÓRIO:[/bold] {repo_line}\n"
            f"[bold]BRANCH:[/bold] {branch_line}\n"
            f"[bold]TASK ATIVA:[/bold] {task_line}",
            border_style="cyan",
        )

        # Painel 2: TASKS
        tasks_status_colored = (
            "[bold green]Configurado[/bold green]"
            if tasks_configured
            else "[dim]Não configurado[/dim]"
        )
        active_repo_line = (
            f"[cyan]{repo_name}[/cyan]"
            if repo_name
            else "[dim]Não detectado (fora de repositório Git)[/dim]"
        )
        print_panel(
            "TASKS : DEMANDA ATIVA",
            f"[bold]PROVEDOR:[/bold] [cyan]Shortcut (API v3)[/cyan]\n"
            f"[bold]STATUS:[/bold] {tasks_status_colored}\n"
            f"[bold]USUÁRIO:[/bold] {shortcut_user_display}\n"
            f"[bold]WORKSPACE:[/bold] [cyan]{tasks_workspace}[/cyan]\n"
            f"[bold]REPOSITÓRIO ATIVO:[/bold] {active_repo_line}\n"
            f"[bold]COMMITS NA TASK:[/bold] [bold green]{task_commits}[/bold green] commit(s)",
            border_style="magenta",
        )

        # Painel 3: AGENT
        ver_suffix = f" ({agent_version})" if agent_version else ""
        agent_status_colored = (
            f"[bold green]Disponível no PATH[/bold green]{ver_suffix}"
            if agent_available
            else "[dim]Ausente no PATH[/dim]"
        )
        model_line = f"[cyan]{agent_model}[/cyan]" if agent_model else "[dim]padrão do agente[/dim]"
        print_panel(
            "AGENT : AGENTES & SDD",
            f"[bold]PROVEDOR:[/bold] [cyan]{agent_adapter} / {agent_cmd}[/cyan]\n"
            f"[bold]STATUS:[/bold] {agent_status_colored}\n"
            f"[bold]MODELO:[/bold] {model_line}\n"
            f"[bold]PAPÉIS:[/bold] [cyan]code, refine, review-pr, review-task[/cyan]\n"
            f"[bold]USAGE:[/bold] [green]{usage_display}[/green]\n"
            f"[bold]PROVEDOR SDD:[/bold] [cyan]{agent_sdd}[/cyan]",
            border_style="green",
        )
