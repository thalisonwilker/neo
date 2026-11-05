"""Comandos de consulta de repositórios Git (`neo git repo`: `list`, `search`, `show`)."""

from __future__ import annotations

from pathlib import Path

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.local_repo import create_repo, edit_repo
from neo.config import ExitCode
from neo.git_context import (
    get_repo_tasks_map,
    list_repos,
    resolve_task_for_repo,
    select_repo,
)
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.resolver import (
    detect_git_remote_info,
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import (
    format_american_date,
    print_error,
    print_json,
    print_panel,
    print_table,
)

repo_app = typer.Typer(
    name="repo",
    help="Gerencia repositórios locais e no GitHub ou Bitbucket Cloud.",
    no_args_is_help=True,
)
repo_app.command("create")(create_repo)
repo_app.command("edit")(edit_repo)


def _execute_repo_list(
    ctx: typer.Context,
    workspace: str | None = None,
    provider: str | None = None,
    limit: int | None = None,
    json_output: bool = False,
) -> None:
    as_json = is_json_mode(ctx, json_output)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        repos = client.list_repositories(workspace=resolved_ws, limit=limit)
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)
    except (httpx.HTTPError, OSError) as e:
        print_error(
            f"Erro de comunicação com o provedor: {e}",
            as_json=as_json,
            code=int(ExitCode.ERROR),
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from e

    tasks_map = get_repo_tasks_map()

    if as_json:
        payload = []
        for r in repos:
            item = r.model_dump()
            item["task"] = resolve_task_for_repo(r.name, repo_slug=r.slug, tasks_map=tasks_map)
            payload.append(item)
        print_json(payload)
    else:
        if not repos:
            print_panel("Repositórios", "Nenhum repositório encontrado no workspace informado.")
            return

        columns = ["Nome", "Data Criação", "Última atualização", "Task"]
        rows: list[list[str]] = []
        for r in repos:
            created = format_american_date(r.created_on)
            updated = format_american_date(r.updated_on)
            task_id = resolve_task_for_repo(r.name, repo_slug=r.slug, tasks_map=tasks_map)
            rows.append([r.name, created, updated, task_id or "-"])

        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        print_table(f"Repositórios no {prov_title}", columns, rows)


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
    """Lista os repositórios do workspace selecionado no provedor Git."""
    _execute_repo_list(
        ctx,
        workspace=workspace,
        provider=provider,
        limit=limit,
        json_output=json_output,
    )


@repo_app.command("remote-list")
def repo_remote_list(
    ctx: typer.Context,
    workspace: str | None = Option(
        None,
        "--workspace",
        help="Slug do workspace ou organização de destino (alias para `list`).",
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
    """Alias de compatibilidade para `neo git repo list`."""
    _execute_repo_list(
        ctx,
        workspace=workspace,
        provider=provider,
        limit=limit,
        json_output=json_output,
    )


@repo_app.command("local-list")
def repo_list_local(
    ctx: typer.Context,
    json_output: bool = Option(False, "--json", help="Emite JSON."),
) -> None:
    """Lista os repositórios locais registrados no Neo."""
    as_json = is_json_mode(ctx, json_output)
    try:
        repos = list_repos()
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc
    if as_json:
        print_json(repos)
    else:
        print_table(
            "Repositórios locais",
            ["Caminho", "Selecionado", "Task"],
            [
                [str(r["path"]), "Sim" if r["selected"] else "Não", str(r["task"] or "-")]
                for r in repos
            ],
        )


@repo_app.command("select")
def repo_select(
    ctx: typer.Context,
    path: Path = Argument(..., help="Caminho do repositório."),  # noqa: B008
) -> None:
    """Registra e seleciona um repositório local."""
    as_json = is_json_mode(ctx)
    try:
        selected = select_repo(path)
    except (ValueError, OSError) as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc
    if as_json:
        print_json({"path": str(selected), "selected": True})
    else:
        print_panel("Repositório selecionado", str(selected))


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
@repo_app.command("get", hidden=True)
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
