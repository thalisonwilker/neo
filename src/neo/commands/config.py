"""Comandos de visão geral e preferências de agente do Neo (`neo config`)."""

from __future__ import annotations

import shutil

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    DEFAULT_CONFIG_FILE,
    DEFAULT_TASK_SERVICE,
    ExitCode,
    get_agent_config_value,
    get_all_services_status,
    get_default_provider_config,
    list_agent_config_values,
    set_agent_config_value,
    unset_agent_config_value,
    validate_agent_config_key,
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


@config_app.command("show")
def config_show(
    ctx: typer.Context,
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o status geral das configurações e credenciais do Neo."""
    as_json = is_json_mode(ctx, json_flag)
    statuses = get_all_services_status()
    default_provider = get_default_provider_config() or "bitbucket"
    tasks_service = DEFAULT_TASK_SERVICE

    git_configured = bool(statuses.get(default_provider, {}).get("configured"))
    tasks_configured = bool(statuses.get(tasks_service, {}).get("configured"))

    agent_values = list_agent_config_values()
    agent_cmd = str(agent_values["command"]["value"] or "agy")
    agent_model = agent_values["model"]["value"]
    agent_sdd = str(agent_values["sdd-provider"]["value"] or "spec-driven")
    agent_adapter = str(agent_values["adapter"]["value"] or "antigravity")
    agent_available = shutil.which(agent_cmd) is not None

    if as_json:
        print_json(
            {
                "config_file": str(DEFAULT_CONFIG_FILE),
                "default_provider": default_provider,
                "default_task_service": tasks_service,
                "git": {
                    "provider": default_provider,
                    "configured": git_configured,
                },
                "tasks": {
                    "service": tasks_service,
                    "configured": tasks_configured,
                },
                "agent": {
                    "adapter": agent_adapter,
                    "command": agent_cmd,
                    "model": agent_model,
                    "sdd_provider": agent_sdd,
                    "available": agent_available,
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

        git_state = (
            "[bold green]Configurado[/bold green]"
            if git_configured
            else "[dim]Não configurado[/dim]"
        )
        tasks_state = (
            "[bold green]Configurado[/bold green]"
            if tasks_configured
            else "[dim]Não configurado[/dim]"
        )
        agent_state = (
            "[bold green]Disponível no PATH[/bold green]"
            if agent_available
            else "[dim]Ausente no PATH[/dim]"
        )
        model_display = (
            f"[cyan]{agent_model}[/cyan]" if agent_model else "[dim]padrão do agente[/dim]"
        )

        print_table("Status de Autenticação do Neo", columns, rows)
        print_panel(
            "Status de Git & Tasks",
            f"[bold]Provedor de Git (git):[/bold] [cyan]{default_provider}[/cyan] ({git_state})\n"
            f"[bold]Gerenciador de Tarefas (tasks):[/bold] [cyan]{tasks_service}[/cyan] ({tasks_state})\n"
            f"[bold]Agente de Codificação (agent):[/bold] [cyan]{agent_adapter}[/cyan] / "
            f"[cyan]{agent_cmd}[/cyan] ({agent_state})\n"
            f"[bold]Modelo do Agente (model):[/bold] {model_display}\n"
            f"[bold]Provedor SDD (sdd-provider):[/bold] [cyan]{agent_sdd}[/cyan]",
        )
