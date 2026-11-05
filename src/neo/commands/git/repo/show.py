"""Ação de repositório Git."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    detect_git_remote_info,
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import (
    print_error,
    print_json,
    print_panel,
)


def repo_show(
    ctx: typer.Context,
    slug: str | None = Argument(
        None,
        help="Slug do repositório (ou informe via --repo ou auto-detecte pelo diretório Git local).",
    ),
    repo: str | None = Option(None, "--repo", help="Slug do repositório a inspecionar."),
    workspace: str | None = Option(
        None, "--workspace", help="Slug do workspace ou organização de destino."
    ),
    provider: str | None = Option(
        None, "--provider", help="Provedor Git: 'github' ou 'bitbucket'."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Exibe os detalhes completos de um repositório."""
    as_json = is_json_mode(ctx, json_output)
    target_repo = (repo or slug or detect_git_remote_info()[1] or "").strip()
    if not target_repo:
        print_error(
            "Repositório não informado e não foi possível detectar pelo Git local. Use `--repo <slug>` para especificar o repositório.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)
    try:
        repo_obj = client.get_repository(repo_slug=target_repo, workspace=resolved_ws)
    except GitProviderError as e:
        handle_git_provider_error(e, as_json=as_json)
    if as_json:
        payload = repo_obj.model_dump()
        payload["ssh_clone_url"] = repo_obj.ssh_clone_url
        payload["https_clone_url"] = repo_obj.https_clone_url
        payload["provider"] = prov_name
        print_json(payload)
    else:
        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        vis_str = "[red]Privado[/red]" if repo_obj.is_private else "[green]Público[/green]"
        updated = (
            repo_obj.updated_on.split("T")[0]
            if "T" in repo_obj.updated_on
            else repo_obj.updated_on or "-"
        )
        print_panel(
            f"Repositório: {repo_obj.name} ({prov_title})",
            f"[bold]Nome:[/bold] {repo_obj.name}\n[bold]Slug:[/bold] [cyan]{repo_obj.slug}[/cyan]\n[bold]Workspace:[/bold] {repo_obj.workspace or resolved_ws or '-'}\n[bold]Visibilidade:[/bold] {vis_str}\n[bold]Branch Padrão:[/bold] [cyan]{repo_obj.main_branch}[/cyan]\n[bold]Descrição:[/bold] {repo_obj.description or '-'}\n[bold]Clone SSH:[/bold] {repo_obj.ssh_clone_url or '-'}\n[bold]Clone HTTPS:[/bold] {repo_obj.https_clone_url or '-'}\n[bold]Atualizado em:[/bold] {updated}",
        )
