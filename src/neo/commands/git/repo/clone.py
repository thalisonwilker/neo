"""Ação de repositório Git."""

from __future__ import annotations

import typer

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.output import (
    print_error,
)


def _legacy_repo_clone(ctx: typer.Context) -> None:
    as_json = is_json_mode(ctx)
    print_error(
        "O comando `neo git repo clone` está no backlog planejado desta versão. Use `neo git repo show --repo <slug>` para consultar as URLs de clone.",
        as_json=as_json,
        code=int(ExitCode.USAGE_ERROR),
    )
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
