"""Comandos operacionais do módulo de agente de codificação (`neo agent`)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    ExitCode,
    get_agent_config_value,
    validate_agent_adapter,
    validate_sdd_provider,
)
from neo.integrations.agents.antigravity import (
    AntigravityAdapter,
    UnsupportedAgentCombinationError,
)
from neo.integrations.sdd.adapters import (
    apply_sdd_setup,
    inspect_project_sdd,
    plan_sdd_setup,
)
from neo.output import console, print_error, print_json, print_panel, print_success
from neo.services.agent_validator import AgentValidationError, validate_agent_executable

agent_app = typer.Typer(
    name="agent",
    help="Diagnóstico, preparação SDD e execução do agente de codificação (Antigravity CLI).",
    no_args_is_help=True,
)


def resolve_agent_runtime(
    *,
    agent_arg: str | None = None,
    command_arg: str | None = None,
    model_arg: str | None = None,
    sdd_provider_arg: str | None = None,
) -> dict[str, Any]:
    """Resolve parâmetros efetivos do agente respeitando `CLI > ENV > config.toml > default` sem mutar config."""
    _, cfg_adapter, adapter_src = get_agent_config_value("adapter")
    _, cfg_command, command_src = get_agent_config_value("command")
    _, cfg_model, model_src = get_agent_config_value("model")
    _, cfg_sdd, sdd_src = get_agent_config_value("sdd-provider")

    adapter = (
        agent_arg.strip() if agent_arg and agent_arg.strip() else (cfg_adapter or "antigravity")
    )
    adapter_source = "cli" if (agent_arg and agent_arg.strip()) else adapter_src

    command = command_arg.strip() if command_arg and command_arg.strip() else (cfg_command or "agy")
    command_source = "cli" if (command_arg and command_arg.strip()) else command_src

    model = model_arg.strip() if model_arg and model_arg.strip() else cfg_model
    model_source = "cli" if (model_arg and model_arg.strip()) else model_src

    sdd_provider = (
        sdd_provider_arg.strip()
        if sdd_provider_arg and sdd_provider_arg.strip()
        else (cfg_sdd or "spec-driven")
    )
    sdd_source = "cli" if (sdd_provider_arg and sdd_provider_arg.strip()) else sdd_src

    return {
        "adapter": adapter,
        "adapter_source": adapter_source,
        "command": command,
        "command_source": command_source,
        "model": model,
        "model_source": model_source,
        "sdd_provider": sdd_provider,
        "sdd_source": sdd_source,
    }


@agent_app.command("status")
def agent_status(
    ctx: typer.Context,
    directory: str = Option(
        ".",
        "--dir",
        help="Diretório do projeto a inspecionar.",
    ),
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite o diagnóstico estruturado em formato JSON puro no stdout.",
    ),
) -> None:
    """Diagnostica disponibilidade do executável, versão, modelo, provedor SDD e arquivos do projeto."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        runtime = resolve_agent_runtime()
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    adapter = runtime["adapter"]
    command = runtime["command"]
    model = runtime["model"]
    sdd_provider = runtime["sdd_provider"]

    executable_ok = False
    resolved_path: str | None = None
    version_str: str | None = None
    issues: list[dict[str, str]] = []

    try:
        check = validate_agent_executable(command, adapter=adapter, timeout=3.0)
        executable_ok = True
        resolved_path = check["resolved_path"]
        version_str = check["version"]
    except AgentValidationError as exc:
        issues.append(
            {
                "component": "command",
                "message": exc.raw_message,
                "suggestion": exc.suggestion or "",
            }
        )

    sdd_info = inspect_project_sdd(Path(directory), sdd_provider)
    if not sdd_info["ready"]:
        issues.append(
            {
                "component": "sdd",
                "message": f"Artefatos da esteira '{sdd_provider}' ainda não estão prontos em {sdd_info['target_dir']}.",
                "suggestion": f"Execute `neo agent setup --sdd-provider {sdd_provider}` para preparar instruções e skills.",
            }
        )

    payload = {
        "adapter": adapter,
        "adapter_source": runtime["adapter_source"],
        "command": command,
        "command_source": runtime["command_source"],
        "executable_available": executable_ok,
        "resolved_path": resolved_path,
        "version": version_str,
        "model": model,
        "model_source": runtime["model_source"],
        "sdd_provider": sdd_provider,
        "sdd_source": runtime["sdd_source"],
        "project": sdd_info,
        "issues": issues,
    }

    if as_json:
        print_json(payload)
        return

    cmd_status = (
        f"[bold green]Disponível[/bold green] ({resolved_path} — {version_str})"
        if executable_ok
        else "[bold red]Indisponível[/bold red]"
    )
    model_str = (
        f"[cyan]{model}[/cyan] ({runtime['model_source']})"
        if model
        else "[dim]padrão do agente[/dim]"
    )
    sdd_state = (
        "[bold green]Pronto[/bold green]"
        if sdd_info["ready"]
        else "[yellow]Pendente de setup[/yellow]"
    )
    skills_list = (
        ", ".join(sdd_info["discovered_skills"]) if sdd_info["discovered_skills"] else "nenhuma"
    )

    lines = [
        f"[bold]Adaptador:[/bold] [cyan]{adapter}[/cyan] ({runtime['adapter_source']})",
        f"[bold]Executável:[/bold] [cyan]{command}[/cyan] ({runtime['command_source']}) — {cmd_status}",
        f"[bold]Modelo:[/bold] {model_str}",
        f"[bold]Provedor SDD:[/bold] [cyan]{sdd_provider}[/cyan] ({runtime['sdd_source']}) — {sdd_state}",
        f"[bold]Diretório:[/bold] {sdd_info['target_dir']}",
        f"[bold]AGENTS.md:[/bold] {'presente' if sdd_info['agents_md_exists'] else 'ausente'}",
        f"[bold]Skills descobertas:[/bold] {skills_list}",
    ]
    if issues:
        lines.append("\n[bold yellow]Orientações de Correção:[/bold yellow]")
        for issue in issues:
            lines.append(f"• {issue['message']}")
            if issue["suggestion"]:
                lines.append(f"  [dim]→ {issue['suggestion']}[/dim]")

    print_panel("Diagnóstico do Agente & SDD", "\n".join(lines))


@agent_app.command("setup")
def agent_setup(
    ctx: typer.Context,
    sdd_provider: str | None = Option(
        None,
        "--sdd-provider",
        help="Provedor SDD para preparação (spec-driven ou spec-kit).",
    ),
    agent: str | None = Option(
        None,
        "--agent",
        help="Identidade do adaptador do agente (padrão: antigravity).",
    ),
    directory: str = Option(
        ".",
        "--dir",
        help="Diretório alvo onde as instruções e skills serão preparadas.",
    ),
    yes: bool = Option(
        False,
        "--yes",
        help="Confirma a criação dos arquivos ausentes sem prompt interativo.",
    ),
    json_flag: bool = Option(
        False,
        "--json",
        help="Emite o resultado da preparação em JSON puro no stdout.",
    ),
) -> None:
    """Prepara de forma idempotente as instruções e skills do provedor SDD no diretório alvo."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        runtime = resolve_agent_runtime(agent_arg=agent, sdd_provider_arg=sdd_provider)
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    eff_adapter = runtime["adapter"]
    eff_sdd = runtime["sdd_provider"]

    try:
        plan = plan_sdd_setup(Path(directory), eff_sdd, adapter=eff_adapter)
    except UnsupportedAgentCombinationError as exc:
        print_error(str(exc), as_json=as_json, code=exc.exit_code)
        raise typer.Exit(code=exc.exit_code) from exc
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    if plan.files_to_create and not yes and not as_json:
        rel_to_create = [str(p.relative_to(plan.target_dir)) for p in plan.files_to_create]
        console.print(
            f"[bold cyan]Provedor SDD:[/bold cyan] {plan.provider} (agente: {plan.adapter})\n"
            f"[bold]Arquivos a criar em {plan.target_dir}:[/bold]"
        )
        for item in rel_to_create:
            console.print(f"  + {item}")
        if plan.files_preserved:
            console.print("[dim]Arquivos existentes preservados intactos:[/dim]")
            for p in plan.files_preserved:
                console.print(f"  = {p.relative_to(plan.target_dir)}")

        confirmed = typer.confirm("Deseja aplicar a preparação SDD neste diretório?")
        if not confirmed:
            console.print("[yellow]Operação cancelada pelo usuário.[/yellow]")
            raise typer.Exit(code=int(ExitCode.SUCCESS))

    result = apply_sdd_setup(plan)

    if as_json:
        print_json(result)
    else:
        created_count = len(result["created_files"])
        preserved_count = len(result["preserved_files"])
        print_success(
            f"Integração SDD ([bold]{result['provider']}[/bold]) pronta em [cyan]{result['target_dir']}[/cyan] "
            f"({created_count} arquivo(s) criado(s), {preserved_count} preservado(s))."
        )


@agent_app.command("run")
def agent_run(
    ctx: typer.Context,
    agent: str | None = Option(
        None,
        "--agent",
        help="Identidade do adaptador do agente apenas para esta execução (ex.: antigravity).",
    ),
    command: str | None = Option(
        None,
        "--command",
        help="Executável do agente apenas para esta execução (ex.: agy).",
    ),
    model: str | None = Option(
        None,
        "--model",
        help="Identificador do modelo encaminhado ao agente apenas para esta execução.",
    ),
    sdd_provider: str | None = Option(
        None,
        "--sdd-provider",
        help="Provedor SDD considerado apenas para esta execução (spec-driven ou spec-kit).",
    ),
    directory: str = Option(
        ".",
        "--dir",
        help="Diretório de trabalho onde a sessão do agente será iniciada.",
    ),
) -> None:
    """Inicia uma sessão interativa do agente no diretório escolhido com overrides locais."""
    if is_json_mode(ctx):
        print_error(
            "O comando `neo agent run` inicia uma sessão interativa de terminal e não suporta `--json`.",
            as_json=True,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    try:
        runtime = resolve_agent_runtime(
            agent_arg=agent,
            command_arg=command,
            model_arg=model,
            sdd_provider_arg=sdd_provider,
        )
    except ValueError as exc:
        print_error(str(exc), as_json=False, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    eff_adapter = runtime["adapter"]
    eff_command = runtime["command"]
    eff_model = runtime["model"]
    eff_sdd = runtime["sdd_provider"]

    # 1. Valida compatibilidade da combinação agente × provedor SDD antes de iniciar
    try:
        AntigravityAdapter.validate_compatibility(eff_adapter, eff_sdd)
        validate_agent_adapter(eff_adapter)
        validate_sdd_provider(eff_sdd)
    except UnsupportedAgentCombinationError as exc:
        print_error(str(exc), as_json=False, code=exc.exit_code)
        raise typer.Exit(code=exc.exit_code) from exc
    except ValueError as exc:
        print_error(str(exc), as_json=False, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    # 2. Valida diretório de trabalho
    target_dir = Path(directory).expanduser().resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        print_error(
            f"Diretório de trabalho não encontrado: '{directory}'.",
            as_json=False,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    # 3. Revalida o executável antes da execução (usa código 4 se ausente no PATH)
    try:
        check = validate_agent_executable(
            eff_command,
            adapter=eff_adapter,
            timeout=3.0,
            not_found_exit_code=int(ExitCode.NOT_FOUND),
        )
    except AgentValidationError as exc:
        print_error(str(exc), as_json=False, code=exc.exit_code)
        raise typer.Exit(code=exc.exit_code) from exc

    # 4. Constrói argumentos estruturados e inicia sessão interativa
    args = AntigravityAdapter.build_run_args(check["resolved_path"], model=eff_model)
    return_code = AntigravityAdapter.run_interactive_session(args, cwd=target_dir)
    if return_code != 0:
        raise typer.Exit(code=return_code)
