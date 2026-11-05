"""Ação de consulta de commits."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.commits import _common as common
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_json, print_panel


def commits_show(
    ctx: typer.Context,
    sha: str = Argument(..., help="Hash completo ou curto (SHA) do commit."),
    repo: str | None = Option(
        None, "--repo", help="Slug do repositório (inferido do Git local se omitido)."
    ),
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
    """Exibe os detalhes completos de um commit específico pelo hash (SHA)."""
    as_json = is_json_mode(ctx, json_output)
    target_repo = common._resolve_target_repo(repo, as_json=as_json)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)
    try:
        commit = client.get_commit(repo_slug=target_repo, sha=sha.strip(), workspace=resolved_ws)
    except GitProviderError as e:
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
            f"[bold]Hash:[/bold] [yellow]{commit.hash}[/yellow]\n[bold]Autor:[/bold] {commit.author.raw or commit.author.author_name}\n[bold]Data:[/bold] {commit.date or '-'}\n[bold]URL:[/bold] {commit.web_url or '-'}\n\n[bold]Mensagem:[/bold]\n{commit.message.strip()}",
        )
