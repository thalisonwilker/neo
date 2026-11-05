"""Ação de repositório Git."""

from __future__ import annotations

from pathlib import Path

import typer
from typer import Argument

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.git_context import (
    select_repo,
)
from neo.output import (
    print_error,
    print_json,
    print_panel,
)


def repo_select(
    ctx: typer.Context,
    path: Path = Argument(..., help="Caminho do repositório."),  # noqa: B008
) -> None:
    """Registra e seleciona um repositório local."""
    as_json = is_json_mode(ctx)
    try:
        selected = select_repo(path)
    except (ValueError, OSError) as exc:
        print_error(str(exc), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc
    if as_json:
        print_json({"path": str(selected), "selected": True})
    else:
        print_panel("Repositório selecionado", str(selected))
