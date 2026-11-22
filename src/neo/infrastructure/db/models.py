"""Modelos ORM SQLAlchemy do bounded context Identidade."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neo.infrastructure.db.base import Base


class UsuarioORM(Base):
    """Tabela `usuarios` mapeando o agregado Usuario."""

    __tablename__ = "usuarios"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    clerk_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    nome_exibicao: Mapped[str | None] = mapped_column(String(60), nullable=True)
    primeiro_acesso_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    espacos: Mapped[list[EspacoORM]] = relationship(
        back_populates="usuario",
        cascade="all, delete-orphan",
        order_by="EspacoORM.criado_em",
    )


class EspacoORM(Base):
    """Tabela `espacos` mapeando os Espacos pertencentes a um Usuario."""

    __tablename__ = "espacos"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(40), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    usuario: Mapped[UsuarioORM] = relationship(back_populates="espacos")


class EmailAutorizadoORM(Base):
    """Tabela `emails_autorizados` da Lista de permissao."""

    __tablename__ = "emails_autorizados"

    email: Mapped[str] = mapped_column(String(254), primary_key=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
