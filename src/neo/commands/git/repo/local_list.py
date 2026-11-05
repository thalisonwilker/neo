"""Ação de repositório Git."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.git_context import (
    list_repos,
)
from neo.output import (
    print_error,
    print_json,
    print_table,
)


def repo_list_local(
    ctx: typer.Context, json_output: bool = Option(False, "--json", help="Emite JSON.")
) -> None:
    """Lista os repositórios locais registrados no Neo."""
    as_json = is_json_mode(ctx, json_output)
    try:
        repos = list_repos()
    except ValueError as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc
    if as_json:
        print_json(repos)
    else:
        print_table(
            "Repositórios locais",
            ["Caminho", "Selecionado", "Task"],
            [
                [str(r["path"]), "Sim" if r["selected"] else "Não", str(r["task"] or "-")]
                for r in repos
            ],
        )
