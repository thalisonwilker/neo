"""Comandos de gerenciamento de configurações e credenciais (`neo config`)."""

from __future__ import annotations

import typer
from keyring.errors import KeyringError
from typer import Argument, Option

from neo.config import (
    DEFAULT_CONFIG_FILE,
    SUPPORTED_GIT_PROVIDERS,
    SUPPORTED_SERVICES,
    delete_credential,
    get_all_services_status,
    get_credential,
    get_credential_source,
    get_default_provider_config,
    mask_token,
    set_credential,
    set_default_provider_config,
    validate_git_provider,
    validate_service,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table

config_app = typer.Typer(
    name="config",
    help="Gerenciamento de configurações e credenciais do Neo.",
    no_args_is_help=True,
)

auth_app = typer.Typer(
    name="auth",
    help="Gerencia tokens de autenticação (Bitbucket, Shortcut).",
    no_args_is_help=True,
)
config_app.add_typer(auth_app, name="auth")


@auth_app.command("set")
def auth_set(
    ctx: typer.Context,
    service: str = Argument(..., help=f"Serviço para autenticar: {', '.join(SUPPORTED_SERVICES)}"),
    token: str = Option(
        None,
        "--token",
        "-t",
        help="Token de acesso da API. Se omitido, solicita via prompt seguro.",
    ),
) -> None:
    """Configura o token de autenticação de um serviço de forma segura."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False

    try:
        svc = validate_service(service)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1)

    if not token:
        if as_json:
            print_error(
                "A flag --token é obrigatória quando o modo --json está ativo.",
                as_json=True,
                code=1,
            )
            raise typer.Exit(code=1)
        token = typer.prompt(f"Digite o token para '{svc}'", hide_input=True)

    try:
        set_credential(svc, token)
        source = get_credential_source(svc)
        print_success(
            f"Token para o serviço '{svc}' configurado com sucesso (armazenado via {source})!",
            as_json=as_json,
            json_payload={"status": "success", "service": svc, "source": source},
        )
    except (KeyringError, OSError, RuntimeError, ValueError) as e:
        print_error(f"Falha ao salvar credencial: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e


@auth_app.command("get")
def auth_get(
    ctx: typer.Context,
    service: str = Argument(..., help=f"Serviço: {', '.join(SUPPORTED_SERVICES)}"),
) -> None:
    """Exibe o status e o token mascarado de um serviço."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False

    try:
        svc = validate_service(service)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1)

    token = get_credential(svc)
    source = get_credential_source(svc)

    if not token:
        msg = f"Serviço '{svc}' não possui credenciais configuradas."
        print_error(
            msg,
            as_json=as_json,
            json_payload={
                "service": svc,
                "configured": False,
                "source": None,
                "masked_token": None,
            },
            code=1,
        )
        raise typer.Exit(code=1)

    masked = mask_token(token)
    if as_json:
        print_json(
            {
                "service": svc,
                "configured": True,
                "source": source,
                "masked_token": masked,
            }
        )
    else:
        print_panel(
            f"Autenticação: {svc}",
            f"[bold]Status:[/bold] [green]Configurado[/green]\n"
            f"[bold]Origem:[/bold] {source}\n"
            f"[bold]Token:[/bold] {masked}",
        )


@auth_app.command("delete")
def auth_delete(
    ctx: typer.Context,
    service: str = Argument(..., help=f"Serviço: {', '.join(SUPPORTED_SERVICES)}"),
) -> None:
    """Remove a credencial armazenada de um serviço."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False

    try:
        svc = validate_service(service)
    except ValueError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1)

    deleted = delete_credential(svc)
    if deleted:
        print_success(
            f"Credencial para o serviço '{svc}' removida com sucesso.",
            as_json=as_json,
            json_payload={"status": "success", "service": svc, "deleted": True},
        )
    else:
        print_error(
            f"Nenhuma credencial encontrada para remover no serviço '{svc}'.",
            as_json=as_json,
            json_payload={"status": "error", "service": svc, "deleted": False},
            code=1,
        )
        raise typer.Exit(code=1)


@config_app.command("set-provider")
def config_set_provider(
    ctx: typer.Context,
    provider: str = Argument(
        ...,
        help=f"Provedor Git padrão: {', '.join(SUPPORTED_GIT_PROVIDERS)}",
    ),
) -> None:
    """Define o provedor Git padrão ('bitbucket' ou 'github') em config.toml."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False

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


@config_app.command("get-provider")
def config_get_provider(ctx: typer.Context) -> None:
    """Exibe o provedor Git padrão atualmente configurado."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov = get_default_provider_config() or "bitbucket (padrão implícito)"

    if as_json:
        print_json({"default_provider": get_default_provider_config()})
    else:
        print_panel("Provedor Git Padrão", f"[bold]Provedor:[/bold] [cyan]{prov}[/cyan]")


@config_app.command("show")
def config_show(ctx: typer.Context) -> None:
    """Exibe o status geral das configurações e credenciais do Neo."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    statuses = get_all_services_status()
    default_provider = get_default_provider_config() or "bitbucket"

    if as_json:
        print_json(
            {
                "config_file": str(DEFAULT_CONFIG_FILE),
                "default_provider": default_provider,
                "services": statuses,
            }
        )
    else:
        columns = ["Serviço", "Status", "Origem", "Token Mascarado"]
        rows: list[list[str]] = []
        for svc, info in statuses.items():
            status_str = (
                "[bold green]Configurado[/bold green]"
                if info["configured"]
                else "[dim]Não configurado[/dim]"
            )
            source_str = str(info["source"]) if info["source"] else "-"
            token_str = str(info["masked_token"]) if info["masked_token"] else "-"
            rows.append([svc, status_str, source_str, token_str])

        print_table("Status de Autenticação do Neo", columns, rows)
        print_panel(
            "Provedor Git Ativo",
            f"[bold]Provedor padrão:[/bold] [cyan]{default_provider}[/cyan]",
        )
