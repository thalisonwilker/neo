"""Fabrica de engine async, sessoes e health check do banco."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def criar_engine(database_url: str) -> AsyncEngine:
    """Cria uma AsyncEngine SQLAlchemy para PostgreSQL ou SQLite async."""
    return create_async_engine(database_url, pool_pre_ping=True)


def criar_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Cria uma fabrica de AsyncSession com expire_on_commit=False."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def verificar_conexao_banco(engine: AsyncEngine) -> bool:
    """Executa consulta leve (`SELECT 1`) para checar disponibilidade do banco."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except (SQLAlchemyError, OSError, TimeoutError):
        return False
