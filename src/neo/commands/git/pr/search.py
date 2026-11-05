"""Ação de pull request."""

from __future__ import annotations

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.pr import _common as common
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
)


def pr_search(
    ctx: typer.Context,
    query: str = Argument(..., help="ID exato ou trecho do título."),
    repo: str | None = Option(None, "--repo"),
    workspace: str | None = Option(None, "--workspace"),
    provider: str | None = Option(None, "--provider"),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Pesquisa pull requests pelo ID ou título."""
    as_json = is_json_mode(ctx, json_output)
    if not query.strip():
        common._fail("Informe um ID ou trecho do título.", as_json)
    target, ws, client = common._context(provider, workspace, repo, as_json)
    try:
        results = client.search_pull_requests(target, query.strip(), workspace=ws)
    except GitProviderError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        common._network_error(exc, as_json)
    common._render_results(results, as_json)
