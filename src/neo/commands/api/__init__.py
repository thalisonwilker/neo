"""Comandos CLI do grupo `neo api` para gerir a Lista de permissao da API."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import typer

from neo.config import ExitCode
from neo.domain.identidade import (
    DadosInvalidosError,
    Email,
    EmailAutorizadoNaoEncontradoError,
)
from neo.output import console, print_error, print_json, print_success, print_table

if TYPE_CHECKING:
    from neo.application.identidade import GerenciarListaDePermissao

api_app = typer.Typer(
    name="api",
    help="Gerencia a Lista de permissão da API Neo.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _usar_json(ctx: typer.Context, local_json: bool) -> bool:
    obj = ctx.obj
    global_json = bool(getattr(obj, "json_mode", False)) if obj is not None else False
    return local_json or global_json


async def _executar_async[T](fn: Callable[[GerenciarListaDePermissao], Awaitable[T]]) -> T:
    from neo.application.identidade import GerenciarListaDePermissao
    from neo.infrastructure.api_settings import obter_api_settings
    from neo.infrastructure.db import (
        RepositorioDeListaDePermissaoSQLAlchemy,
        criar_engine,
        criar_session_factory,
    )

    database_url = obter_api_settings().neo_database_url
    engine = criar_engine(database_url)
    try:
        session_factory = criar_session_factory(engine)
        repo = RepositorioDeListaDePermissaoSQLAlchemy(session_factory)
        caso_de_uso = GerenciarListaDePermissao(repo)
        return await fn(caso_de_uso)
    finally:
        await engine.dispose()


def _rodar[T](
    fn: Callable[[GerenciarListaDePermissao], Awaitable[T]],
    *,
    as_json: bool,
) -> T:
    try:
        return asyncio.run(_executar_async(fn))
    except ModuleNotFoundError as exc:
        print_error(
            "Dependências da API não instaladas. Instale com `neo-cmd[api]`.",
            as_json=as_json,
            code=int(ExitCode.ERROR),
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc
    except (DadosInvalidosError, EmailAutorizadoNaoEncontradoError):
        raise
    except Exception as exc:
        print_error(
            f"Falha ao acessar o banco da API: {exc}",
            as_json=as_json,
            code=int(ExitCode.ERROR),
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc


@api_app.command("permitir")
def permitir_email(
    ctx: typer.Context,
    email: str = typer.Argument(..., help="E-mail autorizado a cadastrar Usuário no Neo."),
    json_output: bool = typer.Option(False, "--json", help="Emite saída em JSON."),
) -> None:
    """Adiciona um e-mail à Lista de permissão da API Neo."""
    as_json = _usar_json(ctx, json_output)
    try:
        Email(email)
    except DadosInvalidosError as exc:
        print_error(exc.mensagem, as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    item, criado = _rodar(lambda uc: uc.permitir(email), as_json=as_json)
    mensagem = (
        f"E-mail autorizado: {item.email.valor}"
        if criado
        else f"E-mail já estava autorizado: {item.email.valor}"
    )
    print_success(
        mensagem,
        as_json=as_json,
        json_payload={"email": item.email.valor, "criado": criado},
    )


@api_app.command("permissoes")
def listar_permissoes(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Emite saída em JSON."),
) -> None:
    """Lista os e-mails atualmente autorizados na Lista de permissão."""
    as_json = _usar_json(ctx, json_output)
    itens = _rodar(lambda uc: uc.listar(), as_json=as_json)
    if as_json:
        print_json(
            [{"email": item.email.valor, "criado_em": item.criado_em.isoformat()} for item in itens]
        )
        return

    if not itens:
        console.print("Nenhum e-mail na lista de permissão.")
        return

    print_table(
        "Lista de permissão da API Neo",
        ["E-mail", "Autorizado em"],
        [[item.email.valor, item.criado_em.strftime("%Y-%m-%d %H:%M UTC")] for item in itens],
    )


@api_app.command("remover-permissao")
def remover_permissao(
    ctx: typer.Context,
    email: str = typer.Argument(..., help="E-mail a remover da Lista de permissão."),
    json_output: bool = typer.Option(False, "--json", help="Emite saída em JSON."),
) -> None:
    """Remove um e-mail da Lista de permissão sem afetar Usuários já registrados."""
    as_json = _usar_json(ctx, json_output)
    try:
        Email(email)
    except DadosInvalidosError as exc:
        print_error(exc.mensagem, as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from exc

    try:
        removido = _rodar(lambda uc: uc.remover(email), as_json=as_json)
    except EmailAutorizadoNaoEncontradoError as exc:
        print_error(exc.mensagem, as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND)) from exc

    print_success(
        f"Permissão removida: {removido.valor}",
        as_json=as_json,
        json_payload={"email": removido.valor, "removido": True},
    )
