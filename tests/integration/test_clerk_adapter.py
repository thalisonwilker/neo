"""Testes de integracao do adapter Clerk (0037 tarefa 5, AC-2 a AC-5)."""

from __future__ import annotations

import json
import time
from typing import Any

import httpx
import jwt
import pytest
import respx
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from neo.domain.identidade import (
    ClerkIndisponivelError,
    Email,
    IdentidadeExterna,
    TokenInvalidoError,
)
from neo.infrastructure.clerk import LeitorDeEmailClerk, VerificadorDeTokenClerk


def _gerar_par_rsa(kid: str) -> tuple[rsa.RSAPrivateKey, dict[str, Any]]:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk_dict = json.loads(RSAAlgorithm.to_jwk(priv.public_key()))
    jwk_dict["kid"] = kid
    jwk_dict["use"] = "sig"
    jwk_dict["alg"] = "RS256"
    return priv, jwk_dict


def _assinar(
    priv: rsa.RSAPrivateKey,
    kid: str,
    *,
    sub: str = "user_abc",
    iss: str = "https://clerk.example",
    azp: str | None = "http://localhost:3100",
    exp_delta: int = 300,
) -> str:
    agora = int(time.time())
    payload: dict[str, Any] = {
        "sub": sub,
        "iss": iss,
        "iat": agora,
        "exp": agora + exp_delta,
    }
    if azp is not None:
        payload["azp"] = azp
    return jwt.encode(payload, priv, algorithm="RS256", headers={"kid": kid})


class FakeJWKClient:
    """Simula PyJWKClient em memoria com suporte a refresh unico em rotacao de kid."""

    def __init__(self, snapshots: list[dict[str, dict[str, Any]]]) -> None:
        self._snapshots = snapshots
        self._idx = 0
        self.refresh_count = 0

    def get_jwk_set(self, refresh: bool = False) -> None:
        if refresh:
            self.refresh_count += 1
            if self._idx + 1 < len(self._snapshots):
                self._idx += 1

    def get_signing_key_from_jwt(self, token: str) -> jwt.PyJWK:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        atual = self._snapshots[self._idx]
        if not isinstance(kid, str) or kid not in atual:
            raise jwt.PyJWKClientError(f"kid desconhecido: {kid}")
        return jwt.PyJWK.from_dict(atual[kid])


async def test_AC_2_verificador_token_clerk_valido_e_rejeicoes() -> None:
    """AC-2: aceita JWT valido e recusa expirado, assinatura errada, iss e azp invalidos."""
    priv1, jwk1 = _gerar_par_rsa("kid-1")
    priv_outro, _ = _gerar_par_rsa("kid-1")
    client = FakeJWKClient([{"kid-1": jwk1}])

    verificador = VerificadorDeTokenClerk(
        jwks_url="https://clerk.example/.well-known/jwks.json",
        issuer="https://clerk.example",
        authorized_parties=("http://localhost:3100",),
        jwk_client=client,  # type: ignore[arg-type]
    )

    token_valido = _assinar(priv1, "kid-1", sub="user_99")
    resultado = await verificador.verificar(token_valido)
    assert resultado.identidade == IdentidadeExterna("user_99")

    invalidos = [
        "",
        "nao-e-jwt",
        "a.b.c",
        _assinar(priv1, "kid-1", exp_delta=-30),
        _assinar(priv_outro, "kid-1"),
        _assinar(priv1, "kid-1", iss="https://evil.example"),
        _assinar(priv1, "kid-1", azp="https://evil.example"),
        _assinar(priv1, "kid-1", azp=None),
        _assinar(priv1, "kid-1", sub=""),
    ]
    for token_ruim in invalidos:
        with pytest.raises(TokenInvalidoError):
            await verificador.verificar(token_ruim)


async def test_rotacao_kid_recarrega_jwks_uma_vez() -> None:
    """Borda: kid novo dispara uma recarga do JWKS antes de aceitar ou recusar."""
    _, jwk1 = _gerar_par_rsa("kid-1")
    priv2, jwk2 = _gerar_par_rsa("kid-2")
    client = FakeJWKClient([{"kid-1": jwk1}, {"kid-1": jwk1, "kid-2": jwk2}])

    verificador = VerificadorDeTokenClerk(
        jwks_url="https://clerk.example/.well-known/jwks.json",
        issuer="https://clerk.example",
        authorized_parties=("http://localhost:3100",),
        jwk_client=client,  # type: ignore[arg-type]
    )

    token_kid2 = _assinar(priv2, "kid-2", sub="user_rot")
    resultado = await verificador.verificar(token_kid2)
    assert resultado.identidade == IdentidadeExterna("user_rot")
    assert client.refresh_count == 1

    # kid completamente desconhecido recarrega uma vez e recusa com TokenInvalidoError
    token_desconhecido = _assinar(priv2, "kid-inexistente")
    with pytest.raises(TokenInvalidoError):
        await verificador.verificar(token_desconhecido)
    assert client.refresh_count == 2


@respx.mock
async def test_AC_3_AC_4_AC_5_leitor_email_clerk_e_indisponibilidade() -> None:
    """AC-3 a AC-5: extrai primary_email_address_id e trata indisponibilidade com 503."""
    leitor = LeitorDeEmailClerk("sk_test_123", base_url="https://api.clerk.test")

    route = respx.get("https://api.clerk.test/v1/users/user_1").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "user_1",
                "primary_email_address_id": "idn_2",
                "email_addresses": [
                    {"id": "idn_1", "email_address": "secundario@example.com"},
                    {"id": "idn_2", "email_address": "Principal@Example.com"},
                ],
            },
        )
    )
    email = await leitor.obter_email_principal(IdentidadeExterna("user_1"))
    assert email == Email("principal@example.com")
    assert route.calls[0].request.headers["Authorization"] == "Bearer sk_test_123"

    respx.get("https://api.clerk.test/v1/users/user_err").mock(
        return_value=httpx.Response(503, json={"error": "unavailable"})
    )
    with pytest.raises(ClerkIndisponivelError):
        await leitor.obter_email_principal(IdentidadeExterna("user_err"))

    respx.get("https://api.clerk.test/v1/users/user_timeout").mock(
        side_effect=httpx.ConnectTimeout("timeout")
    )
    with pytest.raises(ClerkIndisponivelError):
        await leitor.obter_email_principal(IdentidadeExterna("user_timeout"))
