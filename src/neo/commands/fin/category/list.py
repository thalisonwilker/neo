"""Ação financeira."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.fin import _common as common
from neo.config import ExitCode
from neo.output import print_error, print_json, print_table


def category_list(
    ctx: typer.Context,
    category_type: str | None = Option(
        None, "--type", "-t", help="Filtrar por tipo: 'expense' ou 'income'."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Lista as categorias de despesas e receitas cadastradas."""
    as_json = is_json_mode(ctx, json_output)
    service = common._get_service()
    if category_type and category_type not in ("expense", "income"):
        print_error(
            "Tipo de categoria inválido. Use 'expense' ou 'income'.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    categories = service.list_categories(category_type=category_type)
    if as_json:
        print_json([c.to_dict() for c in categories])
    else:
        rows = [
            [
                c.slug,
                c.name,
                "Despesa" if c.category_type == "expense" else "Receita",
                "Sim" if c.is_default else "Não",
            ]
            for c in categories
        ]
        titulo = f"Categorias ({category_type})" if category_type else "Categorias de Transações"
        print_table(titulo, ["Slug", "Nome", "Tipo", "Padrão"], rows)
