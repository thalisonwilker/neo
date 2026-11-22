"""Dependencias FastAPI para autenticacao e resolucao de contexto."""

from __future__ import annotations

from typing import cast

from fastapi import Request

from neo.domain.identidade import IdentidadeExterna, TokenInvalidoError, VerificadorDeToken


async def obter_identidade_autenticada(request: Request) -> IdentidadeExterna:
    """Extrai o Bearer token do cabecalho Authorization e valida via VerificadorDeToken."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise TokenInvalidoError()

    esquema, separador, token = auth_header.strip().partition(" ")
    if separador != " " or esquema.lower() != "bearer" or not token.strip():
        raise TokenInvalidoError()

    verificador = cast(VerificadorDeToken, request.app.state.verificador_de_token)
    resultado = await verificador.verificar(token.strip())
    return resultado.identidade
