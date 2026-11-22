"""Entidades e raiz de agregado do bounded context Identidade."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from neo.domain.identidade.errors import (
    PrimeiroAcessoJaConcluidoError,
    PrimeiroAcessoPendenteError,
)
from neo.domain.identidade.value_objects import (
    Email,
    IdentidadeExterna,
    MetaSemanal,
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
    meta_semanal: MetaSemanal
    agentes_sugeridos: bool = False


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
            # Invariante 8 (0040): Espaco do Primeiro acesso nasce com a Meta sugerida e sem agentes.
            meta_semanal=MetaSemanal.sugerida(tipo_espaco),
            agentes_sugeridos=False,
        )
        self.nome_exibicao = nome_exibicao
        self.primeiro_acesso_em = ts
        self.espacos.append(espaco)
        return espaco

    def criar_espaco(
        self,
        nome: NomeDoEspaco,
        tipo: TipoEspaco,
        meta_semanal: MetaSemanal | None = None,
        agentes_sugeridos: bool = False,
        agora: datetime | None = None,
    ) -> Espaco:
        """Cria um novo Espaco do Usuario (0040).

        Invariante 6: so cria Espaco quem ja concluiu o Primeiro acesso.
        Invariante 7: sem meta informada, vale a Meta sugerida do tipo.
        """
        if not self.primeiro_acesso_concluido:
            raise PrimeiroAcessoPendenteError()
        espaco = Espaco(
            id=uuid4(),
            usuario_id=self.id,
            nome=nome,
            tipo=tipo,
            criado_em=agora or datetime.now(UTC),
            meta_semanal=meta_semanal or MetaSemanal.sugerida(tipo),
            agentes_sugeridos=agentes_sugeridos,
        )
        self.espacos.append(espaco)
        return espaco
