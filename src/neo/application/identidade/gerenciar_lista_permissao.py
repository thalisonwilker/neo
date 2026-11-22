"""Caso de uso: gerenciar a Lista de permissao de e-mails."""

from __future__ import annotations

from neo.domain.identidade import (
    Email,
    EmailAutorizado,
    EmailAutorizadoNaoEncontradoError,
    RepositorioDeListaDePermissao,
)


class GerenciarListaDePermissao:
    """Adiciona, lista e remove e-mails da Lista de permissao."""

    def __init__(self, lista_permissao: RepositorioDeListaDePermissao) -> None:
        self._lista_permissao = lista_permissao

    async def permitir(self, email_bruto: str) -> tuple[EmailAutorizado, bool]:
        """Normaliza e adiciona um e-mail autorizado (idempotente)."""
        email = Email(email_bruto)
        return await self._lista_permissao.adicionar(email)

    async def listar(self) -> list[EmailAutorizado]:
        """Retorna todos os e-mails na Lista de permissao."""
        return await self._lista_permissao.listar()

    async def remover(self, email_bruto: str) -> Email:
        """Remove um e-mail da Lista de permissao sem afetar Usuarios ja registrados."""
        email = Email(email_bruto)
        removido = await self._lista_permissao.remover(email)
        if not removido:
            raise EmailAutorizadoNaoEncontradoError()
        return email
