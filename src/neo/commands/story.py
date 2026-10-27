"""Comandos de consulta e análise de stories no Shortcut (`neo story`)."""

from __future__ import annotations

import typer
from rich.markup import escape
from typer import Argument, Option

from neo.config import get_credential
from neo.integrations.shortcut import (
    ShortcutClient,
    ShortcutError,
    ShortcutNotFoundError,
)
from neo.output import print_error, print_json, print_panel, print_table

story_app = typer.Typer(
    name="story",
    help="Consulta e análise de stories e demandas no Shortcut (API v3).",
    no_args_is_help=True,
)


def _get_shortcut_client(as_json: bool) -> ShortcutClient:
    token = get_credential("shortcut")
    if not token:
        msg = "Credenciais do Shortcut não configuradas. Execute `neo config auth set shortcut`."
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)
    return ShortcutClient(token=token)


@story_app.command("whoami")
def story_whoami(ctx: typer.Context) -> None:
    """Verifica e exibe o membro autenticado na API do Shortcut."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_shortcut_client(as_json)

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


@story_app.command("list")
def story_list(
    ctx: typer.Context,
    mine: bool = Option(False, "--mine", "-m", help="Filtra apenas stories atribuídas a você."),
) -> None:
    """Lista stories ativas no workspace do Shortcut."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_shortcut_client(as_json)

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
        stories = client.list_stories(owner_id=owner_id)
    except ShortcutError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json([s.model_dump() for s in stories])
    else:
        if not stories:
            print_panel("Stories", "Nenhuma story ativa encontrada.")
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

        title = "Minhas Stories no Shortcut" if mine else "Stories Ativas no Shortcut"
        print_table(title, columns, rows)


@story_app.command("search")
def story_search(
    ctx: typer.Context,
    query: str = Argument(..., help="Termo de busca para pesquisar stories."),
) -> None:
    """Pesquisa stories por palavra-chave ou texto."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_shortcut_client(as_json)

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


@story_app.command("show")
def story_show(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID numérico da story no Shortcut."),
) -> None:
    """Exibe detalhes completos de uma story pelo ID."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_shortcut_client(as_json)

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
        content = (
            f"[bold]Tipo:[/bold] {story.story_type.upper()}\n"
            f"[bold]Labels:[/bold] {labels_str}\n"
            f"[bold]URL Web:[/bold] [cyan]{app_url}[/cyan]\n\n"
            f"[bold]Descrição:[/bold]\n{desc}"
        )
        print_panel(f"Story #{story.id}: {story.name}", content)


@story_app.command("analyze")
def story_analyze(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story a ser analisada."),
) -> None:
    """Analisa o contexto da story sugerindo branch git, prefixos e palavras-chave."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_shortcut_client(as_json)

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
