"""Schemas Pydantic de entrada e saida da API Neo v1."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StrictBool, StrictInt

from neo.domain.identidade import Espaco, Usuario


class EspacoResponse(BaseModel):
    """Representacao serializada de um Espaco do Usuario."""

    id: UUID
    nome: str
    tipo: str
    criado_em: datetime
    meta_semanal: int
    agentes_sugeridos: bool


class UsuarioResponse(BaseModel):
    """Representacao serializada do Usuario e seus Espacos."""

    id: UUID
    email: str
    nome_exibicao: str | None
    primeiro_acesso_concluido: bool
    espacos: list[EspacoResponse]


class EspacoInput(BaseModel):
    """Entrada para criacao do primeiro Espaco."""

    model_config = ConfigDict(extra="ignore")

    nome: str
    tipo: str


class PrimeiroAcessoRequest(BaseModel):
    """Payload de conclusao do Primeiro acesso (campos extras ignorados)."""

    model_config = ConfigDict(extra="ignore")

    nome_exibicao: str
    espaco: EspacoInput


class CriarEspacoRequest(BaseModel):
    """Payload de `POST /v1/espacos` (0040); campos extras ignorados.

    `meta_semanal` e estrita: decimais, texto e booleanos viram 422 no campo `meta_semanal`.
    """

    model_config = ConfigDict(extra="ignore")

    nome: str
    tipo: str
    meta_semanal: StrictInt | None = None
    agentes_sugeridos: StrictBool = False


class HealthResponse(BaseModel):
    """Resposta da rota de saude `/health`."""

    status: str
    db: str


def espaco_para_response(espaco: Espaco) -> EspacoResponse:
    """Converte a entidade Espaco em schema de resposta da API."""
    return EspacoResponse(
        id=espaco.id,
        nome=espaco.nome.valor,
        tipo=espaco.tipo.value,
        criado_em=espaco.criado_em,
        meta_semanal=espaco.meta_semanal.valor,
        agentes_sugeridos=espaco.agentes_sugeridos,
    )


def usuario_para_response(usuario: Usuario) -> UsuarioResponse:
    """Converte agregado Usuario do dominio em schema de resposta da API."""
    return UsuarioResponse(
        id=usuario.id,
        email=usuario.email.valor,
        nome_exibicao=usuario.nome_exibicao.valor if usuario.nome_exibicao else None,
        primeiro_acesso_concluido=usuario.primeiro_acesso_concluido,
        espacos=[espaco_para_response(e) for e in usuario.espacos],
    )
