"""Ação de consulta de commits."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.commits import _common as common
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)


def commits_list(
    ctx: typer.Context,
    repo: str | None = Option(
        None, "--repo", help="Slug do repositório (inferido do Git local se omitido)."
    ),
    workspace: str | None = Option(
        None, "--workspace", help="Slug do workspace ou organização de destino."
    ),
    provider: str | None = Option(
        None, "--provider", help="Provedor Git: 'github' ou 'bitbucket'."
    ),
    author: str | None = Option(None, "--author", help="Filtra por nome ou e-mail do autor."),
    limit: int = Option(20, "--limit", help="Quantidade máxima de commits a retornar."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Lista os commits recentes de um repositório no GitHub ou Bitbucket Cloud."""
    as_json = is_json_mode(ctx, json_output)
    target_repo = common._resolve_target_repo(repo, as_json=as_json)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)
    try:
        commits = client.list_commits(
            repo_slug=target_repo, workspace=resolved_ws, author=author, query=None, limit=limit
        )
    except GitProviderError as e:
        handle_git_provider_error(e, as_json=as_json)
    common._render_commits_output(commits, target_repo, prov_name, as_json)
