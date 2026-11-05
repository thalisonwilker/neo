"""Ação de branch local."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git.branch import _common as common
from neo.output import print_json, print_table


def branch_list(
    ctx: typer.Context, json_output: bool = Option(False, "--json", help="Emite JSON estruturado.")
) -> None:
    """Lista branches locais e identifica a branch ativa."""
    as_json = is_json_mode(ctx, json_output)
    try:
        path = common.resolve_repo_path()
        names = common._git(
            path, "for-each-ref", "--format=%(refname:short)", "refs/heads"
        ).splitlines()
        active = common._git(path, "branch", "--show-current") or None
    except ValueError as exc:
        common._fail(exc, as_json)
    data = [{"name": name, "active": name == active} for name in names]
    if as_json:
        print_json(data)
    else:
        print_table(
            "Branches locais",
            ["Branch", "Ativa"],
            [[name, "Sim" if name == active else "-"] for name in names],
        )
