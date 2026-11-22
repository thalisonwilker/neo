"""Mapeamento padronizado de erros de dominio e validacao para respostas JSON."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from neo.domain.identidade import (
    AcessoNaoLiberadoError,
    ClerkIndisponivelError,
    DadosInvalidosError,
    PrimeiroAcessoJaConcluidoError,
    PrimeiroAcessoPendenteError,
    TokenInvalidoError,
)


def _json_erro(
    status_code: int,
    erro: str,
    mensagem: str,
    *,
    campo: str | None = None,
) -> JSONResponse:
    conteudo: dict[str, str] = {"erro": erro, "mensagem": mensagem}
    if campo is not None:
        conteudo["campo"] = campo
    return JSONResponse(status_code=status_code, content=conteudo)


def registrar_error_handlers(app: FastAPI) -> None:
    """Registra handlers globais mantendo o contrato `{erro, mensagem}` em pt-BR."""

    @app.exception_handler(TokenInvalidoError)
    async def _tratar_token_invalido(_: Request, exc: TokenInvalidoError) -> JSONResponse:
        return _json_erro(401, exc.codigo, exc.mensagem)

    @app.exception_handler(AcessoNaoLiberadoError)
    async def _tratar_acesso_nao_liberado(_: Request, exc: AcessoNaoLiberadoError) -> JSONResponse:
        return _json_erro(403, exc.codigo, exc.mensagem)

    @app.exception_handler(PrimeiroAcessoJaConcluidoError)
    async def _tratar_primeiro_acesso_concluido(
        _: Request, exc: PrimeiroAcessoJaConcluidoError
    ) -> JSONResponse:
        return _json_erro(409, exc.codigo, exc.mensagem)

    @app.exception_handler(PrimeiroAcessoPendenteError)
    async def _tratar_primeiro_acesso_pendente(
        _: Request, exc: PrimeiroAcessoPendenteError
    ) -> JSONResponse:
        return _json_erro(409, exc.codigo, exc.mensagem)

    @app.exception_handler(DadosInvalidosError)
    async def _tratar_dados_invalidos(_: Request, exc: DadosInvalidosError) -> JSONResponse:
        return _json_erro(422, exc.codigo, exc.mensagem, campo=exc.campo)

    @app.exception_handler(ClerkIndisponivelError)
    async def _tratar_clerk_indisponivel(_: Request, exc: ClerkIndisponivelError) -> JSONResponse:
        return _json_erro(503, exc.codigo, exc.mensagem)

    @app.exception_handler(RequestValidationError)
    async def _tratar_validacao_request(_: Request, exc: RequestValidationError) -> JSONResponse:
        campo: str | None = None
        erros = exc.errors()
        if erros:
            loc = [str(parte) for parte in erros[0].get("loc", ()) if parte != "body"]
            if loc:
                campo = ".".join(loc)
        return _json_erro(
            422,
            "dados_invalidos",
            "Verifique os dados informados e tente novamente.",
            campo=campo,
        )
