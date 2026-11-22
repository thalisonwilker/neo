"""Value objects do bounded context Identidade."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from neo.domain.identidade.errors import DadosInvalidosError, TokenInvalidoError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_MAX_EMAIL_LEN = 254
_MAX_NOME_EXIBICAO = 60
_MAX_NOME_ESPACO = 100
_MIN_META_SEMANAL = 1
_MAX_META_SEMANAL = 168


class TipoEspaco(StrEnum):
    """Tipos fixos de Espaco suportados pelo Neo."""

    TRABALHO = "trabalho"
    ESTUDOS = "estudos"
    HOBBIES = "hobbies"
    PESSOAL = "pessoal"

    @classmethod
    def parse(cls, valor: str) -> TipoEspaco:
        """Valida e converte texto em TipoEspaco apos remover espacos nas pontas."""
        if not isinstance(valor, str):
            raise DadosInvalidosError(
                "Tipo de espaço deve ser trabalho, estudos, hobbies ou pessoal.",
                campo="espaco.tipo",
            )
        limpo = valor.strip()
        try:
            return cls(limpo)
        except ValueError as exc:
            raise DadosInvalidosError(
                "Tipo de espaço inválido. Escolha entre: trabalho, estudos, hobbies ou pessoal.",
                campo="espaco.tipo",
            ) from exc

    @property
    def meta_sugerida(self) -> int:
        """Meta semanal proposta pelo tipo (0040): trabalho 30, estudos 10, hobbies 8, pessoal 8."""
        return _METAS_SUGERIDAS[self]


_METAS_SUGERIDAS: dict[TipoEspaco, int] = {
    TipoEspaco.TRABALHO: 30,
    TipoEspaco.ESTUDOS: 10,
    TipoEspaco.HOBBIES: 8,
    TipoEspaco.PESSOAL: 8,
}


@dataclass(frozen=True)
class Email:
    """E-mail normalizado em minusculas e sem espacos nas pontas."""

    valor: str

    def __post_init__(self) -> None:
        if not isinstance(self.valor, str):
            raise DadosInvalidosError("E-mail inválido.", campo="email")
        normalizado = self.valor.strip().lower()
        if (
            not normalizado
            or len(normalizado) > _MAX_EMAIL_LEN
            or not _EMAIL_RE.fullmatch(normalizado)
        ):
            raise DadosInvalidosError("E-mail inválido.", campo="email")
        object.__setattr__(self, "valor", normalizado)

    def mascarado(self) -> str:
        """Retorna representacao mascarada para logs sem expor o endereco completo."""
        local, dominio = self.valor.split("@", 1)
        return f"{local[0]}***@{dominio}"

    def __str__(self) -> str:
        return self.valor


@dataclass(frozen=True)
class IdentidadeExterna:
    """Identificador unico da conta no Clerk (`clerk_user_id`)."""

    clerk_user_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.clerk_user_id, str):
            raise TokenInvalidoError("Identidade externa ausente.")
        limpo = self.clerk_user_id.strip()
        if not limpo:
            raise TokenInvalidoError("Identidade externa ausente.")
        object.__setattr__(self, "clerk_user_id", limpo)


@dataclass(frozen=True)
class NomeDeExibicao:
    """Nome de exibicao do Usuario (1 a 60 caracteres apos trim)."""

    valor: str

    def __post_init__(self) -> None:
        if not isinstance(self.valor, str):
            raise DadosInvalidosError(
                "Nome de exibição deve ter entre 1 e 60 caracteres.",
                campo="nome_exibicao",
            )
        limpo = self.valor.strip()
        if not limpo or len(limpo) > _MAX_NOME_EXIBICAO:
            raise DadosInvalidosError(
                "Nome de exibição deve ter entre 1 e 60 caracteres.",
                campo="nome_exibicao",
            )
        object.__setattr__(self, "valor", limpo)


@dataclass(frozen=True)
class NomeDoEspaco:
    """Nome do Espaco criado pelo Usuario (1 a 100 caracteres apos trim)."""

    valor: str

    def __post_init__(self) -> None:
        if not isinstance(self.valor, str):
            raise DadosInvalidosError(
                "Nome do espaço deve ter entre 1 e 100 caracteres.",
                campo="espaco.nome",
            )
        limpo = self.valor.strip()
        if not limpo or len(limpo) > _MAX_NOME_ESPACO:
            raise DadosInvalidosError(
                "Nome do espaço deve ter entre 1 e 100 caracteres.",
                campo="espaco.nome",
            )
        object.__setattr__(self, "valor", limpo)


@dataclass(frozen=True)
class MetaSemanal:
    """Horas por semana dedicadas a um Espaco: inteiro de 1 a 168 (0040)."""

    valor: int

    def __post_init__(self) -> None:
        # bool e subclasse de int: True/False nao sao horas validas.
        if (
            isinstance(self.valor, bool)
            or not isinstance(self.valor, int)
            or not _MIN_META_SEMANAL <= self.valor <= _MAX_META_SEMANAL
        ):
            raise DadosInvalidosError(
                "Meta semanal deve ser um número inteiro de horas entre 1 e 168.",
                campo="meta_semanal",
            )

    @classmethod
    def sugerida(cls, tipo: TipoEspaco) -> MetaSemanal:
        """Meta semanal proposta pelo Tipo de espaco."""
        return cls(tipo.meta_sugerida)
