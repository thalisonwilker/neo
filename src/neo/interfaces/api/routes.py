"""Rotas HTTP da API Neo (/health e /v1/*)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from neo.application.identidade import ConcluirPrimeiroAcesso, CriarEspaco, ObterOuCriarUsuario
from neo.domain.identidade import (
    IdentidadeExterna,
    LeitorDeEmailExterno,
    RepositorioDeListaDePermissao,
    RepositorioDeUsuarios,
)
from neo.interfaces.api.deps import obter_identidade_autenticada
from neo.interfaces.api.schemas import (
    CriarEspacoRequest,
    EspacoResponse,
    HealthResponse,
    PrimeiroAcessoRequest,
    UsuarioResponse,
    espaco_para_response,
    usuario_para_response,
)

router_raiz = APIRouter()
router_v1 = APIRouter(prefix="/v1")


def _criar_caso_obter_usuario(request: Request) -> ObterOuCriarUsuario:
    return ObterOuCriarUsuario(
        usuarios=cast(RepositorioDeUsuarios, request.app.state.repo_usuarios),
        lista_permissao=cast(
            RepositorioDeListaDePermissao,
            request.app.state.repo_lista_permissao,
        ),
        leitor_email=cast(LeitorDeEmailExterno, request.app.state.leitor_de_email),
    )


@router_raiz.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health(request: Request) -> JSONResponse:
    """Verifica saude basica da API e conectividade com o banco."""
    check = cast(Callable[[], Awaitable[bool]], request.app.state.health_check)
    db_ok = await check()
    if db_ok:
        return JSONResponse(status_code=200, content={"status": "ok", "db": "ok"})
    return JSONResponse(status_code=503, content={"status": "erro", "db": "erro"})


@router_v1.get("/me", response_model=UsuarioResponse, tags=["Identidade"])
async def obter_me(
    request: Request,
    identidade: Annotated[IdentidadeExterna, Depends(obter_identidade_autenticada)],
) -> UsuarioResponse:
    """Retorna o Usuario autenticado, criando-o no primeiro pedido autorizado."""
    caso_de_uso = _criar_caso_obter_usuario(request)
    usuario = await caso_de_uso.executar(identidade)
    return usuario_para_response(usuario)


@router_v1.post(
    "/primeiro-acesso",
    response_model=UsuarioResponse,
    status_code=201,
    tags=["Identidade"],
)
async def concluir_primeiro_acesso(
    request: Request,
    body: PrimeiroAcessoRequest,
    identidade: Annotated[IdentidadeExterna, Depends(obter_identidade_autenticada)],
) -> UsuarioResponse:
    """Conclui o Primeiro acesso definindo Nome de exibicao e criando o primeiro Espaco."""
    obter_ou_criar = _criar_caso_obter_usuario(request)
    caso_de_uso = ConcluirPrimeiroAcesso(
        usuarios=cast(RepositorioDeUsuarios, request.app.state.repo_usuarios),
        obter_ou_criar=obter_ou_criar,
    )
    usuario = await caso_de_uso.executar(
        identidade=identidade,
        nome_exibicao_bruto=body.nome_exibicao,
        nome_espaco_bruto=body.espaco.nome,
        tipo_espaco_bruto=body.espaco.tipo,
    )
    return usuario_para_response(usuario)


@router_v1.post(
    "/espacos",
    response_model=EspacoResponse,
    status_code=201,
    tags=["Identidade"],
)
async def criar_espaco(
    request: Request,
    body: CriarEspacoRequest,
    identidade: Annotated[IdentidadeExterna, Depends(obter_identidade_autenticada)],
) -> EspacoResponse:
    """Cria um novo Espaco do Usuario que ja concluiu o Primeiro acesso (0040)."""
    caso_de_uso = CriarEspaco(
        usuarios=cast(RepositorioDeUsuarios, request.app.state.repo_usuarios),
        obter_ou_criar=_criar_caso_obter_usuario(request),
    )
    espaco = await caso_de_uso.executar(
        identidade=identidade,
        nome_bruto=body.nome,
        tipo_bruto=body.tipo,
        meta_semanal_bruta=body.meta_semanal,
        agentes_sugeridos=body.agentes_sugeridos,
    )
    return espaco_para_response(espaco)
