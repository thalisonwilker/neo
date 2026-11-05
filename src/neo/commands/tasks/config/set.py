"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import save_token
from neo.commands.tasks import _common as common


def config_set(
    ctx: typer.Context,
    service: str = common._service_option(),
    token: str = Option(
        None,
        "--token",
        "-t",
        help="Token de acesso da API. Se omitido, solicita via prompt seguro.",
    ),
) -> None:
    """Configura o token do serviço de tasks de forma segura."""
    save_token(ctx, common._resolve_service(ctx, service), token)
