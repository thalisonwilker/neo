"""Ação de tarefas."""

from __future__ import annotations

import typer

from neo.commands._credentials import remove_token
from neo.commands.tasks import _common as common


def config_delete(ctx: typer.Context, service: str = common._service_option()) -> None:
    """Remove a credencial armazenada do serviço de tasks."""
    remove_token(ctx, common._resolve_service(ctx, service))
