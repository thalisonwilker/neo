"""Ação de configuração Git."""

from __future__ import annotations

import typer

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common


def _legacy_config_auth(ctx: typer.Context) -> None:
    common._fail_usage(
        "O comando `neo git config auth` foi removido. Use `neo git config set api-key`, `neo git config get api-key` ou `neo git config unset api-key`.",
        as_json=is_json_mode(ctx),
    )
