"""Comandos de pull request para GitHub e Bitbucket Cloud."""

from __future__ import annotations

from typing import NoReturn

import httpx
import typer

from neo.commands.git.commits import _resolve_target_repo
from neo.config import ExitCode
from neo.integrations.git.pr_models import PullRequest
from neo.integrations.git.provider import GitProvider
from neo.integrations.git.resolver import (
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_json, print_success, print_table


def _fail(message: str, as_json: bool, code: ExitCode = ExitCode.USAGE_ERROR) -> NoReturn:
    print_error(message, as_json=as_json, code=int(code))
    raise typer.Exit(code=int(code))


def _context(
    provider: str | None, workspace: str | None, repo: str | None, as_json: bool
) -> tuple[str, str | None, GitProvider]:
    target = _resolve_target_repo(repo, as_json)
    provider_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_workspace, _ = resolve_git_workspace_and_source(provider_name, workspace)
    return target, resolved_workspace, client


def _network_error(exc: httpx.HTTPError, as_json: bool) -> NoReturn:
    print_error(
        "Falha de rede ao consultar o provedor Git.", as_json=as_json, code=int(ExitCode.ERROR)
    )
    raise typer.Exit(code=int(ExitCode.ERROR)) from exc


def _render_results(results: list[PullRequest], as_json: bool) -> None:
    if as_json:
        print_json([result.model_dump() for result in results])
    elif not results:
        print_success("Nenhum pull request encontrado.", as_json=False)
    else:
        print_table(
            "Pull requests",
            ["ID", "Título", "Estado", "Origem", "Destino", "URL"],
            [[str(r.id), r.title, r.state, r.source, r.destination, r.url] for r in results],
        )
