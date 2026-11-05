"""Comandos de consulta de commits."""

import typer

from neo.commands.git.commits._common import _resolve_target_repo as _resolve_target_repo
from neo.commands.git.commits.list import commits_list
from neo.commands.git.commits.search import commits_search
from neo.commands.git.commits.show import commits_show

commits_app = typer.Typer(
    name="commits",
    help="Lista, pesquisa e inspeciona commits no GitHub e Bitbucket Cloud (list, search, show).",
    no_args_is_help=True,
)
commits_app.command("list")(commits_list)
commits_app.command("search")(commits_search)
commits_app.command("get", hidden=True)(commits_show)
commits_app.command("show")(commits_show)
