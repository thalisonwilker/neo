"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Argument

from neo.commands.tasks import _common as common


def comment_add(
    ctx: typer.Context,
    story_id: int = Argument(..., help="ID da story no Shortcut."),
    text: str = Argument(..., help="Texto do comentário."),
    service: str = common._service_option(),
) -> None:
    """Adiciona um comentário a uma story."""
    common._add_comment_impl(ctx, story_id, text, service)
