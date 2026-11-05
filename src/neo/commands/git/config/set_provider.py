"""Ação de configuração Git."""

from __future__ import annotations

import typer

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common


def _legacy_config_set_provider(ctx: typer.Context) -> None:
    common._fail_usage(
        "O comando `neo git config set-provider` foi removido. Use `neo git config set provider <github|bitbucket>`.",
        as_json=is_json_mode(ctx),
    )
