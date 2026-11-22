"""Verificador local de tokens JWT do Clerk via JWKS."""

from __future__ import annotations

import asyncio
from typing import Any

import jwt
from jwt import PyJWK, PyJWKClient, PyJWKClientError, PyJWTError

from neo.domain.identidade import IdentidadeExterna, TokenInvalidoError, TokenVerificado


class VerificadorDeTokenClerk:
    """Valida assinatura RS256 (JWKS), expiracao, `iss` e `azp` de tokens do Clerk."""

    def __init__(
        self,
        jwks_url: str,
        issuer: str,
        authorized_parties: tuple[str, ...] = (),
        *,
        jwk_client: PyJWKClient | None = None,
    ) -> None:
        self._jwks_url = jwks_url.strip()
        self._issuer = issuer.strip()
        self._authorized_parties = authorized_parties
        if jwk_client is not None:
            self._jwk_client: PyJWKClient | None = jwk_client
        elif self._jwks_url:
            self._jwk_client = PyJWKClient(self._jwks_url, cache_jwk_set=True, lifespan=300)
        else:
            self._jwk_client = None

    def _obter_chave_com_recarga(self, token: str) -> PyJWK:
        if self._jwk_client is None:
            raise TokenInvalidoError()
        try:
            return self._jwk_client.get_signing_key_from_jwt(token)
        except PyJWKClientError:
            try:
                self._jwk_client.get_jwk_set(refresh=True)
                return self._jwk_client.get_signing_key_from_jwt(token)
            except (PyJWKClientError, PyJWTError) as exc:
                raise TokenInvalidoError() from exc
        except PyJWTError as exc:
            raise TokenInvalidoError() from exc

    def _validar_claims(self, payload: dict[str, Any]) -> IdentidadeExterna:
        if self._authorized_parties:
            azp = payload.get("azp")
            if not isinstance(azp, str) or azp not in self._authorized_parties:
                raise TokenInvalidoError()
        sub = payload.get("sub")
        if not isinstance(sub, str) or not sub.strip():
            raise TokenInvalidoError()
        return IdentidadeExterna(sub)

    async def verificar(self, token: str) -> TokenVerificado:
        """Verifica assinatura e claims de confianca do token JWT do Clerk."""
        limpo = token.strip()
        if not limpo or not self._issuer or self._jwk_client is None:
            raise TokenInvalidoError()

        signing_key = await asyncio.to_thread(self._obter_chave_com_recarga, limpo)
        try:
            payload = jwt.decode(
                limpo,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self._issuer,
                options={"require": ["sub", "exp", "iss"], "verify_aud": False},
            )
        except PyJWTError as exc:
            raise TokenInvalidoError() from exc

        identidade = self._validar_claims(payload)
        return TokenVerificado(identidade=identidade)
