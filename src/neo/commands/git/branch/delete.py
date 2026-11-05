"""Ação de branch local."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.branch import _common as common
from neo.output import print_success


def branch_delete(
    ctx: typer.Context,
    name: str = Argument(..., help="Nome da branch local a excluir."),
    yes: bool = Option(False, "--yes", help="Confirma a exclusão sem perguntar."),
) -> None:
    """Exclui uma branch local já mesclada, mediante confirmação."""
    as_json = is_json_mode(ctx)
    try:
        if not name.strip() or name.startswith("-"):
            raise ValueError("Informe um nome de branch válido.")
        path = common.resolve_repo_path()
        active = common._git(path, "branch", "--show-current")
        if name == active:
            raise ValueError("Não é possível excluir a branch ativa.")
        if not yes:
            if as_json:
                raise ValueError("Use --yes para confirmar a exclusão em modo JSON.")
            if not typer.confirm(f"Excluir a branch local '{name}'?"):
                raise ValueError("Operação cancelada pelo usuário.")
        common._git(path, "branch", "-d", "--", name)
    except ValueError as exc:
        common._fail(exc, as_json)
    print_success(f"Branch excluída: {name}", as_json=as_json, json_payload={"branch": name})
