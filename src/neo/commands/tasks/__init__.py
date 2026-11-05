"""Comandos de tarefas."""

import typer

from neo.commands.tasks.analyze import tasks_analyze
from neo.commands.tasks.check.add import check_add
from neo.commands.tasks.check.complete import check_complete
from neo.commands.tasks.check.list import check_list
from neo.commands.tasks.check.uncomplete import check_uncomplete
from neo.commands.tasks.comment.add import comment_add
from neo.commands.tasks.comment.list import comment_list
from neo.commands.tasks.config.columns import config_columns
from neo.commands.tasks.config.delete import config_delete
from neo.commands.tasks.config.get import config_get
from neo.commands.tasks.config.set import config_set
from neo.commands.tasks.create import tasks_create
from neo.commands.tasks.iterations import tasks_iterations
from neo.commands.tasks.list import tasks_list
from neo.commands.tasks.resume import tasks_resume
from neo.commands.tasks.search import tasks_search
from neo.commands.tasks.show import tasks_show
from neo.commands.tasks.whoami import tasks_whoami

tasks_app = typer.Typer(
    name="tasks",
    help="Consulta e análise de tasks/demandas (Shortcut, API v3). Use --service para escolher o serviço.",
    no_args_is_help=True,
)
tasks_config_app = typer.Typer(
    name="config",
    help="Credenciais do serviço de tasks (Shortcut).",
    no_args_is_help=True,
)
tasks_app.add_typer(tasks_config_app, name="config")
tasks_check_app = typer.Typer(
    name="check",
    help="Gerencia itens de checklist (tasks) de uma story no Shortcut.",
    no_args_is_help=True,
)
tasks_app.add_typer(tasks_check_app, name="check")
tasks_comment_app = typer.Typer(
    name="comment",
    help="Adiciona comentários em stories no Shortcut.",
    no_args_is_help=True,
)
tasks_app.add_typer(tasks_comment_app, name="comment")

tasks_config_app.command("set")(config_set)
tasks_config_app.command("get")(config_get)
tasks_config_app.command("delete")(config_delete)
tasks_config_app.command("columns")(config_columns)
tasks_app.command("whoami")(tasks_whoami)
tasks_app.command("iterations")(tasks_iterations)
tasks_app.command("create")(tasks_create)
tasks_app.command("list")(tasks_list)
tasks_app.command("search")(tasks_search)
tasks_app.command("get", hidden=True)(tasks_show)
tasks_app.command("show")(tasks_show)
tasks_check_app.command("list")(check_list)
tasks_check_app.command("add")(check_add)
tasks_check_app.command("done", hidden=True)(check_complete)
tasks_check_app.command("complete")(check_complete)
tasks_check_app.command("undone", hidden=True)(check_uncomplete)
tasks_check_app.command("uncomplete")(check_uncomplete)
tasks_comment_app.command("list")(comment_list)
tasks_comment_app.command("add")(comment_add)
tasks_app.command("analyze")(tasks_analyze)
tasks_app.command("resume")(tasks_resume)
