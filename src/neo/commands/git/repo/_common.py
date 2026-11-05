"""Comandos de consulta de repositórios Git (`neo git repo`: `list`, `search`, `show`)."""

from __future__ import annotations

import httpx
import typer

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.git_context import (
    get_repo_tasks_map,
    resolve_task_for_repo,
)
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
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
    except GitProviderError as e:
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


# Bloqueios orientativos para comandos movidos para o backlog planejado
