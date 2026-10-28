"""Comandos de consulta e histórico de commits Git (`neo git commits`: `list`, `search`, `show`)."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.bitbucket_models import BitbucketCommit
from neo.integrations.resolver import (
    detect_git_remote_info,
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_json, print_panel, print_table

commits_app = typer.Typer(
    name="commits",
    help="Lista, pesquisa e inspeciona commits no GitHub e Bitbucket Cloud (list, search, show).",
    no_args_is_help=True,
)


def _infer_repo_slug_from_git() -> str | None:
    """Tenta inferir o slug do repositório a partir do remote origin do diretório local."""
    return detect_git_remote_info()[1]


def _resolve_target_repo(repo_opt: str | None, as_json: bool) -> str:
    target_repo = (repo_opt or _infer_repo_slug_from_git() or "").strip()
    if not target_repo:
        msg = (
            "Repositório não informado e não foi possível inferir do Git local. "
            "Use a opção `--repo <slug>` para especificar o repositório."
        )
        print_error(msg, as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    return target_repo


def _render_commits_output(
    commits: list[BitbucketCommit],
    target_repo: str,
    prov_name: str,
    as_json: bool,
) -> None:
    if as_json:
        print_json([c.model_dump() for c in commits])
        return

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    if not commits:
        print_panel(
            "Commits",
            f"Nenhum commit encontrado para os filtros informados em '{target_repo}' ({prov_title}).",
        )
        return

    columns = ["Hash", "Autor", "Data", "Mensagem"]
    rows: list[list[str]] = []
    for c in commits:
        date_str = c.date.split("T")[0] if "T" in c.date else c.date
        rows.append(
            [
                f"[bold yellow]{c.short_hash}[/bold yellow]",
                c.author.author_name,
                date_str,
                c.summary,
            ]
        )

    print_table(f"Histórico de Commits ({target_repo} via {prov_title})", columns, rows)


@commits_app.command("list")
def commits_list(
    ctx: typer.Context,
    repo: str | None = Option(
        None,
        "--repo",
        help="Slug do repositório (inferido do Git local se omitido).",
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
    author: str | None = Option(
        None,
        "--author",
        help="Filtra por nome ou e-mail do autor.",
    ),
    limit: int = Option(
        20,
        "--limit",
        help="Quantidade máxima de commits a retornar.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Lista os commits recentes de um repositório no GitHub ou Bitbucket Cloud."""
    as_json = is_json_mode(ctx, json_output)
    target_repo = _resolve_target_repo(repo, as_json=as_json)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        commits = client.list_commits(
            repo_slug=target_repo,
            workspace=resolved_ws,
            author=author,
            query=None,
            limit=limit,
        )
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    _render_commits_output(commits, target_repo, prov_name, as_json)


@commits_app.command("search")
def commits_search(
    ctx: typer.Context,
    query: str | None = Option(
        None,
        "--query",
        help="Termo obrigatório para filtrar na mensagem do commit.",
    ),
    repo: str | None = Option(
        None,
        "--repo",
        help="Slug do repositório (inferido do Git local se omitido).",
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
    author: str | None = Option(
        None,
        "--author",
        help="Filtra por nome ou e-mail do autor.",
    ),
    limit: int = Option(
        20,
        "--limit",
        help="Quantidade máxima de commits a retornar.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Pesquisa commits cuja mensagem contenha o termo informado em --query."""
    as_json = is_json_mode(ctx, json_output)
    if not query or not query.strip():
        print_error(
            "A opção `--query <termo>` é obrigatória em `neo git commits search`. "
            "Para listar commits sem filtro de mensagem, use `neo git commits list`.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    target_repo = _resolve_target_repo(repo, as_json=as_json)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        commits = client.list_commits(
            repo_slug=target_repo,
            workspace=resolved_ws,
            author=author,
            query=query,
            limit=limit,
        )
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    _render_commits_output(commits, target_repo, prov_name, as_json)


@commits_app.command("show")
def commits_show(
    ctx: typer.Context,
    sha: str = Argument(..., help="Hash completo ou curto (SHA) do commit."),
    repo: str | None = Option(
        None,
        "--repo",
        help="Slug do repositório (inferido do Git local se omitido).",
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
    """Exibe os detalhes completos de um commit específico pelo hash (SHA)."""
    as_json = is_json_mode(ctx, json_output)
    target_repo = _resolve_target_repo(repo, as_json=as_json)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)

    try:
        commit = client.get_commit(repo_slug=target_repo, sha=sha.strip(), workspace=resolved_ws)
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    if as_json:
        payload = commit.model_dump()
        payload["short_hash"] = commit.short_hash
        payload["author_name"] = commit.author.author_name
        payload["repo"] = target_repo
        payload["provider"] = prov_name
        print_json(payload)
    else:
        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        print_panel(
            f"Commit {commit.short_hash} ({target_repo} via {prov_title})",
            f"[bold]Hash:[/bold] [yellow]{commit.hash}[/yellow]\n"
            f"[bold]Autor:[/bold] {commit.author.raw or commit.author.author_name}\n"
            f"[bold]Data:[/bold] {commit.date or '-'}\n"
            f"[bold]URL:[/bold] {commit.web_url or '-'}\n\n"
            f"[bold]Mensagem:[/bold]\n{commit.message.strip()}",
        )
