"""Ação de consulta de commits."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.commits import _common as common
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_error


def commits_search(
    ctx: typer.Context,
    query: str | None = Option(
        None, "--query", help="Termo obrigatório para filtrar na mensagem do commit."
    ),
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
    """Pesquisa commits cuja mensagem contenha o termo informado em --query."""
    as_json = is_json_mode(ctx, json_output)
    if not query or not query.strip():
        print_error(
            "A opção `--query <termo>` é obrigatória em `neo git commits search`. Para listar commits sem filtro de mensagem, use `neo git commits list`.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    target_repo = common._resolve_target_repo(repo, as_json=as_json)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_ws, _ = resolve_git_workspace_and_source(prov_name, workspace)
    try:
        commits = client.list_commits(
            repo_slug=target_repo, workspace=resolved_ws, author=author, query=query, limit=limit
        )
    except GitProviderError as e:
        handle_git_provider_error(e, as_json=as_json)
    common._render_commits_output(commits, target_repo, prov_name, as_json)
