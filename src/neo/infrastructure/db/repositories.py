"""Implementacoes SQLAlchemy das portas de persistencia de Identidade."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from sqlalchemy import CursorResult, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from neo.domain.identidade import (
    Email,
    EmailAutorizado,
    Espaco,
    IdentidadeExterna,
    NomeDeExibicao,
    NomeDoEspaco,
    PrimeiroAcessoJaConcluidoError,
    TipoEspaco,
    Usuario,
)
from neo.infrastructure.db.models import EmailAutorizadoORM, EspacoORM, UsuarioORM


def _garantir_utc(dt: datetime) -> datetime:
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt


def _espaco_para_dominio(orm: EspacoORM) -> Espaco:
    return Espaco(
        id=orm.id,
        usuario_id=orm.usuario_id,
        nome=NomeDoEspaco(orm.nome),
        tipo=TipoEspaco(orm.tipo),
        criado_em=_garantir_utc(orm.criado_em),
    )


def _usuario_para_dominio(orm: UsuarioORM) -> Usuario:
    return Usuario(
        id=orm.id,
        identidade=IdentidadeExterna(orm.clerk_user_id),
        email=Email(orm.email),
        nome_exibicao=(
            NomeDeExibicao(orm.nome_exibicao) if orm.nome_exibicao is not None else None
        ),
        primeiro_acesso_em=(
            _garantir_utc(orm.primeiro_acesso_em) if orm.primeiro_acesso_em is not None else None
        ),
        criado_em=_garantir_utc(orm.criado_em),
        espacos=[_espaco_para_dominio(e) for e in orm.espacos],
    )


class RepositorioDeUsuariosSQLAlchemy:
    """Repositorio de Usuarios persistido em banco relacional via SQLAlchemy async."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def buscar_por_identidade(self, identidade: IdentidadeExterna) -> Usuario | None:
        """Busca Usuario pela identidade externa carregando seus Espacos."""
        async with self._session_factory() as session:
            stmt = (
                select(UsuarioORM)
                .options(selectinload(UsuarioORM.espacos))
                .where(UsuarioORM.clerk_user_id == identidade.clerk_user_id)
            )
            orm = (await session.execute(stmt)).scalar_one_or_none()
            return _usuario_para_dominio(orm) if orm is not None else None

    async def criar_ou_obter_existente(self, usuario: Usuario) -> tuple[Usuario, bool]:
        """Persiste novo Usuario ou devolve o existente em caso de corrida paralela."""
        orm = UsuarioORM(
            id=usuario.id,
            clerk_user_id=usuario.identidade.clerk_user_id,
            email=usuario.email.valor,
            nome_exibicao=usuario.nome_exibicao.valor if usuario.nome_exibicao else None,
            primeiro_acesso_em=usuario.primeiro_acesso_em,
            criado_em=usuario.criado_em,
        )
        try:
            async with self._session_factory() as session, session.begin():
                session.add(orm)
            return usuario, True
        except IntegrityError:
            existente = await self.buscar_por_identidade(usuario.identidade)
            if existente is not None:
                return existente, False
            raise

    async def salvar_primeiro_acesso(self, usuario: Usuario, espaco: Espaco) -> Usuario:
        """Atualiza Usuario e cria o primeiro Espaco em uma unica transacao atomica."""
        if usuario.nome_exibicao is None or usuario.primeiro_acesso_em is None:
            raise ValueError("Usuario precisa estar com primeiro acesso preenchido para salvar.")

        async with self._session_factory() as session, session.begin():
            stmt_update = (
                update(UsuarioORM)
                .where(
                    UsuarioORM.id == usuario.id,
                    UsuarioORM.primeiro_acesso_em.is_(None),
                )
                .values(
                    nome_exibicao=usuario.nome_exibicao.valor,
                    primeiro_acesso_em=usuario.primeiro_acesso_em,
                )
            )
            resultado = cast(CursorResult[Any], await session.execute(stmt_update))
            if (resultado.rowcount or 0) == 0:
                raise PrimeiroAcessoJaConcluidoError()

            session.add(
                EspacoORM(
                    id=espaco.id,
                    usuario_id=usuario.id,
                    nome=espaco.nome.valor,
                    tipo=espaco.tipo.value,
                    criado_em=espaco.criado_em,
                )
            )

        atualizado = await self.buscar_por_identidade(usuario.identidade)
        if atualizado is None:
            raise RuntimeError("Usuario nao encontrado apos gravacao do primeiro acesso.")
        return atualizado


class RepositorioDeListaDePermissaoSQLAlchemy:
    """Repositorio da Lista de permissao persistido em `emails_autorizados`."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def esta_autorizado(self, email: Email) -> bool:
        """Retorna True se o e-mail normalizado consta na Lista de permissao."""
        async with self._session_factory() as session:
            stmt = select(EmailAutorizadoORM.email).where(EmailAutorizadoORM.email == email.valor)
            return (await session.execute(stmt)).scalar_one_or_none() is not None

    async def adicionar(self, email: Email) -> tuple[EmailAutorizado, bool]:
        """Adiciona um e-mail na lista de forma idempotente."""
        agora = datetime.now(UTC)
        orm = EmailAutorizadoORM(email=email.valor, criado_em=agora)
        try:
            async with self._session_factory() as session, session.begin():
                session.add(orm)
            return EmailAutorizado(email=email, criado_em=agora), True
        except IntegrityError:
            async with self._session_factory() as session:
                stmt = select(EmailAutorizadoORM).where(EmailAutorizadoORM.email == email.valor)
                existente = (await session.execute(stmt)).scalar_one()
                return (
                    EmailAutorizado(
                        email=Email(existente.email),
                        criado_em=_garantir_utc(existente.criado_em),
                    ),
                    False,
                )

    async def listar(self) -> list[EmailAutorizado]:
        """Lista todos os e-mails autorizados em ordem alfabetica."""
        async with self._session_factory() as session:
            stmt = select(EmailAutorizadoORM).order_by(EmailAutorizadoORM.email)
            linhas = (await session.execute(stmt)).scalars().all()
            return [
                EmailAutorizado(
                    email=Email(item.email),
                    criado_em=_garantir_utc(item.criado_em),
                )
                for item in linhas
            ]

    async def remover(self, email: Email) -> bool:
        """Remove o e-mail informado; retorna False se nao existir."""
        async with self._session_factory() as session, session.begin():
            stmt = delete(EmailAutorizadoORM).where(EmailAutorizadoORM.email == email.valor)
            resultado = cast(CursorResult[Any], await session.execute(stmt))
            return (resultado.rowcount or 0) > 0
