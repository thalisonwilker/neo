"""Ação de repositório Git."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands.git.repo import _common as common


def repo_list(
    ctx: typer.Context,
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
    """Lista os repositórios do workspace selecionado no provedor Git."""
    common._execute_repo_list(
        ctx, workspace=workspace, provider=provider, limit=limit, json_output=json_output
    )
