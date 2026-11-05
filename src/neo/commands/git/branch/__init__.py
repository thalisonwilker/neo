"""Comandos de branches locais."""

import typer

from neo.commands.git.branch._common import current_branch as current_branch
from neo.commands.git.branch._common import select_branch as select_branch
from neo.commands.git.branch.create import branch_create
from neo.commands.git.branch.delete import branch_delete
from neo.commands.git.branch.list import branch_list
from neo.commands.git.branch.select import branch_select

branch_app = typer.Typer(
    name="branch",
    help="Lista, seleciona, cria e exclui branches locais do repositório selecionado.",
    no_args_is_help=True,
)
branch_app.command("list")(branch_list)
branch_app.command("select")(branch_select)
branch_app.command("create")(branch_create)
branch_app.command("delete")(branch_delete)
