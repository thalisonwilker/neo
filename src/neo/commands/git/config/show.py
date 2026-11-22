"""Ação de configuração Git."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common
from neo.commands.git.branch import current_branch
from neo.commands.git.config._display import git_config_panel
from neo.config import (
    get_bitbucket_project,
    list_git_config_values,
)
from neo.git_context import (
    get_task,
    selected_repo,
)
from neo.output import (
    console,
    print_json,
)


def git_config_show(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Exibe as configurações e o contexto Git."""
    as_json = is_json_mode(ctx, json_output)
    values = list_git_config_values()
    values["api-key"] = common._api_key_info()
    if values["provider"]["value"] == "bitbucket":
        project = get_bitbucket_project(values["workspace"]["value"])
        values["project"] = {"value": project, "source": "config" if project else "default"}
    try:
        selected = selected_repo()
        values["repo"] = {"value": str(selected) if selected else None, "source": "context"}
        values["task"] = {"value": get_task(), "source": "context"}
        values["branch"] = {"value": current_branch(), "source": "context"}
    except ValueError:
        values.setdefault("repo", {"value": None, "source": "context"})
        values["task"] = {"value": None, "source": "context"}
        values["branch"] = {"value": None, "source": "context"}
    if as_json:
        print_json(values)
    else:
        console.print(git_config_panel(values))
