"""Ação de tarefas."""

from __future__ import annotations

import typer

from neo.commands._credentials import show_token
from neo.commands.tasks import _common as common


def config_get(ctx: typer.Context, service: str = common._service_option()) -> None:
    """Exibe o status e o token mascarado do serviço de tasks."""
    show_token(ctx, common._resolve_service(ctx, service))
