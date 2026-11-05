"""Comandos Git."""

import typer

from neo.commands.git._common import _inspect_local_git_status as _inspect_local_git_status
from neo.commands.git.branch import branch_app
from neo.commands.git.commits import commits_app
from neo.commands.git.config.auth import _legacy_config_auth
from neo.commands.git.config.get import git_config_get
from neo.commands.git.config.get_provider import _legacy_config_get_provider
from neo.commands.git.config.list import git_config_list
from neo.commands.git.config.set import git_config_set
from neo.commands.git.config.set_provider import _legacy_config_set_provider
from neo.commands.git.config.unset import git_config_unset
from neo.commands.git.pr import pr_app
from neo.commands.git.repo import repo_app
from neo.commands.git.status import git_status

git_app = typer.Typer(
    name="git",
    help="Gerencia configuração, repositórios e branches no GitHub e Bitbucket Cloud.",
    no_args_is_help=True,
)
git_config_app = typer.Typer(
    name="config",
    help="Gerencia preferências do módulo Git na seção [git] de config.toml (set, get, list, unset).",
    no_args_is_help=True,
)
git_app.add_typer(git_config_app, name="config")
git_app.add_typer(repo_app, name="repo")
git_app.add_typer(commits_app, name="commits")
git_app.add_typer(branch_app, name="branch")
git_app.add_typer(pr_app, name="pr")

git_config_app.command("set")(git_config_set)
git_config_app.command("get")(git_config_get)
git_config_app.command("list")(git_config_list)
git_config_app.command("unset")(git_config_unset)
git_config_app.command(
    "auth", hidden=True, context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)(_legacy_config_auth)
git_config_app.command(
    "set-provider",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(_legacy_config_set_provider)
git_config_app.command(
    "get-provider",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)(_legacy_config_get_provider)
git_app.command("status")(git_status)
