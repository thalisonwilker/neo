"""Caso de uso: concluir o Primeiro acesso definindo Nome de exibicao e primeiro Espaco."""

from __future__ import annotations

import logging

from neo.application.identidade.obter_ou_criar_usuario import ObterOuCriarUsuario
from neo.domain.identidade import (
    IdentidadeExterna,
    NomeDeExibicao,
    NomeDoEspaco,
    PrimeiroAcessoJaConcluidoError,
    RepositorioDeUsuarios,
    TipoEspaco,
    Usuario,
)

logger = logging.getLogger("neo.application.identidade")


class ConcluirPrimeiroAcesso:
    """Conclui o Primeiro acesso e cria o primeiro Espaco na mesma transacao."""

    def __init__(
        self,
        usuarios: RepositorioDeUsuarios,
        obter_ou_criar: ObterOuCriarUsuario,
    ) -> None:
        self._usuarios = usuarios
        self._obter_ou_criar = obter_ou_criar

    async def executar(
        self,
        identidade: IdentidadeExterna,
        nome_exibicao_bruto: str,
        nome_espaco_bruto: str,
        tipo_espaco_bruto: str,
    ) -> Usuario:
        """Valida entrada, conclui Primeiro acesso uma unica vez e persiste Usuario + Espaco."""
        usuario = await self._obter_ou_criar.executar(identidade)
        if usuario.primeiro_acesso_concluido:
            raise PrimeiroAcessoJaConcluidoError()

        nome_exibicao = NomeDeExibicao(nome_exibicao_bruto)
        nome_espaco = NomeDoEspaco(nome_espaco_bruto)
        tipo_espaco = TipoEspaco.parse(tipo_espaco_bruto)

        espaco = usuario.concluir_primeiro_acesso(
            nome_exibicao=nome_exibicao,
            nome_espaco=nome_espaco,
            tipo_espaco=tipo_espaco,
        )
        salvo = await self._usuarios.salvar_primeiro_acesso(usuario, espaco)
        logger.info(
            "evento=PrimeiroAcessoConcluido usuario_id=%s espaco_id=%s",
            salvo.id,
            espaco.id,
        )
        return salvo
