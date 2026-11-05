"""Ação de tarefas."""

from __future__ import annotations

import typer
from rich.markup import escape
from typer import Argument

from neo.commands.tasks import _common as common
from neo.output import print_error, print_json, print_panel
from neo.services.tasks.errors import TaskProviderError, TaskProviderNotFoundError


def tasks_analyze(
    ctx: typer.Context,
    service: str = common._service_option(),
    story_id: int = Argument(..., help="ID da story a ser analisada."),
) -> None:
    """Analisa o contexto da story sugerindo branch git, prefixos e palavras-chave."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = common._get_client(service, as_json)
    try:
        analysis = client.analyze_story(story_id)
    except TaskProviderNotFoundError as e:
        print_error(f"Story #{story_id} não encontrada para análise: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except TaskProviderError as e:
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
        content = f"[bold]Título:[/bold] {analysis.title}\n[bold]Branch Recomendada:[/bold] [cyan]{analysis.suggested_branch}[/cyan]\n[bold]Prefixo de Commit:[/bold] [yellow]{escape(analysis.commit_prefix)}[/yellow]\n[bold]Possui Bloqueios?:[/bold] {blocker_badge}\n[bold]Palavras-chave de Busca:[/bold] {kw_str}{criteria_text}"
        print_panel(f"Análise de Contexto: Story #{analysis.story_id}", content)
