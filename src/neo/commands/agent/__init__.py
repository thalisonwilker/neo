"""Comandos de agent."""

import typer

from neo.commands.agent.run import agent_run
from neo.commands.agent.setup import agent_setup
from neo.commands.agent.status import agent_status

agent_app = typer.Typer(
    name="agent",
    help="Diagnóstico, preparação SDD e execução do agente de codificação (Antigravity CLI).",
    no_args_is_help=True,
)

agent_app.command("status")(agent_status)
agent_app.command("setup")(agent_setup)
agent_app.command("run")(agent_run)
