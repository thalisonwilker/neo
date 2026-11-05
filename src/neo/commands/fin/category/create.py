"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_success
from neo.services.finance import (
    DuplicateEntityError,
)


def category_create(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug único da categoria (ex: jogos, cursos, mercado)."),
    name: str = Option(..., "--name", "-n", help="Nome de exibição da categoria."),
    category_type: str = Option(
        ..., "--type", "-t", help="Tipo da categoria: 'expense' ou 'income'."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Cadastra uma nova categoria de despesa ou receita."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    if category_type not in ("expense", "income"):
        print_error(
            "Tipo de categoria inválido. Use 'expense' ou 'income'.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    try:
        cat = service.create_category(slug=slug, name=name, category_type=category_type)
    except DuplicateEntityError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))
    if as_json:
        print_json(cat.to_dict())
    else:
        tipo_lbl = "Despesa" if cat.category_type == "expense" else "Receita"
        print_success(f"Categoria '{cat.name}' ({cat.slug}) criada para {tipo_lbl}.")
