"""Cria tabelas iniciais de Identidade (usuarios, espacos, emails_autorizados).

Revision ID: 0001_identidade_inicial
Revises:
Create Date: 2026-11-22 15:00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_identidade_inicial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Aplica o schema inicial do contexto Identidade."""
    op.create_table(
        "emails_autorizados",
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("email"),
    )
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("clerk_user_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("nome_exibicao", sa.String(length=60), nullable=True),
        sa.Column("primeiro_acesso_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clerk_user_id", name="uq_usuarios_clerk_user_id"),
    )
    op.create_index("ix_usuarios_clerk_user_id", "usuarios", ["clerk_user_id"], unique=True)
    op.create_table(
        "espacos",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("usuario_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("nome", sa.String(length=40), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_espacos_usuario_id", "espacos", ["usuario_id"], unique=False)


def downgrade() -> None:
    """Reverte o schema inicial do contexto Identidade."""
    op.drop_index("ix_espacos_usuario_id", table_name="espacos")
    op.drop_table("espacos")
    op.drop_index("ix_usuarios_clerk_user_id", table_name="usuarios")
    op.drop_table("usuarios")
    op.drop_table("emails_autorizados")
