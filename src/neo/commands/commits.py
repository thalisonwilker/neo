"""Comandos de consulta e histórico de commits no Bitbucket (`neo commits`)."""

from __future__ import annotations

import re
import subprocess

import typer
from typer import Option

from neo.config import get_credential
from neo.integrations.bitbucket import (
    BitbucketClient,
    BitbucketError,
)
from neo.output import print_error, print_json, print_panel, print_table

commits_app = typer.Typer(
    name="commits",
    help="Histórico e pesquisa de commits no Bitbucket.",
    no_args_is_help=True,
)


def _infer_repo_slug_from_git() -> str | None:
    """Tenta inferir o slug do repositório a partir do remote origin do diretório local."""
    try:
        res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            url = res.stdout.strip()
            # Padrões: git@bitbucket.org:workspace/repo.git ou https://bitbucket.org/workspace/repo.git
            m = re.search(r"bitbucket\.org[:/][^/]+/([^/.]+)(?:\.git)?", url)
            if m:
                return m.group(1)
    except (subprocess.SubprocessError, OSError):
        return None
    return None


def _get_bitbucket_client(as_json: bool) -> BitbucketClient:
    token = get_credential("bitbucket")
    if not token:
        msg = "Credenciais do Bitbucket não configuradas. Execute `neo config auth set bitbucket`."
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)
    return BitbucketClient(token=token)


@commits_app.command("search")
def commits_search(
    ctx: typer.Context,
    repo: str | None = Option(
        None, "--repo", "-r", help="Slug do repositório (inferido do git local se omitido)."
    ),
    workspace: str | None = Option(None, "--workspace", "-w", help="Workspace do Bitbucket."),
    author: str | None = Option(None, "--author", "-a", help="Filtra por nome ou e-mail do autor."),
    query: str | None = Option(
        None, "--query", "-q", help="Filtra por termo na mensagem do commit."
    ),
    limit: int = Option(20, "--limit", "-l", help="Quantidade máxima de commits a retornar."),
) -> None:
    """Pesquisa commits em um repositório do Bitbucket."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    target_repo = repo or _infer_repo_slug_from_git()
    if not target_repo:
        msg = (
            "Repositório não informado e não foi possível inferir do git local. "
            "Use a flag `--repo <slug>` para especificar o repositório."
        )
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)

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
        if not commits:
            print_panel(
                "Commits",
                f"Nenhum commit encontrado para os filtros informados em '{target_repo}'.",
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

        print_table(f"Histórico de Commits ({target_repo})", columns, rows)
