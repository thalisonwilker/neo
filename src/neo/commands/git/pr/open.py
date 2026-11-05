"""Ação de pull request."""

from __future__ import annotations

import httpx
import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.branch import current_branch
from neo.commands.git.pr import _common as common
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import (
    handle_git_provider_error,
)
from neo.output import console, print_json, print_success


def pr_open(
    ctx: typer.Context,
    base: str | None = Option(None, "--base", help="Branch remota de destino."),
    title: str | None = Option(None, "--title", help="Título do pull request."),
    description: str | None = Option(None, "--description", help="Descrição do pull request."),
    repo: str | None = Option(None, "--repo", help="Slug do repositório."),
    workspace: str | None = Option(None, "--workspace", help="Workspace do repositório."),
    provider: str | None = Option(None, "--provider", help="Provedor Git."),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Abre pull request usando a branch local atual como origem."""
    as_json = is_json_mode(ctx, json_output)
    try:
        source = current_branch()
    except ValueError as exc:
        common._fail(str(exc), as_json, ExitCode.NOT_FOUND)
    if not source:
        common._fail(
            "Nenhuma branch ativa. Selecione uma branch antes de abrir o pull request.", as_json
        )
    if as_json and (base is None or title is None or description is None):
        common._fail("Em modo JSON informe --base, --title e --description.", True)
    target, ws, client = common._context(provider, workspace, repo, as_json)
    try:
        branches = client.list_pr_branches(target, workspace=ws)
        if source not in branches:
            common._fail(
                f"A branch '{source}' não existe no provedor. Publique a branch antes de abrir o PR.",
                as_json,
                ExitCode.NOT_FOUND,
            )
        if base is None:
            choices = [name for name in branches if name != source]
            if not choices:
                common._fail(
                    "Nenhuma branch remota de destino disponível.", as_json, ExitCode.NOT_FOUND
                )
            for i, name in enumerate(choices, 1):
                console.print(f"{i}. {name}")
            selected = typer.prompt("Número da branch de destino", type=int)
            if selected < 1 or selected > len(choices):
                common._fail("Seleção de branch inválida.", as_json)
            base = choices[selected - 1]
        if base not in branches or base == source:
            common._fail(
                "A branch de destino deve existir no provedor e ser diferente da origem.", as_json
            )
        if title is None:
            title = typer.prompt("Título")
        if not title.strip():
            common._fail("O título não pode ser vazio.", as_json)
        if description is None:
            description = typer.prompt("Descrição", default="", show_default=False)
        result = client.create_pull_request(
            target, source, base, title.strip(), description, workspace=ws
        )
    except GitProviderError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        common._network_error(exc, as_json)
    if as_json:
        print_json(result.model_dump())
    else:
        print_success(f"Pull request #{result.id} criado: {result.url}", as_json=False)
