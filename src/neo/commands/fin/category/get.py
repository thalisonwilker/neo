"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_panel
from neo.services.finance import (
    CategoryNotFoundError,
)


def category_get(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da categoria."),
    category_type: str | None = Option(
        None, "--type", "-t", help="Tipo da categoria ('expense' ou 'income')."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe detalhes de uma categoria específica."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    try:
        cat = service.get_category(slug, category_type=category_type)
    except CategoryNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    if as_json:
        print_json(cat.to_dict())
    else:
        tipo_lbl = "Despesa" if cat.category_type == "expense" else "Receita"
        text = f"[bold]Slug:[/bold] {cat.slug}\n[bold]Nome:[/bold] {cat.name}\n[bold]Tipo:[/bold] {tipo_lbl}\n[bold]Categoria Padrão:[/bold] {('Sim' if cat.is_default else 'Não')}\n[bold]Criado em:[/bold] {cat.created_at}"
        print_panel(f"Categoria: {cat.name}", text)
