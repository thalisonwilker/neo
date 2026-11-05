"""Comandos de repositórios Git."""

import typer

from neo.commands.git.repo.clone import _legacy_repo_clone
from neo.commands.git.repo.create import create_repo
from neo.commands.git.repo.edit import edit_repo
from neo.commands.git.repo.list import repo_list
from neo.commands.git.repo.local_list import repo_list_local
from neo.commands.git.repo.remote_list import repo_remote_list
from neo.commands.git.repo.search import repo_search
from neo.commands.git.repo.select import repo_select
from neo.commands.git.repo.show import repo_show

repo_app = typer.Typer(
    name="repo",
    help="Gerencia repositórios locais e no GitHub ou Bitbucket Cloud.",
    no_args_is_help=True,
)
repo_app.command("create")(create_repo)
repo_app.command("edit")(edit_repo)
repo_app.command("list")(repo_list)
repo_app.command("remote-list")(repo_remote_list)
repo_app.command("local-list")(repo_list_local)
repo_app.command("select")(repo_select)
repo_app.command("search")(repo_search)
repo_app.command("get", hidden=True)(repo_show)
repo_app.command("show")(repo_show)
repo_app.command(
    "clone",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(_legacy_repo_clone)
