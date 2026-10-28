"""Operações de credenciais compartilhadas por `neo git config auth` e `neo tasks config`."""

from __future__ import annotations

import typer
from keyring.errors import KeyringError

from neo.config import (
    delete_credential,
    get_credential,
    get_credential_source,
    mask_token,
    set_credential,
)
from neo.output import print_error, print_json, print_panel, print_success


def is_json_mode(ctx: typer.Context) -> bool:
    return getattr(ctx.obj, "json_mode", False) if ctx.obj else False


def save_token(ctx: typer.Context, svc: str, token: str | None) -> None:
    """Grava o token de `svc` (prompt oculto se `token` for omitido)."""
    as_json = is_json_mode(ctx)

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


def show_token(ctx: typer.Context, svc: str) -> None:
    """Exibe o status e o token mascarado de `svc`."""
    as_json = is_json_mode(ctx)
    token = get_credential(svc)
    source = get_credential_source(svc)

    if not token:
        print_error(
            f"Serviço '{svc}' não possui credenciais configuradas.",
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


def remove_token(ctx: typer.Context, svc: str) -> None:
    """Remove a credencial armazenada de `svc`."""
    as_json = is_json_mode(ctx)

    if delete_credential(svc):
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
