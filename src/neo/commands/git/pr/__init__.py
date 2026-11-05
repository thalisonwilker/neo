"""Comandos de pull requests."""

import typer

from neo.commands.git.pr.approve import pr_approve
from neo.commands.git.pr.decline import pr_decline
from neo.commands.git.pr.list import pr_list_open
from neo.commands.git.pr.open import pr_open
from neo.commands.git.pr.search import pr_search

pr_app = typer.Typer(
    name="pr",
    help="Lista, abre, aprova, recusa e pesquisa pull requests.",
    invoke_without_command=True,
)
pr_app.callback()(pr_list_open)
pr_app.command("open")(pr_open)
pr_app.command("approve")(pr_approve)
pr_app.command("decline")(pr_decline)
pr_app.command("search")(pr_search)
