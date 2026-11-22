"""Entidades e raiz de agregado do bounded context Identidade."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from neo.domain.identidade.errors import PrimeiroAcessoJaConcluidoError
from neo.domain.identidade.value_objects import (
    Email,
    IdentidadeExterna,
    NomeDeExibicao,
    NomeDoEspaco,
    TipoEspaco,
)


@dataclass
class Espaco:
    """Agrupador da vida do Usuario no painel (ex.: trabalho, estudos, hobbies, pessoal)."""

    id: UUID
    usuario_id: UUID
    nome: NomeDoEspaco
    tipo: TipoEspaco
    criado_em: datetime


@dataclass(frozen=True)
class EmailAutorizado:
    """Entrada da Lista de permissao autorizando criacao de Usuario."""

    email: Email
    criado_em: datetime


@dataclass
class Usuario:
    """Raiz de agregado representando uma pessoa registrada no Neo."""

    id: UUID
    identidade: IdentidadeExterna
    email: Email
    nome_exibicao: NomeDeExibicao | None = None
    primeiro_acesso_em: datetime | None = None
    criado_em: datetime = field(default_factory=lambda: datetime.now(UTC))
    espacos: list[Espaco] = field(default_factory=list)

    @property
    def primeiro_acesso_concluido(self) -> bool:
        """Indica se o Usuario ja concluiu o Primeiro acesso."""
        return self.primeiro_acesso_em is not None

    @classmethod
    def registrar(
        cls,
        identidade: IdentidadeExterna,
        email: Email,
        agora: datetime | None = None,
    ) -> Usuario:
        """Cria um novo Usuario com Primeiro acesso pendente."""
        ts = agora or datetime.now(UTC)
        return cls(
            id=uuid4(),
            identidade=identidade,
            email=email,
            nome_exibicao=None,
            primeiro_acesso_em=None,
            criado_em=ts,
            espacos=[],
        )

    def concluir_primeiro_acesso(
        self,
        nome_exibicao: NomeDeExibicao,
        nome_espaco: NomeDoEspaco,
        tipo_espaco: TipoEspaco,
        agora: datetime | None = None,
    ) -> Espaco:
        """Define o nome de exibicao e cria exatamente um Espaco inicial."""
        if self.primeiro_acesso_concluido:
            raise PrimeiroAcessoJaConcluidoError()
        ts = agora or datetime.now(UTC)
        espaco = Espaco(
            id=uuid4(),
            usuario_id=self.id,
            nome=nome_espaco,
            tipo=tipo_espaco,
            criado_em=ts,
        )
        self.nome_exibicao = nome_exibicao
        self.primeiro_acesso_em = ts
        self.espacos.append(espaco)
        return espaco
