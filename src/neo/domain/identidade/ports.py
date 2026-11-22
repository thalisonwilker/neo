"""Portas (interfaces) do bounded context Identidade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from neo.domain.identidade.entities import EmailAutorizado, Espaco, Usuario
from neo.domain.identidade.value_objects import Email, IdentidadeExterna


@dataclass(frozen=True)
class TokenVerificado:
    """Resultado validado da verificacao de um token externo."""

    identidade: IdentidadeExterna


class VerificadorDeToken(Protocol):
    """Porta para validar tokens de sessao emitidos pelo provedor externo."""

    async def verificar(self, token: str) -> TokenVerificado: ...


class LeitorDeEmailExterno(Protocol):
    """Porta para consultar o e-mail principal de uma identidade no provedor externo."""

    async def obter_email_principal(self, identidade: IdentidadeExterna) -> Email: ...


class RepositorioDeUsuarios(Protocol):
    """Porta de persistencia para o agregado Usuario e seus Espacos."""

    async def buscar_por_identidade(self, identidade: IdentidadeExterna) -> Usuario | None: ...

    async def criar_ou_obter_existente(self, usuario: Usuario) -> tuple[Usuario, bool]: ...

    async def salvar_primeiro_acesso(self, usuario: Usuario, espaco: Espaco) -> Usuario: ...

    async def adicionar_espaco(self, espaco: Espaco) -> None: ...


class RepositorioDeListaDePermissao(Protocol):
    """Porta de persistencia da Lista de permissao."""

    async def esta_autorizado(self, email: Email) -> bool: ...

    async def adicionar(self, email: Email) -> tuple[EmailAutorizado, bool]: ...

    async def listar(self) -> list[EmailAutorizado]: ...

    async def remover(self, email: Email) -> bool: ...
