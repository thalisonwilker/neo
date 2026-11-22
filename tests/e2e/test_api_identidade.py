"""Testes de aceite (E2E) da API FastAPI do Neo (0037 tarefa 6, AC-1 a AC-9)."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

import neo.infrastructure.db.models  # noqa: F401
from neo.domain.identidade import ClerkIndisponivelError, Email, IdentidadeExterna
from neo.infrastructure.api_settings import ApiSettings
from neo.infrastructure.clerk import VerificadorDeTokenClerk
from neo.infrastructure.db import (
    Base,
    RepositorioDeListaDePermissaoSQLAlchemy,
    RepositorioDeUsuariosSQLAlchemy,
    criar_engine,
    criar_session_factory,
    verificar_conexao_banco,
)
from neo.interfaces.api import create_app


class _FakeJWKClient:
    def __init__(self, jwks: dict[str, dict[str, Any]]) -> None:
        self._jwks = jwks

    def get_jwk_set(self, refresh: bool = False) -> None:
        return None

    def get_signing_key_from_jwt(self, token: str) -> jwt.PyJWK:
        kid = jwt.get_unverified_header(token).get("kid")
        if not isinstance(kid, str) or kid not in self._jwks:
            raise jwt.PyJWKClientError("kid desconhecido")
        return jwt.PyJWK.from_dict(self._jwks[kid])


class _LeitorEmailEmMemoria:
    def __init__(self, mapa: dict[str, str], indisponivel: bool = False) -> None:
        self.mapa = mapa
        self.indisponivel = indisponivel
        self.chamadas: list[str] = []

    async def obter_email_principal(self, identidade: IdentidadeExterna) -> Email:
        self.chamadas.append(identidade.clerk_user_id)
        if self.indisponivel:
            raise ClerkIndisponivelError()
        return Email(self.mapa[identidade.clerk_user_id])


@dataclass
class _ApiTestHarness:
    client: httpx.AsyncClient
    priv_key: rsa.RSAPrivateKey
    repo_usuarios: RepositorioDeUsuariosSQLAlchemy
    repo_lista: RepositorioDeListaDePermissaoSQLAlchemy
    leitor_email: _LeitorEmailEmMemoria
    app: Any
    db_ok: bool = True

    def assinar(
        self,
        *,
        sub: str = "user_ok",
        iss: str = "https://clerk.test",
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
        return jwt.encode(payload, self.priv_key, algorithm="RS256", headers={"kid": "k1"})

    def headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def api_harness(tmp_path: Path) -> AsyncIterator[_ApiTestHarness]:
    """Cria app FastAPI ligada a SQLite async real e JWKS de teste em memoria."""
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk_dict = json.loads(RSAAlgorithm.to_jwk(priv.public_key()))
    jwk_dict["kid"] = "k1"

    engine = criar_engine(f"sqlite+aiosqlite:///{tmp_path / 'api_e2e.db'}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = criar_session_factory(engine)
    repo_usuarios = RepositorioDeUsuariosSQLAlchemy(session_factory)
    repo_lista = RepositorioDeListaDePermissaoSQLAlchemy(session_factory)
    leitor = _LeitorEmailEmMemoria(
        {
            "user_ok": "Thalyson@Gmail.com",
            "user_dup": "dup@example.com",
            "user_intruso": "intruso@example.com",
        }
    )
    verificador = VerificadorDeTokenClerk(
        jwks_url="https://clerk.test/.well-known/jwks.json",
        issuer="https://clerk.test",
        authorized_parties=("http://localhost:3100",),
        jwk_client=_FakeJWKClient({"k1": jwk_dict}),  # type: ignore[arg-type]
    )

    state = {"db_ok": True}

    async def _health() -> bool:
        if not state["db_ok"]:
            return False
        return await verificar_conexao_banco(engine)

    app = create_app(
        settings=ApiSettings(
            NEO_API_CORS_ORIGINS="http://localhost:3100",
            CLERK_ISSUER="https://clerk.test",
        ),
        verificador_de_token=verificador,
        leitor_de_email=leitor,
        repo_usuarios=repo_usuarios,
        repo_lista_permissao=repo_lista,
        health_check=_health,
    )

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://api.test") as client:
        harness = _ApiTestHarness(
            client=client,
            priv_key=priv,
            repo_usuarios=repo_usuarios,
            repo_lista=repo_lista,
            leitor_email=leitor,
            app=app,
        )

        async def _health_dinamico() -> bool:
            if not harness.db_ok:
                return False
            return await verificar_conexao_banco(engine)

        app.state.health_check = _health_dinamico
        yield harness

    await engine.dispose()


async def test_AC_1_health_sem_token_ok_e_erro_banco(api_harness: _ApiTestHarness) -> None:
    """AC-1: GET /health responde 200 sem token e 503 se banco cair."""
    res_ok = await api_harness.client.get("/health")
    assert res_ok.status_code == 200
    assert res_ok.json() == {"status": "ok", "db": "ok"}

    api_harness.db_ok = False
    res_erro = await api_harness.client.get("/health")
    assert res_erro.status_code == 503
    assert res_erro.json() == {"status": "erro", "db": "erro"}


async def test_AC_2_rejeita_pedidos_sem_token_valido(api_harness: _ApiTestHarness) -> None:
    """AC-2: /v1/* sem token, expirado, assinatura invalida, iss ou azp errado -> 401."""
    outra_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token_outra_assinatura = jwt.encode(
        {
            "sub": "user_ok",
            "iss": "https://clerk.test",
            "azp": "http://localhost:3100",
            "iat": int(time.time()),
            "exp": int(time.time()) + 300,
        },
        outra_priv,
        algorithm="RS256",
        headers={"kid": "k1"},
    )
    tokens_invalidos = [
        None,
        "token-invalido",
        api_harness.assinar(exp_delta=-10),
        token_outra_assinatura,
        api_harness.assinar(iss="https://errado.test"),
        api_harness.assinar(azp="https://evil.example"),
    ]

    for token in tokens_invalidos:
        headers = api_harness.headers(token) if token is not None else {}
        res_me = await api_harness.client.get("/v1/me", headers=headers)
        assert res_me.status_code == 401
        assert res_me.json()["erro"] == "token_invalido"

        res_pa = await api_harness.client.post(
            "/v1/primeiro-acesso",
            headers=headers,
            json={"nome_exibicao": "A", "espaco": {"nome": "B", "tipo": "trabalho"}},
        )
        assert res_pa.status_code == 401
        assert res_pa.json()["erro"] == "token_invalido"

    assert (
        await api_harness.repo_usuarios.buscar_por_identidade(IdentidadeExterna("user_ok")) is None
    )


async def test_AC_3_e_AC_5_primeiro_pedido_autorizado_e_reconhecimento(
    api_harness: _ApiTestHarness,
) -> None:
    """AC-3 e AC-5: cria Usuario na 1a chamada e reconhece sem ir ao Clerk apos remocao."""
    await api_harness.repo_lista.adicionar(Email("thalyson@gmail.com"))
    token = api_harness.assinar(sub="user_ok")

    res1 = await api_harness.client.get("/v1/me", headers=api_harness.headers(token))
    assert res1.status_code == 200
    body1 = res1.json()
    assert body1["email"] == "thalyson@gmail.com"
    assert body1["nome_exibicao"] is None
    assert body1["primeiro_acesso_concluido"] is False
    assert body1["espacos"] == []
    assert api_harness.leitor_email.chamadas == ["user_ok"]

    await api_harness.repo_lista.remover(Email("thalyson@gmail.com"))
    res2 = await api_harness.client.get("/v1/me", headers=api_harness.headers(token))
    assert res2.status_code == 200
    assert res2.json()["id"] == body1["id"]
    assert api_harness.leitor_email.chamadas == ["user_ok"]


async def test_AC_4_email_nao_autorizado_recebe_403(
    api_harness: _ApiTestHarness, caplog: pytest.LogCaptureFixture
) -> None:
    """AC-4: e-mail fora da Lista de permissao recebe 403 e nao cria Usuario."""
    token = api_harness.assinar(sub="user_intruso")

    with caplog.at_level(logging.WARNING):
        res_me = await api_harness.client.get("/v1/me", headers=api_harness.headers(token))

    assert res_me.status_code == 403
    assert res_me.json()["erro"] == "acesso_nao_liberado"
    assert (
        await api_harness.repo_usuarios.buscar_por_identidade(IdentidadeExterna("user_intruso"))
        is None
    )
    assert "intruso@example.com" not in caplog.text
    assert "i***@example.com" in caplog.text

    res_pa = await api_harness.client.post(
        "/v1/primeiro-acesso",
        headers=api_harness.headers(token),
        json={"nome_exibicao": "Intruso", "espaco": {"nome": "X", "tipo": "trabalho"}},
    )
    assert res_pa.status_code == 403
    assert res_pa.json()["erro"] == "acesso_nao_liberado"


async def test_AC_6_AC_7_AC_8_primeiro_acesso_validacoes_e_repeticao(
    api_harness: _ApiTestHarness,
) -> None:
    """AC-6, AC-7 e AC-8: conclui primeiro acesso (ignora extras), valida 422 e bloqueia 409."""
    await api_harness.repo_lista.adicionar(Email("thalyson@gmail.com"))
    token = api_harness.assinar(sub="user_ok")
    headers = api_harness.headers(token)

    invalidos = [
        ({"nome_exibicao": "   ", "espaco": {"nome": "Neo", "tipo": "trabalho"}}, "nome_exibicao"),
        (
            {"nome_exibicao": "a" * 61, "espaco": {"nome": "Neo", "tipo": "trabalho"}},
            "nome_exibicao",
        ),
        (
            {"nome_exibicao": "Thalyson", "espaco": {"nome": "  ", "tipo": "trabalho"}},
            "espaco.nome",
        ),
        (
            # Limite de 100 desde a 0040 (AC-6).
            {"nome_exibicao": "Thalyson", "espaco": {"nome": "b" * 101, "tipo": "trabalho"}},
            "espaco.nome",
        ),
        (
            {"nome_exibicao": "Thalyson", "espaco": {"nome": "Neo", "tipo": "invalido"}},
            "espaco.tipo",
        ),
    ]
    for payload, campo_esperado in invalidos:
        res_422 = await api_harness.client.post(
            "/v1/primeiro-acesso", headers=headers, json=payload
        )
        assert res_422.status_code == 422
        assert res_422.json()["erro"] == "dados_invalidos"
        assert res_422.json()["campo"] == campo_esperado

    res_ok = await api_harness.client.post(
        "/v1/primeiro-acesso",
        headers=headers,
        json={
            "nome_exibicao": "  Thalyson  ",
            "espaco": {"nome": "  Neo  ", "tipo": "trabalho"},
            "campo_extra_ignorado": "qualquer",
        },
    )
    assert res_ok.status_code == 201
    body_ok = res_ok.json()
    assert body_ok["primeiro_acesso_concluido"] is True
    assert body_ok["nome_exibicao"] == "Thalyson"
    assert len(body_ok["espacos"]) == 1
    assert body_ok["espacos"][0]["nome"] == "Neo"
    assert body_ok["espacos"][0]["tipo"] == "trabalho"

    res_409 = await api_harness.client.post(
        "/v1/primeiro-acesso",
        headers=headers,
        json={"nome_exibicao": "Novo", "espaco": {"nome": "Outro", "tipo": "pessoal"}},
    )
    assert res_409.status_code == 409
    assert res_409.json()["erro"] == "primeiro_acesso_ja_concluido"


async def test_AC_9_logs_sem_segredos_e_cors_restrito(
    api_harness: _ApiTestHarness, caplog: pytest.LogCaptureFixture
) -> None:
    """AC-9: log registra metodo/rota/status/duracao/request_id sem token/e-mail e CORS restrito."""
    await api_harness.repo_lista.adicionar(Email("thalyson@gmail.com"))
    token = api_harness.assinar(sub="user_ok")

    with caplog.at_level(logging.INFO):
        res_autorizado = await api_harness.client.get(
            "/v1/me",
            headers={**api_harness.headers(token), "Origin": "http://localhost:3100"},
        )
        res_sem_token = await api_harness.client.get(
            "/v1/me",
            headers={"Origin": "https://evil.example"},
        )

    assert res_autorizado.status_code == 200
    assert res_autorizado.headers.get("access-control-allow-origin") == "http://localhost:3100"
    assert "X-Request-ID" in res_autorizado.headers

    assert res_sem_token.status_code == 401
    assert res_sem_token.headers.get("access-control-allow-origin") is None
    assert api_harness.app.state.metricas_recusas["401"] >= 1

    logs_api = "\n".join(r.getMessage() for r in caplog.records if r.name.startswith("neo."))
    assert "metodo=GET rota=/v1/me status=200" in logs_api
    assert "duracao_ms=" in logs_api
    assert "request_id=" in logs_api
    assert token not in logs_api
    assert "thalyson@gmail.com" not in logs_api


async def test_bordas_concorrencia_e_clerk_indisponivel(api_harness: _ApiTestHarness) -> None:
    """Bordas: pedidos simultaneos no primeiro acesso criam 1 Usuario; Clerk fora -> 503."""
    await api_harness.repo_lista.adicionar(Email("dup@example.com"))
    token_dup = api_harness.assinar(sub="user_dup")

    r1, r2 = await asyncio.gather(
        api_harness.client.get("/v1/me", headers=api_harness.headers(token_dup)),
        api_harness.client.get("/v1/me", headers=api_harness.headers(token_dup)),
    )
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]

    api_harness.leitor_email.indisponivel = True
    token_intruso = api_harness.assinar(sub="user_intruso")
    r_503 = await api_harness.client.get("/v1/me", headers=api_harness.headers(token_intruso))
    assert r_503.status_code == 503
    assert r_503.json()["erro"] == "clerk_indisponivel"
