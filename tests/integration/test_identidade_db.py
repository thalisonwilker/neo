"""Testes de integracao da persistencia SQLAlchemy e Alembic (0037 tarefa 4)."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

import neo.infrastructure.db.models  # noqa: F401
from neo.domain.identidade import (
    Email,
    Espaco,
    IdentidadeExterna,
    NomeDeExibicao,
    NomeDoEspaco,
    PrimeiroAcessoJaConcluidoError,
    TipoEspaco,
    Usuario,
)
from neo.infrastructure.db import (
    Base,
    RepositorioDeListaDePermissaoSQLAlchemy,
    RepositorioDeUsuariosSQLAlchemy,
    criar_engine,
    criar_session_factory,
    verificar_conexao_banco,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = PROJECT_ROOT / "alembic.ini"
DEFAULT_PG_TEST_URL = "postgresql+asyncpg://neo:neo@localhost:5432/neo_test"


def _alembic_config() -> Config:
    return Config(str(ALEMBIC_INI))


async def _preparar_schema_sqlite(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(params=["sqlite", "postgres"])
async def db_engine(
    request: pytest.FixtureRequest,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncIterator[tuple[str, AsyncEngine]]:
    """Fornece engine async isolada em SQLite e, quando disponivel, PostgreSQL real."""
    if request.param == "sqlite":
        db_file = tmp_path / "identidade_test.db"
        engine = criar_engine(f"sqlite+aiosqlite:///{db_file}")
        await _preparar_schema_sqlite(engine)
        try:
            yield "sqlite", engine
        finally:
            await engine.dispose()
        return

    pg_url = os.environ.get("NEO_TEST_DATABASE_URL", DEFAULT_PG_TEST_URL)
    engine = criar_engine(pg_url)
    try:
        conectado = await asyncio.wait_for(verificar_conexao_banco(engine), timeout=2.0)
    except TimeoutError:
        conectado = False

    if not conectado:
        await engine.dispose()
        pytest.skip(
            "PostgreSQL indisponivel em localhost:5432 — suba com docker compose up -d postgres"
        )

    monkeypatch.setenv("NEO_DATABASE_URL", pg_url)
    await asyncio.to_thread(command.upgrade, _alembic_config(), "head")
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE espacos, usuarios, emails_autorizados CASCADE"))
    try:
        yield "postgres", engine
    finally:
        await engine.dispose()


def test_AC_1_alembic_upgrade_downgrade_sqlite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-1: migration inicial aplica e reverte tabelas em SQLite via CLI do Alembic."""
    db_file = tmp_path / "alembic_cli.db"
    monkeypatch.setenv("NEO_DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    cfg = _alembic_config()

    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")


async def test_AC_1_verificar_conexao_banco_ok_e_erro(
    db_engine: tuple[str, AsyncEngine],
) -> None:
    """AC-1: health check retorna True com banco no ar e False quando inacessivel."""
    _, engine = db_engine
    assert await verificar_conexao_banco(engine) is True

    engine_quebrada = criar_engine("postgresql+asyncpg://neo:neo@127.0.0.1:1/inexistente")
    try:
        assert await verificar_conexao_banco(engine_quebrada) is False
    finally:
        await engine_quebrada.dispose()


async def test_AC_3_e_AC_5_criar_usuario_e_concorrencia(
    db_engine: tuple[str, AsyncEngine],
) -> None:
    """AC-3 e AC-5: persiste Usuario e resolve corrida paralela sem duplicar."""
    _, engine = db_engine
    session_factory = criar_session_factory(engine)
    repo = RepositorioDeUsuariosSQLAlchemy(session_factory)
    identidade = IdentidadeExterna("user_db_1")

    assert await repo.buscar_por_identidade(identidade) is None

    u1 = Usuario.registrar(identidade, Email("dev@example.com"))
    u2 = Usuario.registrar(identidade, Email("dev@example.com"))

    res1, res2 = await asyncio.gather(
        repo.criar_ou_obter_existente(u1),
        repo.criar_ou_obter_existente(u2),
    )

    criados = [r[1] for r in (res1, res2)]
    assert sorted(criados) == [False, True]
    assert res1[0].id == res2[0].id

    encontrado = await repo.buscar_por_identidade(identidade)
    assert encontrado is not None
    assert encontrado.id == res1[0].id
    assert encontrado.email == Email("dev@example.com")
    assert encontrado.primeiro_acesso_concluido is False


async def test_AC_6_e_AC_8_primeiro_acesso_atomico_rollback_e_bloqueio_repeticao(
    db_engine: tuple[str, AsyncEngine],
) -> None:
    """AC-6 e AC-8: grava Usuario + Espaco atomicamente, reverte em erro e bloqueia repeticao."""
    _, engine = db_engine
    session_factory = criar_session_factory(engine)
    repo = RepositorioDeUsuariosSQLAlchemy(session_factory)

    u1 = Usuario.registrar(IdentidadeExterna("user_ok"), Email("ok@example.com"))
    await repo.criar_ou_obter_existente(u1)
    espaco1 = u1.concluir_primeiro_acesso(
        NomeDeExibicao("Thalyson"),
        NomeDoEspaco("Neo"),
        TipoEspaco.TRABALHO,
    )
    salvo1 = await repo.salvar_primeiro_acesso(u1, espaco1)
    assert salvo1.primeiro_acesso_concluido is True
    assert salvo1.nome_exibicao == NomeDeExibicao("Thalyson")
    assert len(salvo1.espacos) == 1
    assert salvo1.espacos[0].id == espaco1.id

    # AC-8: segunda tentativa no mesmo Usuario falha com PrimeiroAcessoJaConcluidoError
    u1_recarregado = await repo.buscar_por_identidade(IdentidadeExterna("user_ok"))
    assert u1_recarregado is not None
    espaco_extra = EspacoFakeFactory.clonar_para(u1_recarregado)
    with pytest.raises(PrimeiroAcessoJaConcluidoError):
        await repo.salvar_primeiro_acesso(u1_recarregado, espaco_extra)

    # AC-6 (prova de rollback): falha ao inserir Espaco (PK duplicada) reverte o UPDATE de Usuario
    u2 = Usuario.registrar(IdentidadeExterna("user_rb"), Email("rb@example.com"))
    await repo.criar_ou_obter_existente(u2)
    espaco_colisao = u2.concluir_primeiro_acesso(
        NomeDeExibicao("Rollback"),
        NomeDoEspaco("Colisao"),
        TipoEspaco.PESSOAL,
    )
    espaco_colisao.id = espaco1.id

    with pytest.raises(IntegrityError):
        await repo.salvar_primeiro_acesso(u2, espaco_colisao)

    u2_banco = await repo.buscar_por_identidade(IdentidadeExterna("user_rb"))
    assert u2_banco is not None
    assert u2_banco.primeiro_acesso_concluido is False
    assert u2_banco.nome_exibicao is None
    assert u2_banco.espacos == []


async def test_AC_10_lista_de_permissao_crud_nao_afeta_usuarios(
    db_engine: tuple[str, AsyncEngine],
) -> None:
    """AC-10: adicionar idempotente, listar ordenado e remover sem apagar Usuarios existentes."""
    _, engine = db_engine
    session_factory = criar_session_factory(engine)
    repo_lista = RepositorioDeListaDePermissaoSQLAlchemy(session_factory)
    repo_usuarios = RepositorioDeUsuariosSQLAlchemy(session_factory)

    email = Email("Pessoa@Example.com")
    item1, criado1 = await repo_lista.adicionar(email)
    assert criado1 is True
    assert item1.email == Email("pessoa@example.com")

    _, criado2 = await repo_lista.adicionar(email)
    assert criado2 is False
    assert await repo_lista.esta_autorizado(email) is True

    await repo_lista.adicionar(Email("alpha@example.com"))
    listados = await repo_lista.listar()
    assert [i.email.valor for i in listados] == ["alpha@example.com", "pessoa@example.com"]

    usuario = Usuario.registrar(IdentidadeExterna("user_perm"), email)
    await repo_usuarios.criar_ou_obter_existente(usuario)

    assert await repo_lista.remover(email) is True
    assert await repo_lista.remover(email) is False
    assert await repo_lista.esta_autorizado(email) is False

    # AC-5 / AC-10: usuario registrado permanece intacto
    assert await repo_usuarios.buscar_por_identidade(IdentidadeExterna("user_perm")) is not None


class EspacoFakeFactory:
    """Auxiliar local para construir Espaco de teste com o tipo do dominio."""

    @staticmethod
    def clonar_para(usuario: Usuario) -> Espaco:
        return Espaco(
            id=uuid4(),
            usuario_id=usuario.id,
            nome=NomeDoEspaco("Segundo"),
            tipo=TipoEspaco.ESTUDOS,
            criado_em=datetime.now(UTC),
        )
