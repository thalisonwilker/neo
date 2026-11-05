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
from neo.integrations.agents.antigravity import (
    UnsupportedAgentCombinationError,
)
from neo.integrations.sdd.adapters import (
    apply_sdd_setup,
    plan_sdd_setup,
)
from neo.output import console, print_error, print_json, print_success


def agent_setup(
    ctx: typer.Context,
    sdd_provider: str | None = Option(
        None, "--sdd-provider", help="Provedor SDD para preparação (spec-driven ou spec-kit)."
    ),
    agent: str | None = Option(
        None, "--agent", help="Identidade do adaptador do agente (padrão: antigravity)."
    ),
    directory: str = Option(
        ".", "--dir", help="Diretório alvo onde as instruções e skills serão preparadas."
    ),
    yes: bool = Option(
        False, "--yes", help="Confirma a criação dos arquivos ausentes sem prompt interativo."
    ),
    json_flag: bool = Option(
        False, "--json", help="Emite o resultado da preparação em JSON puro no stdout."
    ),
) -> None:
    """Prepara de forma idempotente as instruções e skills do provedor SDD no diretório alvo."""
    as_json = is_json_mode(ctx, json_flag)
    try:
        runtime = common.resolve_agent_runtime(agent_arg=agent, sdd_provider_arg=sdd_provider)
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
    if plan.files_to_create and (not yes) and (not as_json):
        rel_to_create = [str(p.relative_to(plan.target_dir)) for p in plan.files_to_create]
        console.print(
            f"[bold cyan]Provedor SDD:[/bold cyan] {plan.provider} (agente: {plan.adapter})\n[bold]Arquivos a criar em {plan.target_dir}:[/bold]"
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
            f"Integração SDD ([bold]{result['provider']}[/bold]) pronta em [cyan]{result['target_dir']}[/cyan] ({created_count} arquivo(s) criado(s), {preserved_count} preservado(s))."
        )
