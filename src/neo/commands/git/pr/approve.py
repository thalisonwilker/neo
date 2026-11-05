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
from neo.output import print_success


def pr_approve(
    ctx: typer.Context,
    pr_id: int = Argument(..., help="ID do pull request."),
    message: str | None = Option(None, "--message", help="Mensagem de aprovação."),
    repo: str | None = Option(None, "--repo"),
    workspace: str | None = Option(None, "--workspace"),
    provider: str | None = Option(None, "--provider"),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Aprova um pull request com mensagem."""
    as_json = is_json_mode(ctx, json_output)
    if pr_id < 1:
        common._fail("O ID deve ser positivo.", as_json)
    if message is None:
        if as_json:
            common._fail("Em modo JSON informe --message.", True)
        message = typer.prompt("Mensagem de aprovação")
    if not message.strip():
        common._fail("A mensagem não pode ser vazia.", as_json)
    target, ws, client = common._context(provider, workspace, repo, as_json)
    try:
        client.approve_pull_request(target, pr_id, message.strip(), workspace=ws)
    except GitProviderError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        common._network_error(exc, as_json)
    print_success(
        f"Pull request #{pr_id} aprovado.",
        as_json=as_json,
        json_payload={"id": pr_id, "status": "approved"},
    )
