"""Guarda-chuva dos comandos Git (Bitbucket e GitHub) (`neo git`)."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode, remove_token, save_token, show_token
from neo.commands.commits import commits_app
from neo.commands.repo import repo_app
from neo.commands.workspace import workspace_app
from neo.config import (
    SUPPORTED_GIT_PROVIDERS,
    SUPPORTED_TASK_SERVICES,
    GitProviderType,
    get_default_provider_config,
    set_default_provider_config,
    validate_git_provider,
)
from neo.output import print_error, print_json, print_panel, print_success

git_app = typer.Typer(
    name="git",
    help="Comandos Git unificados para Bitbucket e GitHub (config, workspace, repo, commits).",
    no_args_is_help=True,
)

git_config_app = typer.Typer(
    name="config",
    help="Credenciais e provedor Git padrão (Bitbucket, GitHub).",
    no_args_is_help=True,
)

auth_app = typer.Typer(
    name="auth",
    help="Gerencia tokens de autenticação dos provedores Git (Bitbucket, GitHub).",
    no_args_is_help=True,
)

git_config_app.add_typer(auth_app, name="auth")
git_app.add_typer(git_config_app, name="config")
git_app.add_typer(workspace_app, name="workspace")
git_app.add_typer(repo_app, name="repo")
git_app.add_typer(commits_app, name="commits")


def _validate_git_service(ctx: typer.Context, service: str) -> GitProviderType:
    """Valida o serviço Git; `shortcut` é rejeitado com dica para `neo tasks config`."""
    as_json = is_json_mode(ctx)
    if service.strip().lower() in SUPPORTED_TASK_SERVICES:
        print_error(
            f"'{service}' é um serviço de tasks, não um provedor Git. "
            f"Use `neo tasks config` para configurá-lo.",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1)
    try:
        return validate_git_provider(service)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e


@auth_app.command("set")
def auth_set(
    ctx: typer.Context,
    service: str = Argument(
        ..., help=f"Provedor para autenticar: {', '.join(SUPPORTED_GIT_PROVIDERS)}"
    ),
    token: str = Option(
        None,
        "--token",
        "-t",
        help="Token de acesso da API. Se omitido, solicita via prompt seguro.",
    ),
) -> None:
    """Configura o token de autenticação de um provedor Git de forma segura."""
    save_token(ctx, _validate_git_service(ctx, service), token)


@auth_app.command("get")
def auth_get(
    ctx: typer.Context,
    service: str = Argument(..., help=f"Provedor: {', '.join(SUPPORTED_GIT_PROVIDERS)}"),
) -> None:
    """Exibe o status e o token mascarado de um provedor Git."""
    show_token(ctx, _validate_git_service(ctx, service))


@auth_app.command("delete")
def auth_delete(
    ctx: typer.Context,
    service: str = Argument(..., help=f"Provedor: {', '.join(SUPPORTED_GIT_PROVIDERS)}"),
) -> None:
    """Remove a credencial armazenada de um provedor Git."""
    remove_token(ctx, _validate_git_service(ctx, service))


@git_config_app.command("set-provider")
def config_set_provider(
    ctx: typer.Context,
    provider: str = Argument(
        ...,
        help=f"Provedor Git padrão: {', '.join(SUPPORTED_GIT_PROVIDERS)}",
    ),
) -> None:
    """Define o provedor Git padrão ('bitbucket' ou 'github') em config.toml."""
    as_json = is_json_mode(ctx)

    try:
        prov = validate_git_provider(provider)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    set_default_provider_config(prov)
    print_success(
        f"Provedor Git padrão definido com sucesso: [cyan]{prov}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "default_provider": prov},
    )


@git_config_app.command("get-provider")
def config_get_provider(ctx: typer.Context) -> None:
    """Exibe o provedor Git padrão atualmente configurado."""
    as_json = is_json_mode(ctx)
    prov = get_default_provider_config() or "bitbucket (padrão implícito)"

    if as_json:
        print_json({"default_provider": get_default_provider_config()})
    else:
        print_panel("Provedor Git Padrão", f"[bold]Provedor:[/bold] [cyan]{prov}[/cyan]")
