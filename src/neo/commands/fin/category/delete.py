"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_success
from neo.services.finance import (
    CategoryInUseError,
    CategoryNotFoundError,
)


def category_delete(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da categoria a remover."),
    category_type: str | None = Option(
        None, "--type", "-t", help="Tipo da categoria ('expense' ou 'income')."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Remove uma categoria que não possua transações vinculadas."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        service.delete_category(slug=slug, category_type=category_type)
    except CategoryNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except CategoryInUseError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))
    if as_json:
        print_json({"status": "success", "message": f"Categoria '{slug}' removida com sucesso."})
    else:
        print_success(f"Categoria '{slug}' removida com sucesso.")
