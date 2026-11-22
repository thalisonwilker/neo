"""Caso de uso: obter Usuario existente ou cria-lo no primeiro pedido autorizado."""

from __future__ import annotations

import logging

from neo.domain.identidade import (
    AcessoNaoLiberadoError,
    IdentidadeExterna,
    LeitorDeEmailExterno,
    RepositorioDeListaDePermissao,
    RepositorioDeUsuarios,
    Usuario,
)

logger = logging.getLogger("neo.application.identidade")


class ObterOuCriarUsuario:
    """Resolve um Usuario a partir da identidade externa validada pelo token."""

    def __init__(
        self,
        usuarios: RepositorioDeUsuarios,
        lista_permissao: RepositorioDeListaDePermissao,
        leitor_email: LeitorDeEmailExterno,
    ) -> None:
        self._usuarios = usuarios
        self._lista_permissao = lista_permissao
        self._leitor_email = leitor_email

    async def executar(self, identidade: IdentidadeExterna) -> Usuario:
        """Retorna Usuario existente (sem consultar Clerk) ou cria se e-mail estiver autorizado."""
        existente = await self._usuarios.buscar_por_identidade(identidade)
        if existente is not None:
            return existente

        email = await self._leitor_email.obter_email_principal(identidade)
        autorizado = await self._lista_permissao.esta_autorizado(email)
        if not autorizado:
            logger.warning(
                "evento=AcessoRecusado clerk_user_id=%s email=%s",
                identidade.clerk_user_id,
                email.mascarado(),
            )
            raise AcessoNaoLiberadoError()

        novo = Usuario.registrar(identidade=identidade, email=email)
        usuario, criado = await self._usuarios.criar_ou_obter_existente(novo)
        if criado:
            logger.info(
                "evento=UsuarioRegistrado usuario_id=%s email=%s",
                usuario.id,
                email.mascarado(),
            )
        return usuario
