"""Testes de aceite (E2E) da criacao de Espaco na API (0040 tarefa 4, AC-1 a AC-6)."""

from __future__ import annotations

from typing import Any

import pytest

# O fixture `api_harness` (app real, SQLite async, JWKS em memoria) vem do conftest.py.
from test_api_identidade import _ApiTestHarness

from neo.domain.identidade import Email


async def _usuario_pronto(h: _ApiTestHarness, concluir: bool = True) -> dict[str, str]:
    await h.repo_lista.adicionar(Email("thalyson@gmail.com"))
    headers = h.headers(h.assinar())
    if concluir:
        res = await h.client.post(
            "/v1/primeiro-acesso",
            json={"nome_exibicao": "Thalyson", "espaco": {"nome": "Neo", "tipo": "trabalho"}},
            headers=headers,
        )
        assert res.status_code == 201
    else:
        assert (await h.client.get("/v1/me", headers=headers)).status_code == 200
    return headers


async def _espacos(h: _ApiTestHarness, headers: dict[str, str]) -> list[dict[str, Any]]:
    res = await h.client.get("/v1/me", headers=headers)
    assert res.status_code == 200
    espacos: list[dict[str, Any]] = res.json()["espacos"]
    return espacos


async def test_0040_AC_1_criar_espaco(api_harness: _ApiTestHarness) -> None:
    headers = await _usuario_pronto(api_harness)
    res = await api_harness.client.post(
        "/v1/espacos",
        json={
            "nome": "  Faculdade  ",
            "tipo": "estudos",
            "meta_semanal": 12,
            "agentes_sugeridos": True,
            "extra": "ignorado",
        },
        headers=headers,
    )
    assert res.status_code == 201
    corpo = res.json()
    assert set(corpo) == {"id", "nome", "tipo", "meta_semanal", "agentes_sugeridos", "criado_em"}
    assert corpo["nome"] == "Faculdade"
    assert corpo["tipo"] == "estudos"
    assert corpo["meta_semanal"] == 12
    assert corpo["agentes_sugeridos"] is True

    espacos = await _espacos(api_harness, headers)
    assert [e["nome"] for e in espacos] == ["Neo", "Faculdade"]
    assert espacos[-1]["id"] == corpo["id"]


async def test_0040_AC_2_meta_e_agentes_omitidos(api_harness: _ApiTestHarness) -> None:
    headers = await _usuario_pronto(api_harness)
    res = await api_harness.client.post(
        "/v1/espacos", json={"nome": "Oficina", "tipo": "hobbies"}, headers=headers
    )
    assert res.status_code == 201
    assert res.json()["meta_semanal"] == 8
    assert res.json()["agentes_sugeridos"] is False


@pytest.mark.parametrize(
    ("corpo", "campo"),
    [
        ({"nome": "", "tipo": "trabalho"}, "nome"),
        ({"nome": "   ", "tipo": "trabalho"}, "nome"),
        ({"nome": "x" * 101, "tipo": "trabalho"}, "nome"),
        ({"nome": "Ok", "tipo": "lazer"}, "tipo"),
        ({"nome": "Ok", "tipo": "trabalho", "meta_semanal": 0}, "meta_semanal"),
        ({"nome": "Ok", "tipo": "trabalho", "meta_semanal": 169}, "meta_semanal"),
        ({"nome": "Ok", "tipo": "trabalho", "meta_semanal": 12.5}, "meta_semanal"),
        ({"nome": "Ok", "tipo": "trabalho", "meta_semanal": "12"}, "meta_semanal"),
    ],
)
async def test_0040_AC_3_dados_invalidos(
    api_harness: _ApiTestHarness, corpo: dict[str, Any], campo: str
) -> None:
    headers = await _usuario_pronto(api_harness)
    res = await api_harness.client.post("/v1/espacos", json=corpo, headers=headers)
    assert res.status_code == 422
    assert res.json()["erro"] == "dados_invalidos"
    assert res.json()["campo"] == campo
    assert len(await _espacos(api_harness, headers)) == 1


async def test_0040_AC_3_nome_de_100_caracteres_apos_trim_e_aceito(
    api_harness: _ApiTestHarness,
) -> None:
    headers = await _usuario_pronto(api_harness)
    res = await api_harness.client.post(
        "/v1/espacos", json={"nome": "  " + "n" * 100 + "  ", "tipo": "pessoal"}, headers=headers
    )
    assert res.status_code == 201
    assert res.json()["nome"] == "n" * 100


async def test_0040_AC_4_primeiro_acesso_pendente(api_harness: _ApiTestHarness) -> None:
    headers = await _usuario_pronto(api_harness, concluir=False)
    res = await api_harness.client.post(
        "/v1/espacos", json={"nome": "Neo", "tipo": "trabalho"}, headers=headers
    )
    assert res.status_code == 409
    assert res.json()["erro"] == "primeiro_acesso_pendente"
    assert await _espacos(api_harness, headers) == []


async def test_0040_AC_4_sem_token_recusa(api_harness: _ApiTestHarness) -> None:
    res = await api_harness.client.post("/v1/espacos", json={"nome": "Neo", "tipo": "trabalho"})
    assert res.status_code == 401
    assert res.json()["erro"] == "token_invalido"


async def test_0040_AC_5_me_devolve_meta_e_agentes(api_harness: _ApiTestHarness) -> None:
    headers = await _usuario_pronto(api_harness)
    espaco = (await _espacos(api_harness, headers))[0]
    assert espaco["meta_semanal"] == 30
    assert espaco["agentes_sugeridos"] is False
    assert {"id", "nome", "tipo", "criado_em"} <= set(espaco)


async def test_0040_AC_6_primeiro_acesso_aceita_nome_ate_100(
    api_harness: _ApiTestHarness,
) -> None:
    await api_harness.repo_lista.adicionar(Email("thalyson@gmail.com"))
    headers = api_harness.headers(api_harness.assinar())

    longo = await api_harness.client.post(
        "/v1/primeiro-acesso",
        json={"nome_exibicao": "Ana", "espaco": {"nome": "p" * 101, "tipo": "estudos"}},
        headers=headers,
    )
    assert longo.status_code == 422
    assert longo.json()["campo"] == "espaco.nome"

    res = await api_harness.client.post(
        "/v1/primeiro-acesso",
        json={"nome_exibicao": "Ana", "espaco": {"nome": "p" * 41, "tipo": "estudos"}},
        headers=headers,
    )
    assert res.status_code == 201
    espaco = res.json()["espacos"][0]
    assert espaco["nome"] == "p" * 41
    assert espaco["meta_semanal"] == 10
    assert espaco["agentes_sugeridos"] is False
