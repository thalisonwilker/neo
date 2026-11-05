"""Ação de repositório Git."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import (
    print_error,
    print_json,
    print_panel,
    print_table,
)


def repo_search(
    ctx: typer.Context,
    query: str | None = Option(
        None, "--query", help="Termo de pesquisa (nome, slug ou descrição do repositório)."
    ),
    workspace: str | None = Option(
        None, "--workspace", help="Slug do workspace ou organização de destino."
    ),
    provider: str | None = Option(
        None, "--provider", help="Provedor Git: 'github' ou 'bitbucket'."
    ),
    limit: int | None = Option(
        None, "--limit", help="Quantidade máxima de repositórios a retornar."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
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
    except GitProviderError as e:
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
