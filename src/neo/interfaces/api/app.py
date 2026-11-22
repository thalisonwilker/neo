"""Fabrica da aplicacao FastAPI do Neo."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neo.domain.identidade import (
    LeitorDeEmailExterno,
    RepositorioDeListaDePermissao,
    RepositorioDeUsuarios,
    VerificadorDeToken,
)
from neo.infrastructure.api_settings import ApiSettings, obter_api_settings
from neo.infrastructure.clerk import LeitorDeEmailClerk, VerificadorDeTokenClerk
from neo.infrastructure.db import (
    RepositorioDeListaDePermissaoSQLAlchemy,
    RepositorioDeUsuariosSQLAlchemy,
    criar_engine,
    criar_session_factory,
    verificar_conexao_banco,
)
from neo.interfaces.api.error_handlers import registrar_error_handlers
from neo.interfaces.api.middleware import ObservabilidadeMiddleware
from neo.interfaces.api.routes import router_raiz, router_v1


def create_app(
    settings: ApiSettings | None = None,
    *,
    verificador_de_token: VerificadorDeToken | None = None,
    leitor_de_email: LeitorDeEmailExterno | None = None,
    repo_usuarios: RepositorioDeUsuarios | None = None,
    repo_lista_permissao: RepositorioDeListaDePermissao | None = None,
    health_check: Callable[[], Awaitable[bool]] | None = None,
) -> FastAPI:
    """Constroi a instancia FastAPI com CORS, observabilidade, erros e rotas v1."""
    cfg = settings or obter_api_settings()

    @asynccontextmanager
    async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
        engine = None
        if repo_usuarios is None or repo_lista_permissao is None or health_check is None:
            engine = criar_engine(cfg.neo_database_url)
            session_factory = criar_session_factory(engine)
            if repo_usuarios is None:
                fastapi_app.state.repo_usuarios = RepositorioDeUsuariosSQLAlchemy(session_factory)
            if repo_lista_permissao is None:
                fastapi_app.state.repo_lista_permissao = RepositorioDeListaDePermissaoSQLAlchemy(
                    session_factory
                )
            if health_check is None:
                fastapi_app.state.health_check = lambda: verificar_conexao_banco(engine)

        if verificador_de_token is None:
            fastapi_app.state.verificador_de_token = VerificadorDeTokenClerk(
                jwks_url=cfg.clerk_jwks_url,
                issuer=cfg.clerk_issuer,
                authorized_parties=cfg.clerk_authorized_parties,
            )
        if leitor_de_email is None:
            fastapi_app.state.leitor_de_email = LeitorDeEmailClerk(
                secret_key=cfg.clerk_secret_key,
                base_url=cfg.clerk_api_base_url,
            )

        try:
            yield
        finally:
            if engine is not None:
                await engine.dispose()

    fastapi_app = FastAPI(
        title="Neo API",
        version="0.1.0",
        description="API REST do Neo para identidade, espacos e painel de projetos.",
        lifespan=lifespan,
    )
    fastapi_app.state.metricas_recusas = {"401": 0, "403": 0}
    if verificador_de_token is not None:
        fastapi_app.state.verificador_de_token = verificador_de_token
    if leitor_de_email is not None:
        fastapi_app.state.leitor_de_email = leitor_de_email
    if repo_usuarios is not None:
        fastapi_app.state.repo_usuarios = repo_usuarios
    if repo_lista_permissao is not None:
        fastapi_app.state.repo_lista_permissao = repo_lista_permissao
    if health_check is not None:
        fastapi_app.state.health_check = health_check

    fastapi_app.add_middleware(ObservabilidadeMiddleware)
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    registrar_error_handlers(fastapi_app)
    fastapi_app.include_router(router_raiz)
    fastapi_app.include_router(router_v1)
    return fastapi_app


app = create_app()
