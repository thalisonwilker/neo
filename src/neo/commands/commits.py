"""Comandos de consulta e histórico de commits Git (Bitbucket e GitHub) (`neo commits`)."""

from __future__ import annotations

import typer
from typer import Option

from neo.integrations.bitbucket import BitbucketError
from neo.integrations.resolver import (
    detect_git_remote_info,
    resolve_git_provider,
)
from neo.output import print_error, print_json, print_panel, print_table

commits_app = typer.Typer(
    name="commits",
    help="Histórico e pesquisa de commits no Bitbucket e GitHub.",
    no_args_is_help=True,
)


def _infer_repo_slug_from_git() -> str | None:
    """Tenta inferir o slug do repositório a partir do remote origin do diretório local."""
    return detect_git_remote_info()[1]


@commits_app.command("search")
def commits_search(
    ctx: typer.Context,
    repo: str | None = Option(
        None, "--repo", "-r", help="Slug do repositório (inferido do git local se omitido)."
    ),
    workspace: str | None = Option(
        None, "--workspace", "-w", help="Workspace ou organização/usuário de destino."
    ),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
    author: str | None = Option(None, "--author", "-a", help="Filtra por nome ou e-mail do autor."),
    query: str | None = Option(
        None, "--query", "-q", help="Filtra por termo na mensagem do commit."
    ),
    limit: int = Option(20, "--limit", "-l", help="Quantidade máxima de commits a retornar."),
) -> None:
    """Pesquisa commits em um repositório no Bitbucket ou GitHub."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False

    target_repo = repo or _infer_repo_slug_from_git()
    if not target_repo:
        msg = (
            "Repositório não informado e não foi possível inferir do git local. "
            "Use a flag `--repo <slug>` para especificar o repositório."
        )
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)

    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    try:
        commits = client.list_commits(
            repo_slug=target_repo,
            workspace=workspace,
            author=author,
            query=query,
            limit=limit,
        )
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json([c.model_dump() for c in commits])
    else:
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
