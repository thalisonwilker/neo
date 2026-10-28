"""Comandos de consulta de repositórios Git (`neo git repo`: `list`, `search`, `show`)."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.resolver import (
    detect_git_remote_info,
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_json, print_panel, print_table

repo_app = typer.Typer(
    name="repo",
    help="Lista, pesquisa e exibe detalhes de repositórios no GitHub e Bitbucket Cloud (list, search, show).",
    no_args_is_help=True,
)


@repo_app.command("list")
def repo_list(
    ctx: typer.Context,
    workspace: str | None = Option(
        None,
        "--workspace",
        help="Slug do workspace ou organização de destino.",
    ),
    provider: str | None = Option(
        None,
        "--provider",
        help="Provedor Git: 'github' ou 'bitbucket'.",
    ),
    limit: int | None = Option(
        None,
        "--limit",
        help="Quantidade máxima de repositórios a retornar.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Lista os repositórios disponíveis no workspace ativo."""
    as_json = is_json_mode(ctx, json_output)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        repos = client.list_repositories(workspace=resolved_ws, limit=limit)
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    if as_json:
        print_json([r.model_dump() for r in repos])
    else:
        if not repos:
            print_panel("Repositórios", "Nenhum repositório encontrado no workspace informado.")
            return

        columns = ["Nome", "Slug", "Visibilidade", "Branch Padrão", "Atualizado em"]
        rows: list[list[str]] = []
        for r in repos:
            vis = "[red]Privado[/red]" if r.is_private else "[green]Público[/green]"
            updated = r.updated_on.split("T")[0] if "T" in r.updated_on else r.updated_on
            rows.append([r.name, r.slug, vis, r.main_branch, updated])

        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        print_table(f"Repositórios no {prov_title}", columns, rows)


@repo_app.command("search")
def repo_search(
    ctx: typer.Context,
    query: str | None = Option(
        None,
        "--query",
        help="Termo de pesquisa (nome, slug ou descrição do repositório).",
    ),
    workspace: str | None = Option(
        None,
        "--workspace",
        help="Slug do workspace ou organização de destino.",
    ),
    provider: str | None = Option(
        None,
        "--provider",
        help="Provedor Git: 'github' ou 'bitbucket'.",
    ),
    limit: int | None = Option(
        None,
        "--limit",
        help="Quantidade máxima de repositórios a retornar.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Pesquisa repositórios por nome, slug ou descrição usando --query."""
    as_json = is_json_mode(ctx, json_output)
    if not query or not query.strip():
        print_error(
            "A opção `--query <termo>` é obrigatória em `neo git repo search`.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        repos = client.search_repositories(query=query, workspace=resolved_ws, limit=limit)
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    if as_json:
        print_json([r.model_dump() for r in repos])
    else:
        if not repos:
            print_panel(
                f"Busca: '{query}'", "Nenhum repositório encontrado para o termo pesquisado."
            )
            return

        columns = ["Nome", "Slug", "Visibilidade", "Descrição"]
        rows: list[list[str]] = []
        for r in repos:
            vis = "[red]Privado[/red]" if r.is_private else "[green]Público[/green]"
            desc = r.description or "-"
            rows.append([r.name, r.slug, vis, desc])

        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        print_table(f"Repositórios no {prov_title} encontrados para '{query}'", columns, rows)


@repo_app.command("show")
def repo_show(
    ctx: typer.Context,
    slug: str | None = Argument(
        None,
        help="Slug do repositório (ou informe via --repo ou auto-detecte pelo diretório Git local).",
    ),
    repo: str | None = Option(
        None,
        "--repo",
        help="Slug do repositório a inspecionar.",
    ),
    workspace: str | None = Option(
        None,
        "--workspace",
        help="Slug do workspace ou organização de destino.",
    ),
    provider: str | None = Option(
        None,
        "--provider",
        help="Provedor Git: 'github' ou 'bitbucket'.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe os detalhes completos de um repositório."""
    as_json = is_json_mode(ctx, json_output)
    target_repo = (repo or slug or detect_git_remote_info()[1] or "").strip()
    if not target_repo:
        print_error(
            "Repositório não informado e não foi possível detectar pelo Git local. "
            "Use `--repo <slug>` para especificar o repositório.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        repo_obj = client.get_repository(repo_slug=target_repo, workspace=resolved_ws)
    except BitbucketError as e:
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
            else (repo_obj.updated_on or "-")
        )
        print_panel(
            f"Repositório: {repo_obj.name} ({prov_title})",
            f"[bold]Nome:[/bold] {repo_obj.name}\n"
            f"[bold]Slug:[/bold] [cyan]{repo_obj.slug}[/cyan]\n"
            f"[bold]Workspace:[/bold] {repo_obj.workspace or resolved_ws or '-'}\n"
            f"[bold]Visibilidade:[/bold] {vis_str}\n"
            f"[bold]Branch Padrão:[/bold] [cyan]{repo_obj.main_branch}[/cyan]\n"
            f"[bold]Descrição:[/bold] {repo_obj.description or '-'}\n"
            f"[bold]Clone SSH:[/bold] {repo_obj.ssh_clone_url or '-'}\n"
            f"[bold]Clone HTTPS:[/bold] {repo_obj.https_clone_url or '-'}\n"
            f"[bold]Atualizado em:[/bold] {updated}",
        )


# Bloqueios orientativos para comandos movidos para o backlog planejado
@repo_app.command(
    "clone",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_repo_clone(ctx: typer.Context) -> None:
    as_json = is_json_mode(ctx)
    print_error(
        "O comando `neo git repo clone` está no backlog planejado desta versão. "
        "Use `neo git repo show --repo <slug>` para consultar as URLs de clone.",
        as_json=as_json,
        code=int(ExitCode.USAGE_ERROR),
    )
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))


@repo_app.command(
    "create",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_repo_create(ctx: typer.Context) -> None:
    as_json = is_json_mode(ctx)
    print_error(
        "O comando `neo git repo create` está no backlog planejado desta versão.",
        as_json=as_json,
        code=int(ExitCode.USAGE_ERROR),
    )
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
