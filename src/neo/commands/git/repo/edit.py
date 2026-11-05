"""Ação de repositório local."""

from __future__ import annotations

import httpx
import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import local_repo as common
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.output import print_error, print_success


def edit_repo(
    ctx: typer.Context,
    description: str = Option(..., "--description", help="Nova descrição no provedor Git."),
) -> None:
    """Altera a descrição do repositório selecionado no provedor."""
    as_json = is_json_mode(ctx)
    provider, workspace, repo = common.detect_git_remote_details()
    if not provider or not workspace or (not repo):
        print_error(
            "O repositório selecionado não tem um origin GitHub ou Bitbucket reconhecido.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    _, client = common.resolve_git_provider(provider, as_json=as_json)
    try:
        client.update_repository_description(repo, description, workspace=workspace)
    except (GitProviderError, httpx.HTTPError) as exc:
        print_error("Não foi possível atualizar a descrição no provedor.", as_json=as_json, code=1)
        raise typer.Exit(code=1) from exc
    print_success(
        f"Descrição de {workspace}/{repo} atualizada.",
        as_json=as_json,
        json_payload={
            "status": "success",
            "provider": provider,
            "repo": repo,
            "description": description,
        },
    )
