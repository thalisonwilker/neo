"""Testes de aceite (E2E) dos comandos `neo api` para Lista de permissao (0037 tarefa 7, AC-10)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import neo.infrastructure.db.models  # noqa: F401
from neo.cli import app
from neo.config import ExitCode
from neo.domain.identidade import Email, IdentidadeExterna, Usuario
from neo.infrastructure.db import (
    Base,
    RepositorioDeUsuariosSQLAlchemy,
    criar_engine,
    criar_session_factory,
)

runner = CliRunner()


async def _preparar_banco(db_url: str) -> None:
    engine = criar_engine(db_url)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


async def _registrar_usuario(db_url: str, clerk_id: str, email: str) -> None:
    engine = criar_engine(db_url)
    try:
        repo = RepositorioDeUsuariosSQLAlchemy(criar_session_factory(engine))
        await repo.criar_ou_obter_existente(
            Usuario.registrar(IdentidadeExterna(clerk_id), Email(email))
        )
    finally:
        await engine.dispose()


async def _buscar_usuario(db_url: str, clerk_id: str) -> Usuario | None:
    engine = criar_engine(db_url)
    try:
        repo = RepositorioDeUsuariosSQLAlchemy(criar_session_factory(engine))
        return await repo.buscar_por_identidade(IdentidadeExterna(clerk_id))
    finally:
        await engine.dispose()


def test_AC_10_cli_lista_de_permissao_permitir_listar_remover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-10: `neo api permitir`, `permissoes` e `remover-permissao` com validacoes e sem afetar Usuarios."""
    db_file = tmp_path / "cli_allowlist.db"
    db_url = f"sqlite+aiosqlite:///{db_file}"
    asyncio.run(_preparar_banco(db_url))
    monkeypatch.setenv("NEO_DATABASE_URL", db_url)

    # Lista vazia inicialmente
    res_vazia = runner.invoke(app, ["api", "permissoes"])
    assert res_vazia.exit_code == int(ExitCode.SUCCESS)
    assert "Nenhum e-mail" in res_vazia.output

    # E-mail invalido sai com USAGE_ERROR (2) e nao grava
    res_invalido = runner.invoke(app, ["api", "permitir", "invalido"])
    assert res_invalido.exit_code == int(ExitCode.USAGE_ERROR)

    # Permitir grava em minusculas; repetir nao duplica e sai com 0
    res_add1 = runner.invoke(app, ["api", "permitir", "Thalyson@Example.COM"])
    assert res_add1.exit_code == int(ExitCode.SUCCESS)
    assert "thalyson@example.com" in res_add1.output

    res_add2 = runner.invoke(app, ["api", "permitir", "thalyson@example.com"])
    assert res_add2.exit_code == int(ExitCode.SUCCESS)
    assert "já estava autorizado" in res_add2.output

    # Listar humano e --json
    res_list = runner.invoke(app, ["api", "permissoes"])
    assert res_list.exit_code == int(ExitCode.SUCCESS)
    assert "thalyson@example.com" in res_list.output

    res_json = runner.invoke(app, ["api", "permissoes", "--json"])
    assert res_json.exit_code == int(ExitCode.SUCCESS)
    itens = json.loads(res_json.output)
    assert len(itens) == 1
    assert itens[0]["email"] == "thalyson@example.com"

    # Usuario existente com o mesmo e-mail
    asyncio.run(_registrar_usuario(db_url, "user_cli_1", "thalyson@example.com"))

    # Remover existente sai com 0 e mantem Usuario intacto
    res_rm = runner.invoke(app, ["api", "remover-permissao", "THALYSON@example.com"])
    assert res_rm.exit_code == int(ExitCode.SUCCESS)
    assert "thalyson@example.com" in res_rm.output

    usuario_restante = asyncio.run(_buscar_usuario(db_url, "user_cli_1"))
    assert usuario_restante is not None
    assert usuario_restante.email == Email("thalyson@example.com")

    # Remover inexistente sai com NOT_FOUND (4)
    res_rm_404 = runner.invoke(app, ["api", "remover-permissao", "thalyson@example.com"])
    assert res_rm_404.exit_code == int(ExitCode.NOT_FOUND)
