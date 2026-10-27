"""Entrypoint principal da CLI Neo."""

from __future__ import annotations

from dataclasses import dataclass

import typer
from rich import print as rprint

from neo.commands.commits import commits_app
from neo.commands.config import config_app
from neo.commands.repo import repo_app
from neo.commands.story import story_app

__version__ = "0.1.0"


@dataclass
class AppContext:
    json_mode: bool = False
    verbose: bool = False


app = typer.Typer(
    name="neo",
    help="""[bold cyan]Neo — Personal Command Assistant[/bold cyan]

Compreenda seus sistemas. Seja dono das suas escolhas.

Centraliza operações de trabalho (Bitbucket, Shortcut) e vida pessoal,
investigando dados com autonomia e sem atrito.
""",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Registra subcomandos
app.add_typer(config_app, name="config")
app.add_typer(repo_app, name="repo")
app.add_typer(commits_app, name="commits")
app.add_typer(story_app, name="story")


def version_callback(value: bool) -> None:
    if value:
        rprint(f"[bold cyan]Neo[/bold cyan] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        "-V",
        help="Exibe a versão do Neo e encerra.",
        callback=version_callback,
        is_eager=True,
    ),
    json_mode: bool = typer.Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Habilita mensagens de debug e detalhes de rede.",
    ),
) -> None:
    """Configura o contexto global da aplicação."""
    ctx.obj = AppContext(json_mode=json_mode, verbose=verbose)


if __name__ == "__main__":
    app()
