"""Comandos de config."""

import typer

from neo.commands.config.agent.get import agent_config_get
from neo.commands.config.agent.list import agent_config_list
from neo.commands.config.agent.set import agent_config_set
from neo.commands.config.agent.unset import agent_config_unset
from neo.commands.config.show import config_show

config_app = typer.Typer(
    name="config",
    help="Visão geral das configurações do Neo (`neo git`, `neo tasks` e `neo config agent`).",
    no_args_is_help=True,
)
agent_config_app = typer.Typer(
    name="agent",
    help="Gerencia preferências do agente de codificação (command, model, sdd-provider, adapter).",
    no_args_is_help=True,
)
config_app.add_typer(agent_config_app, name="agent")

agent_config_app.command("set")(agent_config_set)
agent_config_app.command("get")(agent_config_get)
agent_config_app.command("list")(agent_config_list)
agent_config_app.command("unset")(agent_config_unset)
config_app.command("show")(config_show)
