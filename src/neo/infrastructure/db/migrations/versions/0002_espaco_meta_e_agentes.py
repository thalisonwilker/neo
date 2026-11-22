"""Espaco ganha meta semanal e agentes sugeridos; nome passa a aceitar 100 caracteres (0040).

Revision ID: 0002_espaco_meta_e_agentes
Revises: 0001_identidade_inicial
Create Date: 2026-11-22 20:00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_espaco_meta_e_agentes"
down_revision: str | Sequence[str] | None = "0001_identidade_inicial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Meta sugerida por Tipo de espaco (domain.md da 0040), usada para preencher os Espacos existentes.
_METAS_SUGERIDAS = {"trabalho": 30, "estudos": 10, "hobbies": 8, "pessoal": 8}


def upgrade() -> None:
    """Amplia o nome, cria e preenche `meta_semanal` e cria `agentes_sugeridos`.

    Usa `batch_alter_table` para funcionar tambem no SQLite dos testes (PostgreSQL altera direto).
    """
    with op.batch_alter_table("espacos") as batch:
        batch.alter_column(
            "nome",
            existing_type=sa.String(length=40),
            type_=sa.String(length=100),
            existing_nullable=False,
        )
        batch.add_column(sa.Column("meta_semanal", sa.SmallInteger(), nullable=True))
        batch.add_column(
            sa.Column("agentes_sugeridos", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    casos = " ".join(f"WHEN '{tipo}' THEN {meta}" for tipo, meta in _METAS_SUGERIDAS.items())
    op.execute(f"UPDATE espacos SET meta_semanal = CASE tipo {casos} ELSE 8 END")

    with op.batch_alter_table("espacos") as batch:
        batch.alter_column("meta_semanal", existing_type=sa.SmallInteger(), nullable=False)
        batch.create_check_constraint(
            "ck_espacos_meta_semanal_faixa", "meta_semanal BETWEEN 1 AND 168"
        )


def downgrade() -> None:
    """Remove as colunas novas e volta o nome a 40 caracteres.

    Falha de forma explicita se algum Espaco tiver nome maior que 40 (nao trunca dado do Usuario).
    """
    longos = (
        op.get_bind()
        .execute(sa.text("SELECT count(*) FROM espacos WHERE length(nome) > 40"))
        .scalar_one()
    )
    if longos:
        raise RuntimeError(
            f"{longos} Espaço(s) com nome maior que 40 caracteres; encurte antes do downgrade."
        )
    with op.batch_alter_table("espacos") as batch:
        batch.drop_constraint("ck_espacos_meta_semanal_faixa", type_="check")
        batch.drop_column("agentes_sugeridos")
        batch.drop_column("meta_semanal")
        batch.alter_column(
            "nome",
            existing_type=sa.String(length=100),
            type_=sa.String(length=40),
            existing_nullable=False,
        )
