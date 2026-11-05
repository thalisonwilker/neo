"""Ação de agent."""

from __future__ import annotations

from pathlib import Path

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.agent import _common as common
from neo.config import (
    ExitCode,
)
from neo.integrations.sdd.adapters import (
    inspect_project_sdd,
)
from neo.output import print_error, print_json, print_panel
from neo.services.agent_validator import AgentValidationError, validate_agent_executable


def agent_status(
    ctx: typer.Context,
    directory: str = Option(".", "--dir", help="Diretório do projeto a inspecionar."),
    json_flag: bool = Option(
        False, "--json", help="Emite o diagnóstico estruturado em formato JSON puro no stdout."
    ),
) -> None:
    """Diagnostica disponibilidade do executável, versão, modelo, provedor SDD e arquivos do projeto."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        runtime = common.resolve_agent_runtime()
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
            {"component": "command", "message": exc.raw_message, "suggestion": exc.suggestion or ""}
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
        f"[bold]AGENTS.md:[/bold] {('presente' if sdd_info['agents_md_exists'] else 'ausente')}",
        f"[bold]Skills descobertas:[/bold] {skills_list}",
    ]
    if issues:
        lines.append("\n[bold yellow]Orientações de Correção:[/bold yellow]")
        for issue in issues:
            lines.append(f"• {issue['message']}")
            if issue["suggestion"]:
                lines.append(f"  [dim]→ {issue['suggestion']}[/dim]")
    print_panel("Agente & SDD", "\n".join(lines))
