"""Ação de branch local."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands._credentials import is_json_mode
from neo.commands.git.branch import _common as common
from neo.output import print_success


def branch_create(
    ctx: typer.Context, name: str = Argument(..., help="Nome da nova branch local.")
) -> None:
    """Cria uma branch local sem alterar a branch ativa."""
    as_json = is_json_mode(ctx)
    try:
        if not name.strip() or name.startswith("-"):
            raise ValueError("Informe um nome de branch válido.")
        common._git(common.resolve_repo_path(), "branch", "--", name)
    except ValueError as exc:
        common._fail(exc, as_json)
    print_success(f"Branch criada: {name}", as_json=as_json, json_payload={"branch": name})
