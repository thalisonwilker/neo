"""Ação de pull request."""

from __future__ import annotations

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.pr import _common as common
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
)
from neo.output import print_success


def pr_decline(
    ctx: typer.Context,
    pr_id: int = Argument(..., help="ID do pull request."),
    yes: bool = Option(False, "--yes", help="Confirma a recusa."),
    repo: str | None = Option(None, "--repo"),
    workspace: str | None = Option(None, "--workspace"),
    provider: str | None = Option(None, "--provider"),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Recusa ou fecha um pull request sem fazer merge."""
    as_json = is_json_mode(ctx, json_output)
    if pr_id < 1:
        common._fail("O ID deve ser positivo.", as_json)
    if not yes:
        if as_json:
            common._fail("Em modo JSON informe --yes.", True)
        if not typer.confirm(f"Recusar o pull request #{pr_id}?"):
            common._fail("Operação cancelada.", as_json, ExitCode.ERROR)
    target, ws, client = common._context(provider, workspace, repo, as_json)
    try:
        client.decline_pull_request(target, pr_id, workspace=ws)
    except GitProviderError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        common._network_error(exc, as_json)
    print_success(
        f"Pull request #{pr_id} recusado.",
        as_json=as_json,
        json_payload={"id": pr_id, "status": "declined"},
    )
