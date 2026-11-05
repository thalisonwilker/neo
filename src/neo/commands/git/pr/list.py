"""Ação de pull request."""

from __future__ import annotations

import httpx
import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.pr import _common as common
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
)


def pr_list_open(
    ctx: typer.Context,
    repo: str | None = Option(None, "--repo", help="Slug do repositório."),
    workspace: str | None = Option(None, "--workspace", help="Workspace do repositório."),
    provider: str | None = Option(None, "--provider", help="Provedor Git."),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Lista os pull requests abertos quando nenhum subcomando é informado."""
    if ctx.invoked_subcommand is not None:
        return
    as_json = is_json_mode(ctx, json_output)
    target, ws, client = common._context(provider, workspace, repo, as_json)
    try:
        results = client.list_open_pull_requests(target, workspace=ws)
    except GitProviderError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        common._network_error(exc, as_json)
    common._render_results(results, as_json)
