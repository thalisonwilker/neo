"""Ação de branch local."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands._credentials import is_json_mode
from neo.commands.git.branch import _common as common
from neo.output import print_success


def branch_select(
    ctx: typer.Context, name: str = Argument(..., help="Nome da branch local.")
) -> None:
    """Seleciona a branch local com checkout."""
    as_json = is_json_mode(ctx)
    try:
        common.select_branch(name)
    except ValueError as exc:
        common._fail(exc, as_json)
    print_success(f"Branch selecionada: {name}", as_json=as_json, json_payload={"branch": name})
